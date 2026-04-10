from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from reportlab.pdfgen import canvas
import json
import datetime
from django.utils import timezone
from django.db.models import Q

from store.models import Cart, CartItem, Product
from .models import Order, OrderItem, Payment
from .serializers import OrderSerializer
from .razorpay_utils import create_razorpay_order, verify_signature
from users.notification_utils import trigger_all_notifications


class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from users.models import Address
        from decimal import Decimal
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.items.all()

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        # 1. Handle Address
        address_id = request.data.get('address_id')
        if not address_id:
            return Response({"error": "Shipping address is required"}, status=400)
        
        address_obj = get_object_or_404(Address, id=address_id, user=request.user.app_user)
        
        # Snapshot for order
        delivery_address_snapshot = {
            "full_name": address_obj.full_name,
            "phone": address_obj.phone_number,
            "line1": address_obj.address_line1,
            "line2": address_obj.address_line2,
            "locality": address_obj.locality,
            "city": address_obj.city,
            "state": address_obj.state,
            "pincode": address_obj.pincode
        }

        # 2. Calculate Pricing
        subtotal = Decimal('0.00')
        for item in cart_items:
            product = item.product
            if product.stock < item.quantity:
                return Response({"error": f"Not enough stock for {product.name}"}, status=400)
            subtotal += Decimal(str(product.price)) * item.quantity

        # Discount: 10% auto discount above 1000
        discount = Decimal('0.00')
        if subtotal > 1000:
            discount = (subtotal * Decimal('0.10')).quantize(Decimal('0.01'))
        
        # Area Discount: Extra 5% for special cities
        SPECIAL_CITIES = ["Mumbai", "Pune", "Bangalore", "Delhi", "Hyderabad", "Chennai", "Kolkata", "Ahmedabad", "Surat", "Pune", "Jaipur", "Lucknow", "Patna"]
        area_discount = Decimal('0.00')
        if address_obj.city in SPECIAL_CITIES:
            area_discount = ((subtotal - discount) * Decimal('0.05')).quantize(Decimal('0.01'))
        
        total_discount = discount + area_discount

        # Shipping: Dynamic
        SELLER_STATE = "Maharashtra" 
        shipping = Decimal('0.00')
        if subtotal < 500:
            shipping = Decimal('40.00') if address_obj.state == SELLER_STATE else Decimal('80.00')

        # Tax Calculation (18% Total)
        tax_rate = Decimal('0.18')
        tax_total = ((subtotal - total_discount) * tax_rate).quantize(Decimal('0.01'))
        
        cgst, sgst, igst = Decimal('0.00'), Decimal('0.00'), Decimal('0.00')
        if address_obj.state.strip().lower() == SELLER_STATE.lower():
            cgst = (tax_total / 2).quantize(Decimal('0.01'))
            sgst = tax_total - cgst
        else:
            igst = tax_total

        total_price = subtotal - total_discount + tax_total + shipping

        # 3. Create Order
        order = Order.objects.create(
            user=request.user, 
            status="Pending", 
            payment_status="Pending",
            subtotal=subtotal,
            discount=discount,
            cgst=cgst,
            sgst=sgst,
            igst=igst,
            shipping=shipping,
            total_price=total_price,
            delivery_address=delivery_address_snapshot,
            tracking_history=[{
                "status": "Pending",
                "time": timezone.now().isoformat(),
                "message": "Order initiated and awaiting payment"
            }]
        )
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # 4. Integrate Razorpay
        razorpay_order = create_razorpay_order(total_price, order.id)
        if not razorpay_order:
            # order.delete() # Optional cleanup
            return Response({"error": "Failed to initiate payment with Razorpay"}, status=500)

        # Create Payment Record
        Payment.objects.create(
            order=order,
            razorpay_order_id=razorpay_order['id'],
            amount=total_price,
            status='Pending'
        )

        return Response({
            "message": "Payment initiated",
            "razorpay_order_id": razorpay_order['id'],
            "order_id": order.id,
            "total": float(total_price),
            "currency": "INR",
            "key": getattr(settings, 'RAZORPAY_KEY_ID', 'rzp_test_placeholder')
        })


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')

        # Verify
        is_valid = verify_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature)
        print(f"💰 Razorpay Verification Result: {is_valid}")
        print(f"OrderId: {razorpay_order_id}, PaymentId: {razorpay_payment_id}")
        
        payment = get_object_or_404(Payment, razorpay_order_id=razorpay_order_id)
        order = payment.order

        if is_valid:
            # Update Payment
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.is_successful = True
            payment.status = "Success"
            payment.save()

            # Update Order
            order.is_paid = True
            order.payment_status = "Success"
            order.status = "Confirmed"
            order.save()

            # Update Inventory
            for item in order.items.all():
                product = item.product
                product.stock -= item.quantity
                product.save()

            # Clear Cart
            cart = Cart.objects.filter(user=order.user).first()
            if cart:
                cart.items.all().delete()

            # Trigger Multi-Channel Notifications
            app_user = getattr(order.user, 'app_user', None)
            if app_user:
                msg = f"Order #{order.id} Confirmed! Total: ₹{order.total_price}. Track your package at Bloom & Buy."
                trigger_all_notifications(
                    user=app_user, 
                    title="Bloom & Buy Order Confirmed! 🎉", 
                    message=msg
                )
            else:
                print(f"⚠️ Warning: No app_user profile for user {order.user.username}. Skipping notifications.")

            return Response({"message": "Payment successful", "order_id": order.id})
        else:
            print(f"❌ Payment verification failed for Order ID: {razorpay_order_id}")
            payment.status = "Failed"
            payment.save()
            order.payment_status = "Failed"
            order.save()
            return Response({"error": "Payment verification failed"}, status=400)


class MyOrdersView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class AdminOrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all().order_by('-created_at')


class SellerOrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return orders where at least one product belongs to this seller
        return Order.objects.filter(items__product__supplier=self.request.user).distinct().order_by('-created_at')


class TrackOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        
        # Ensure user can only track their own orders
        if order.user != request.user and not request.user.is_staff:
            return Response({"error": "Forbidden"}, status=403)

        status_levels = ["Pending", "Confirmed", "Packed", "Shipped", "In Transit", "Out for Delivery", "Delivered"]
        try:
            current_level = status_levels.index(order.status)
        except ValueError:
            current_level = 0

        steps = []
        for i, s in enumerate(status_levels):
            steps.append({
                "name": s,
                "completed": i <= current_level,
                "current": i == current_level
            })

        return Response({
            "orderId": order.id,
            "status": order.status,
            "steps": steps,
            "history": order.tracking_history,
            "tracking_id": order.tracking_id,
            "carrier": order.carrier,
            "estimatedDelivery": order.estimated_delivery
        })


class UpdateOrderStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        
        # Check if Admin or Seller of product
        is_seller = order.items.filter(product__supplier=request.user).exists()
        if not request.user.is_staff and not is_seller:
            return Response({"error": "Permission denied"}, status=403)

        new_status = request.data.get("status")
        tracking_id = request.data.get("tracking_id")
        carrier = request.data.get("carrier")

        if new_status: order.status = new_status
        if tracking_id: order.tracking_id = tracking_id
        if carrier: order.carrier = carrier
        
        # Add to history
        order.tracking_history.append({
            "status": new_status,
            "time": timezone.now().isoformat(),
            "message": request.data.get("message", f"Order moved to {new_status}")
        })
        
        order.save()
        
        # Trigger Notification for update
        app_user = order.user.app_user
        msg = f"Your order #{order.id} status is now: {new_status}."
        trigger_all_notifications(
            user=app_user, 
            title="Order Status Updated", 
            message=msg
        )

        return Response({"message": "Order status updated successfully"})


def generate_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, f"INVOICE - Order #{order.id}")
    
    p.setFont("Helvetica", 12)
    p.drawString(100, 780, f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
    p.drawString(100, 760, f"Customer: {order.user.username}")
    p.drawString(100, 740, f"Email: {order.user.email}")
    p.drawString(100, 720, f"Address: {order.shipping_address}")
    
    p.line(100, 710, 500, 710)
    p.drawString(100, 690, "Product")
    p.drawString(400, 690, "Qty")
    p.drawString(450, 690, "Price")
    
    y = 670
    for item in order.items.all():
        p.drawString(100, y, f"{item.product.name}")
        p.drawString(400, y, f"{item.quantity}")
        p.drawString(450, y, f"₹{item.price}")
        y -= 20
        
    # Final Totals
    p.line(100, y-10, 500, y-10)
    y -= 30
    p.setFont("Helvetica", 10)
    p.drawString(300, y, f"Subtotal:")
    p.drawString(450, y, f"₹{order.subtotal}")
    y-=15
    p.drawString(300, y, f"Discount:")
    p.drawString(450, y, f"-₹{order.discount}")
    y-=15
    if order.igst > 0:
        p.drawString(300, y, f"IGST (18%):")
        p.drawString(450, y, f"₹{order.igst}")
    else:
        p.drawString(300, y, f"CGST (9%):")
        p.drawString(450, y, f"₹{order.cgst}")
        y-=15
        p.drawString(300, y, f"SGST (9%):")
        p.drawString(450, y, f"₹{order.sgst}")
    y-=15
    p.drawString(300, y, f"Shipping:")
    p.drawString(450, y, f"₹{order.shipping}")
    y-=20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(300, y, f"Grand Total:")
    p.drawString(450, y, f"₹{order.total_price}")
    
    y-=40
    p.setFont("Helvetica", 10)
    p.drawString(100, y, f"Payment Method: {getattr(order.payment, 'payment_method', 'Razorpay')}")
    p.drawString(100, y-15, f"Transaction ID: {getattr(order.payment, 'razorpay_payment_id', 'N/A')}")
    p.drawString(100, y-30, f"Order Status: {order.status}")

    p.showPage()
    p.save()
    return response

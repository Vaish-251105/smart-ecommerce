from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from store.models import Cart, CartItem
from .models import Order, OrderItem, Payment
from .serializers import OrderSerializer
from rest_framework.generics import ListAPIView
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
import stripe
from django.conf import settings    

class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        if not cart_items.exists():
            return Response({"error": "Cart is empty"})

        order = Order.objects.create(user=request.user)
        total = 0

        for item in cart.items.all():
            product = item.product

            if product.stock < item.quantity:
                return Response(
                    {"error": f"Not enough stock for {product.name}"},
                    status=400
                )

            product.stock -= item.quantity
            product.save()

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )
            total += item.product.price * item.quantity

        order.total_price = total
        order.save()

        cart.items.all().delete()

        return Response({
            "message": "Order created successfully",
            "order_id": order.id,
            "total": total
        })
    
class MyOrdersView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    

class MakePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)

            if order.is_paid:
                return Response({"error": "Order already paid"}, status=400)

            if order.status == "PAID": 
                return Response({"error": "Order already paid"}, status=400)

            payment = Payment.objects.create(
                order=order,
                payment_method=request.data.get("payment_method"),
                transaction_id="TXN12345",
                amount=order.total_price,
                is_successful=True
            )

            stripe.api_key = settings.STRIPE_SECRET_KEY

            payment_intent = stripe.PaymentIntent.create(
                amount=int(order.total_price * 100),  # Stripe uses paise
                currency="inr",
            )

            order.is_paid = True
            order.status = "PAID"
            order.save()

            return Response({"message": "Payment successful"})
            return Response({
                "client_secret": payment_intent.client_secret
            })

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)


from django.shortcuts import get_object_or_404
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from .models import Order


def generate_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    p = canvas.Canvas(response)

    p.drawString(100, 800, f"Invoice for Order #{order.id}")
    p.drawString(100, 780, f"User: {order.user.username}")
    p.drawString(100, 760, f"Total: ₹{order.total_price}")
    p.drawString(100, 740, f"Status: {order.status}")

    y = 700

    # safer related name handling
    items = order.items.all()

    for item in items:
        p.drawString(100, y, f"{item.product.name} - Qty: {item.quantity}")
        y -= 20

    p.showPage()
    p.save()

    return response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.db.models import Sum, Q
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
import datetime

from users.models import AppUser, Notification, PromotionalMessage, ConsumerProfile
from store.models import Product
from orders.models import Order, Payment, OrderItem
from store.serializers import ProductSerializer
from users.notification_utils import trigger_all_notifications

# --- Summary & Analytics ---
class AdminSummaryView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        total_users = User.objects.count()
        total_products = Product.objects.count()
        total_orders = Order.objects.count()
        total_revenue = Payment.objects.filter(is_successful=True).aggregate(Sum('amount'))['amount__sum'] or 0
        last_7_days = timezone.now() - datetime.timedelta(days=7)
        recent_revenue = Payment.objects.filter(is_successful=True, created_at__gte=last_7_days).values('created_at__date').annotate(revenue=Sum('amount')).order_by('created_at__date')
        top_products = OrderItem.objects.values('product__name').annotate(totalSold=Sum('quantity'), revenue=Sum('price')).order_by('-totalSold')[:5]
        low_stock = Product.objects.filter(stock__lte=10).values('name', 'stock')

        return Response({
            "totalRevenue": total_revenue, "totalOrders": total_orders, "totalUsers": total_users, "totalProducts": total_products,
            "recentRevenue": [{"id": str(r['created_at__date']), "revenue": r['revenue']} for r in recent_revenue],
            "topProducts": [{"id": p['product__name'], "totalSold": p['totalSold'], "revenue": p['revenue']} for p in top_products],
            "lowStock": [{"name": p['name'], "stock": p['stock']} for p in low_stock]
        })

# --- Inventory & Moderation ---
class AdminInventoryView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        queryset = Product.objects.all().order_by('-created_at')
        lowstock = request.query_params.get('lowstock')
        deadstock = request.query_params.get('deadstock')
        if lowstock == 'true': queryset = queryset.filter(stock__lt=10)
        elif deadstock == 'true': queryset = queryset.filter(stock=0)
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        return Response({"products": serializer.data})

class AdminProductOverrideView(APIView):
    permission_classes = [IsAdminUser]
    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product updated successfully"})
        return Response(serializer.errors, status=400)

class AdminProductModerationView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        products = Product.objects.filter(approval_status='pending').order_by('-created_at')
        paginator = Paginator(products, request.query_params.get('limit', 12))
        page_obj = paginator.get_page(request.query_params.get('page', 1))
        serializer = ProductSerializer(page_obj.object_list, many=True, context={'request': request})
        return Response({
            "products": serializer.data,
            "pagination": {"page": page_obj.number, "pages": paginator.num_pages, "total": paginator.count}
        })

class AdminModerateProductView(APIView):
    permission_classes = [IsAdminUser]
    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        status = request.data.get('status') or request.data.get('approvalStatus')
        reason = request.data.get('reason') or request.data.get('rejectionReason', '')
        if status in ['approved', 'rejected']:
            product.approval_status = status
            product.rejection_reason = reason if status == 'rejected' else ''
            product.is_active = (status == 'approved')
            product.save()
            if product.supplier:
                target_user = AppUser.objects.filter(user_auth=product.supplier).first()
                if target_user:
                    trigger_all_notifications(target_user.user_auth, f"Product {status.capitalize()}", f"Your product '{product.name}' was {status}.")
            return Response({"message": f"Product {status} successfully"})
        return Response({"error": "Invalid status"}, status=400)

# --- Order Management ---
class AdminOrderListView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        status = request.query_params.get('status')
        orders = Order.objects.all().order_by('-created_at')
        if status: orders = orders.filter(status=status)
        data = [{
            "_id": str(o.id),
            "user": {"name": o.user.username, "email": o.user.email},
            "totalAmount": float(o.total_price),
            "status": o.status,
            "createdAt": o.created_at
        } for o in orders]
        return Response({"orders": data})

class AdminOrderDetailView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        payment = getattr(order, 'payment', None)
        return Response({
            "_id": str(order.id),
            "user": {"name": order.user.get_full_name() or order.user.username, "email": order.user.email},
            "totalAmount": float(order.total_price),
            "status": order.status,
            "payment_status": order.payment_status,
            "createdAt": order.created_at,
            "is_paid": order.is_paid,
            "transactionId": getattr(payment, 'razorpay_payment_id', 'N/A'),
            "items": [{"productName": i.product.name, "quantity": i.quantity, "price": float(i.price)} for i in order.items.all()]
        })

# --- User & Seller Lists ---
class AdminUserListView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        users = User.objects.all().order_by('-date_joined')
        data = [{
            "id": u.id, "name": u.username, "email": u.email, "createdAt": u.date_joined,
            "totalSpent": float(Order.objects.filter(user=u, is_paid=True).aggregate(Sum('total_price'))['total_price__sum'] or 0)
        } for u in users]
        return Response({"users": data})

class AdminSellerListView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        suppliers = AppUser.objects.filter(role='supplier')
        data = [{
            "id": s.id, "storeName": getattr(getattr(s, 'supplierprofile', None), 'company_name', 'N/A'),
            "phone": s.phone, "isActive": s.is_active, "email": s.email
        } for s in suppliers]
        return Response({"sellers": data})

class AdminUserDetailView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, pk):
        user_auth = get_object_or_404(User, pk=pk)
        app_user = getattr(user_auth, 'app_user', None)
        orders = Order.objects.filter(user=user_auth).order_by('-created_at')
        
        return Response({
            "id": user_auth.id,
            "name": user_auth.get_full_name() or user_auth.username,
            "email": user_auth.email,
            "dateJoined": user_auth.date_joined,
            "orders": [{
                "id": o.id,
                "date": o.created_at,
                "status": o.status,
                "total": float(o.total_price),
                "itemCount": o.items.count()
            } for o in orders]
        })

class AdminSellerDetailView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, pk):
        app_user = get_object_or_404(AppUser, pk=pk)
        profile = getattr(app_user, 'supplierprofile', None)
        products = Product.objects.filter(supplier=app_user.user_auth)
        
        # Calculate some stats for the seller if needed, for now just recent orders
        orders = Order.objects.filter(items__product__supplier=app_user.user_auth).distinct().order_by('-created_at')[:10]
        
        return Response({
            "id": app_user.id,
            "name": app_user.username,
            "email": app_user.email,
            "storeName": profile.company_name if profile else "N/A",
            "storeLogo": profile.logo.url if profile and profile.logo else None,
            "products": ProductSerializer(products, many=True, context={'request': request}).data,
            "salesHistory": [{
                "orderId": o.id,
                "productName": i.product.name,
                "quantity": i.quantity,
                "price": float(i.price),
                "status": o.status
            } for o in orders for i in o.items.filter(product__supplier=app_user.user_auth)]
        })

# --- Promotional Notifications ---
class AdminPromotionalView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        title = request.data.get('title')
        content = request.data.get('content')
        target_role = request.data.get('target_role', 'consumer')
        channels = request.data.get('channels', ['Email'])
        promo = PromotionalMessage.objects.create(title=title, content=content, target_role=target_role, send_via=",".join(channels))
        targets = AppUser.objects.filter(role=target_role)
        sent_count = 0
        for target in targets:
            if target.role == 'consumer':
                try:
                    if not target.consumerprofile.is_opted_in: continue
                except: pass
            trigger_all_notifications(target, title, content, channels=channels)
            sent_count += 1
        promo.sent_at = timezone.now()
        promo.save()
        return Response({"message": f"Promotion sent to {sent_count} users successfully"})

class AdminSendNotificationView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        user_id = request.data.get('userId')
        title = request.data.get('title')
        message = request.data.get('message')
        channels = request.data.get('channels', ['In-App'])
        try:
            user = AppUser.objects.get(Q(pk=user_id) | Q(user_auth_id=user_id))
            # FIX: Trigger with AppUser object 'user', which has email and phone
            trigger_all_notifications(user, title, message, channels=channels)
            return Response({"message": "Notification sent successfully"})
        except Exception as e:
            return Response({"error": str(e)}, status=404)

# --- Notifications ---
class AdminNotificationView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        app_user = AppUser.objects.filter(user_auth=request.user).first()
        if not app_user: return Response([])
        notifications = Notification.objects.filter(user=app_user, type='In-App').order_by('-created_at')[:20]
        data = [{
            "id": n.id, "title": n.title, "message": n.message, "isRead": n.is_read, "createdAt": n.created_at
        } for n in notifications]
        return Response(data)

class AdminNotificationMarkReadView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request, pk):
        note = get_object_or_404(Notification, id=pk)
        note.is_read = True
        note.save()
        return Response({"message": "Marked as read"})
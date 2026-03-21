from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser

from users.models import AppUser
from store.models import Product
from orders.models import Order, Payment, OrderItem
from django.db.models import Sum


class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):

        total_users = AppUser.objects.count()
        total_products = Product.objects.count()
        total_orders = Order.objects.count()

        paid_orders = Order.objects.filter(is_paid=True).count()
        pending_orders = Order.objects.filter(is_paid=False).count()

        total_payments = Payment.objects.count()

        total_revenue = Payment.objects.filter(
            is_successful=True
        ).aggregate(Sum('amount'))['amount__sum'] or 0

        data = {
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "paid_orders": paid_orders,
            "pending_orders": pending_orders,
            "total_payments": total_payments,
            "total_revenue": total_revenue
        }

        return Response(data)


# ✅ LOW STOCK PRODUCTS
@api_view(['GET'])
def low_stock_products(request):
    products = Product.objects.filter(stock__lt=5)

    data = []

    for p in products:
        data.append({
            "product_id": p.id,
            "name": p.name,
            "stock": p.stock
        })

    return Response(data)


# ✅ TOP SELLING PRODUCTS
@api_view(['GET'])
def top_selling_products(request):

    products = (
        OrderItem.objects
        .values('product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )

    return Response(products)
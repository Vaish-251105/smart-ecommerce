from rest_framework.decorators import api_view
from rest_framework.response import Response
from orders.models import OrderItem
from store.models import Product

@api_view(['GET'])
def recommend_products(request, user_id):

    orders = OrderItem.objects.filter(order__user_id=user_id)

    product_ids = orders.values_list('product_id', flat=True)

    recommended = Product.objects.exclude(id__in=product_ids)[:5]

    data = []

    for p in recommended:
        data.append({
            "id": p.id,
            "name": p.name,
            "price": p.price
        })

    return Response({
        "recommended_products": data
    })
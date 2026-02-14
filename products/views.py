from rest_framework.generics import ListCreateAPIView
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Cart, CartItem, Product

class ProductListAPI(ListCreateAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer

class CategoryListCreateApi(ListCreateAPIView):
    queryset = Category.objects.filter(is_active=True)  
    serializer_class = CategorySerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    user = request.user
    product_id = request.data.get("product_id")
    quantity = int(request.data.get("quantity", 1))

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    cart, created = Cart.objects.get_or_create(user=user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()

    return Response({"message": "Product added to cart"})
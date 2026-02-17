from django.shortcuts import render
from rest_framework.response import Response

# Create your views here.
from rest_framework.generics import ListCreateAPIView
from .models import Product, Category, Cart, CartItem
from .serializers import ProductSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

class ProductListAPIView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


from rest_framework.generics import RetrieveUpdateDestroyAPIView

class ProductDetailApi(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    user = request.user
    product_id = request.data.get("product_id")
    quantity = request.data.get("quantity", 1)
    
    try:
        quantity = int(quantity)
    except ValueError:
        return Response({"error": "Invalid quantity"}, status=400)


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
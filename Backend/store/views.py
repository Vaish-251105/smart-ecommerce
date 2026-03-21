from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView , RetrieveUpdateDestroyAPIView
from .models import Product, Category, Cart, CartItem
from .serializers import ProductSerializer , CategorySerializer, CartSerializer, CartItemSerializer
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView


# Create your views here.
class ProductListAPIView(ListCreateAPIView):
 queryset = Product.objects.all()
 serializer_class = ProductSerializer
 permission_classes = [IsAuthenticatedOrReadOnly]

 filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

 filterset_fields = ['category']
 search_fields = ['name', 'description']
 ordering_fields = ['price', 'created_at']

def get_queryset(self):
    queryset = Product.objects.all()

    category = self.request.query_params.get('category')
    search = self.request.query_params.get('search')

    if category:
        queryset = queryset.filter(category__iexact=category)

    if search:
        queryset = queryset.filter(name__icontains=search)

    return queryset

class ProductDetailApi(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class RecentProductsAPIView(APIView):

    def get(self, request):
        products = Product.objects.order_by("-id")[:5]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

class CategoryListCreateAPIView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CartAPIView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


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

    if not product_id:
        return Response({"error": "Product ID is required"}, status=400)

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


class CheckoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.get(user=request.user)

        order = Order.objects.create(user=request.user)

        total = 0

        for item in cart.items.all():
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

        return Response({"message": "Order created successfully"})

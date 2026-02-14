from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListCreateAPIView
from .models import Product
from .serializers import ProductSerializer

class ProductListAPIView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


from rest_framework.generics import RetrieveUpdateDestroyAPIView

class ProductDetailApi(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

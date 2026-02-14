from django.urls import path
from .views import ProductListAPIView, ProductDetailApi

urlpatterns = [
    path('products/', ProductListAPIView.as_view()),
    path('products/<int:pk>/', ProductDetailApi.as_view(), name='product-detail'),
]

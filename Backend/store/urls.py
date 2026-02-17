from django.urls import path
from .views import ProductListAPIView, ProductDetailApi, add_to_cart

urlpatterns = [
    path('products/', ProductListAPIView.as_view()),
    path('products/<int:pk>/', ProductDetailApi.as_view(), name='product-detail'),
    path('add-to-cart/', add_to_cart, name='add-to-cart'),
]

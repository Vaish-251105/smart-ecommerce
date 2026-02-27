from django.urls import path
from .views import CategoryDetailAPIView, CategoryListCreateAPIView, CheckoutAPIView, ProductDetailApi, ProductListAPIView, CategoryListCreateAPIView, ProductListAPIView, ProductDetailApi, add_to_cart
from .views import CartAPIView

urlpatterns = [
    path('products/', ProductListAPIView.as_view()),
    path('products/<int:pk>/', ProductDetailApi.as_view(), name='product-detail'),
    path('cart/', CartAPIView.as_view()),
    path('add-to-cart/', add_to_cart, name='add-to-cart'),
    path('checkout/', CheckoutAPIView.as_view()),
    path('categories/', CategoryListCreateAPIView.as_view()),
    path('categories/<int:pk>/', CategoryDetailAPIView.as_view()),
    
]

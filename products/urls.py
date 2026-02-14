from django.urls import path
from .views import CategoryListCreateApi, ProductListAPI, add_to_cart

urlpatterns = [
    path('products/', ProductListAPI.as_view(),),
    path('categories/', CategoryListCreateApi.as_view(),),
    path('add-to-cart/', add_to_cart, name='add-to-cart'),
]

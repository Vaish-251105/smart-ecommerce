from django.urls import path
from .views import recommend_products

urlpatterns = [
    path('recommendations/<int:user_id>/', recommend_products)
]
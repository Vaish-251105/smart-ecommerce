from django.urls import path
from .views import AdminDashboardView
from adminpanel.views import low_stock_products, top_selling_products
from . import views

urlpatterns = [
    path("dashboard/", AdminDashboardView.as_view()),
    path('low-stock/', views.low_stock_products),
    path('top-products/', views.top_selling_products),
]
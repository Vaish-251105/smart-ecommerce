from django.urls import path
from .views import RegisterView, AddressListCreateView, AddressDetailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('addresses/', AddressListCreateView.as_view(), name='address-list'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address-detail'),
]

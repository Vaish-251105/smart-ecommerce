from django.urls import path
from .views import CheckoutAPIView, MakePaymentView, MyOrdersView, generate_invoice

urlpatterns = [
    path('checkout/', CheckoutAPIView.as_view()),
    path('my-orders/', MyOrdersView.as_view()),
    path("pay/<int:order_id>/", MakePaymentView.as_view()),
    path("invoice/<int:order_id>/", generate_invoice),
]

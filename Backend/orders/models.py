from django.db import models
from users.models import ConsumerProfile
from store.models import Product
# Create your models here.

class Order(models.Model):
    consumer = models.ForeignKey(ConsumerProfile, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20)
    payment_status = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100)
    paid_at = models.DateTimeField(auto_now_add=True)



from django.db import models

from users.models import SupplierProfile
from django.contrib.auth.models import User
# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.category_name

class Product(models.Model):
    supplier = models.ForeignKey(SupplierProfile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=150)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    dynamic_price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class InventoryLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    stock_in = models.IntegerField(default=0)
    stock_out = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Cart"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.product.price * self.quantity
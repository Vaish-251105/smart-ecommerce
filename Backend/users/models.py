from django.db import models

class AppUser(models.Model):
    ROLE_CHOICES = [
        ('admin','Admin'),
        ('supplier','Supplier'),
        ('consumer','Consumer')
    ]

    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class SupplierProfile(models.Model):
    user = models.OneToOneField(AppUser, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=150)
    gst_number = models.CharField(max_length=50)
    address = models.TextField()
    rating = models.FloatField(default=0)
    verified = models.BooleanField(default=False)


class ConsumerProfile(models.Model):
    user = models.OneToOneField(AppUser, on_delete=models.CASCADE)
    address = models.TextField()
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

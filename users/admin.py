from django.contrib import admin

# Register your models here.
from .models import AppUser, SupplierProfile, ConsumerProfile

admin.site.register(AppUser)
admin.site.register(SupplierProfile)
admin.site.register(ConsumerProfile)

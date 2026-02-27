# store/admin.py

from django.contrib import admin

from accounts.models import Membership

from .models import Category, Category, Product

admin.site.register(Product)
admin.site.register(Category)


    
admin.site.register(Membership)

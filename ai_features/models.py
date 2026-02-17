from django.db import models
from store.models import Product
from users.models import AppUser
from django.conf import settings


# Create your models here.
class UserActivity(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=30)
    timestamp = models.DateTimeField(auto_now_add=True)


class ProductAIScore(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    demand_score = models.FloatField()
    trust_score = models.FloatField()
    final_ai_score = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)


class MembershipAIRecommendation(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    recommended_plan = models.CharField(max_length=20)
    confidence_score = models.FloatField()
    generated_at = models.DateTimeField(auto_now_add=True)


class ChatbotLog(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    query = models.TextField()
    intent = models.CharField(max_length=50)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

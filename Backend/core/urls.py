from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Users / Accounts
    path('api/users/', include('accounts.urls')),

    # Store
    path('api/', include('store.urls')),

    # Orders
    path('api/orders/', include('orders.urls')),

    # JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Admin Panel
    path('api/admin/', include('adminpanel.urls')),

    # AI Features
    path('api/ai/', include('ai_features.urls')),
]

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Users / Accounts
    path('api/users/', include('accounts.urls')),   # or 'users.urls' if your app name is users

    # Products
    path('api/', include('products.urls')),

    # Store / Cart (if you have it)
    path('api/store/', include('store.urls')),

    # JWT Token
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

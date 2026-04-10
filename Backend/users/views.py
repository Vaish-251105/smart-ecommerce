from rest_framework import generics, permissions
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, AddressSerializer
from .models import Address, AppUser

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class AddressListCreateView(generics.ListCreateAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user.app_user)

    def perform_create(self, serializer):
        # Ensure we link to AppUser correctly
        app_user = self.request.user.app_user
        serializer.save(user=app_user)

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user.app_user)

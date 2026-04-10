from django.shortcuts import render
from rest_framework import generics
from django.contrib.auth.models import User
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import RegisterSerializer, CustomTokenObtainPairSerializer, UserSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens for the new user
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'token': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=201)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        # Check if seller profile exists (simplified for now)
        data = {
            "user": serializer.data
        }
        return Response(data)

    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully", "user": serializer.data})
        return Response(serializer.errors, status=400)

class GoogleLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        name = request.data.get('name', 'Google User')
        if not email:
            return Response({'error': 'Email is required from Google'}, status=400)
        
        # 1. Get or Create the Auth User
        user, created = User.objects.get_or_create(
            username=email, 
            defaults={'email': email, 'first_name': name.split()[0]}
        )
        if created:
            user.set_unusable_password()
            user.save()
            
        # 2. Get or Create the AppUser (users app)
        from users.models import AppUser, ConsumerProfile, SupplierProfile
        app_user = AppUser.objects.filter(email=email).first()
        
        if not app_user:
            # Create new AppUser if email doesn't exist at all
            app_user = AppUser.objects.create(
                user_auth=user,
                username=email,
                email=email,
                role='consumer',
                phone=''
            )
        elif not app_user.user_auth:
            # Link existing AppUser to this auth user if not linked
            app_user.user_auth = user
            app_user.save()
            
        # 3. Ensure appropriate profile exists
        if app_user.role == 'supplier':
            SupplierProfile.objects.get_or_create(user=app_user)
        else:
            ConsumerProfile.objects.get_or_create(user=app_user)
            
        # 4. Sync UserProfile (accounts app fallback)
        from .models import UserProfile
        UserProfile.objects.get_or_create(
            user=user, 
            defaults={
                'role': 'seller' if app_user.role == 'supplier' else 'customer', 
                'name': name
            }
        )

        # 5. Generate tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'token': str(refresh.access_token),
            'user': UserSerializer(user).data
        })

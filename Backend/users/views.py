import os
from twilio.rest import Client
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification, AppUser, PromotionalMessage, Address
from .serializers import AddressSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import status

# Twilio Setup
TWILIO_ACCOUNT_SID = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
TWILIO_AUTH_TOKEN = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
TWILIO_PHONE_NUMBER = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
TWILIO_WHATSAPP_NUMBER = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)


def get_or_create_app_user(auth_user):
    from users.models import AppUser, ConsumerProfile
    app_user = getattr(auth_user, 'app_user', None)
    if app_user:
        return app_user

    app_user = AppUser.objects.filter(user_auth=auth_user).first()
    if app_user:
        return app_user

    if auth_user.email:
        app_user = AppUser.objects.filter(email=auth_user.email).first()
        if app_user:
            app_user.user_auth = auth_user
            app_user.save()
            return app_user

    app_user = AppUser.objects.create(
        user_auth=auth_user,
        username=auth_user.username or auth_user.email or 'user',
        email=auth_user.email or '',
        role='consumer',
        phone=''
    )
    ConsumerProfile.objects.get_or_create(user=app_user)
    return app_user

def send_web_notification(user, title, message):
    Notification.objects.create(
        user=user,
        type='In-App',
        title=title,
        message=message
    )

def send_email_notification(to_email, subject, message):
    if not to_email:
        return False
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email], fail_silently=False)
        return True
    except Exception as e:
        print(f"📧 Email Failed: {e}")
        return False

def send_sms_notification(to_phone, message):
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]) or not to_phone:
        print("📱 Twilio SMS error: Missing credentials or phone.")
        return False
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(body=message, from_=TWILIO_PHONE_NUMBER, to=to_phone)
        return True
    except Exception as e:
        print(f"📱 SMS Failed: {e}")
        return False

def send_whatsapp_notification(to_phone, message):
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER]) or not to_phone:
        print("🟢 Twilio WhatsApp error: Missing credentials or phone.")
        return False
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        formatted_to = to_phone if to_phone.startswith('whatsapp:') else f'whatsapp:{to_phone}'
        client.messages.create(body=message, from_=TWILIO_WHATSAPP_NUMBER, to=formatted_to)
        return True
    except Exception as e:
        print(f"🟢 WhatsApp Failed: {e}")
        return False

def trigger_all_notifications(user, title, message, channels=None):
    from django.contrib.auth.models import User

    if channels is None:
        channels = ['In-App', 'Email', 'SMS', 'WhatsApp']

    app_user = None
    auth_user = None

    if isinstance(user, User):
        auth_user = user
        app_user = getattr(user, 'app_user', None)
    elif isinstance(user, AppUser):
        app_user = user
        auth_user = user.user_auth

    results = {}
    
    if app_user and 'In-App' in channels:
        send_web_notification(app_user, title, message)
        results['In-App'] = 'Sent'

    email = auth_user.email if auth_user else (app_user.email if app_user else None)
    if 'Email' in channels and email:
        results['Email'] = 'Sent' if send_email_notification(email, title, message) else 'Failed'
        
    phone = app_user.phone if app_user else None
    if phone:
        if 'SMS' in channels:
            results['SMS'] = 'Sent' if send_sms_notification(phone, message) else 'Failed'
        if 'WhatsApp' in channels:
            results['WhatsApp'] = 'Sent' if send_whatsapp_notification(phone, message) else 'Failed'
            
    return results


class UserAddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        app_user = get_or_create_app_user(request.user)
        addresses = Address.objects.filter(user=app_user).order_by('-is_default', '-created_at')
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request):
        app_user = get_or_create_app_user(request.user)
        data = request.data.copy()
        data['user'] = app_user.id
        serializer = AddressSerializer(data=data)
        if serializer.is_valid():
            if data.get('is_default'):
                Address.objects.filter(user=app_user).update(is_default=False)
            address = serializer.save(user=app_user)
            return Response(AddressSerializer(address).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        app_user = get_or_create_app_user(request.user)
        try:
            address = Address.objects.get(pk=pk, user=app_user)
        except Address.DoesNotExist:
            return Response({'detail': 'Address not found.'}, status=status.HTTP_404_NOT_FOUND)

        address.delete()
        return Response({'message': 'Address deleted'}, status=status.HTTP_204_NO_CONTENT)


class UserNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        app_user = get_or_create_app_user(request.user)
        notifications = Notification.objects.filter(user=app_user).order_by('-created_at')[:20]
        data = [
            {
                'id': note.id,
                'type': note.type,
                'title': note.title,
                'message': note.message,
                'is_read': note.is_read,
                'status': note.status,
                'createdAt': note.created_at,
            }
            for note in notifications
        ]
        return Response(data)


class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        app_user = get_or_create_app_user(request.user)
        try:
            notification = Notification.objects.get(pk=pk, user=app_user)
        except Notification.DoesNotExist:
            return Response({'detail': 'Notification not found.'}, status=status.HTTP_404_NOT_FOUND)

        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})


class GlobalAnnouncementsView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        announcements = PromotionalMessage.objects.all().order_by('-created_at')[:10]
        data = [
            {
                'id': ann.id,
                'title': ann.title,
                'content': ann.content,
                'targetRole': ann.target_role,
                'sendVia': ann.send_via,
                'createdAt': ann.created_at,
            }
            for ann in announcements
        ]
        return Response(data)

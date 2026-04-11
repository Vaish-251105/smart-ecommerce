import os
from twilio.rest import Client
from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

# Twilio Setup (Using placeholders)
TWILIO_ACCOUNT_SID = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
TWILIO_AUTH_TOKEN = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
TWILIO_PHONE_NUMBER = getattr(settings, 'TWILIO_PHONE_NUMBER', None)
TWILIO_WHATSAPP_NUMBER = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None) # e.g. 'whatsapp:+14155238886'

def send_web_notification(user, title, message):
    """
    Saves an in-app notification to the database.
    """
    Notification.objects.create(
        user=user,
        type='In-App',
        title=title,
        message=message
    )

def send_email_notification(to_email, subject, message):
    """
    Sends an email using Django's SMTP backend.
    """
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [to_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"📧 Email Failed: {e}")
        return False

def send_sms_notification(to_phone, message):
    """
    Sends an SMS via Twilio.
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        print("📱 Twilio SMS credentials missing. Check settings.")
        return False
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone
        )
        return True
    except Exception as e:
        print(f"📱 SMS Failed: {e}")
        return False

def send_whatsapp_notification(to_phone, message):
    """
    Sends a WhatsApp message via Twilio WhatsApp API.
    """
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER]):
        print("🟢 Twilio WhatsApp credentials missing. Check settings.")
        return False

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        # Ensure to_phone starts with whatsapp:
        formatted_to = to_phone if to_phone.startswith('whatsapp:') else f'whatsapp:{to_phone}'
        client.messages.create(
            body=message,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=formatted_to
        )
        return True
    except Exception as e:
        print(f"🟢 WhatsApp Failed: {e}")
        return False

def trigger_all_notifications(user, title, message, channels=['In-App', 'Email', 'SMS', 'WhatsApp']):
    """
    Triggers notifications across multiple channels.
    Accepts either a User (auth) or AppUser object.
    """
    from django.contrib.auth.models import User
    from .models import AppUser

    # Identify AppUser and auth User
    app_user = None
    auth_user = None

    if isinstance(user, User):
        auth_user = user
        app_user = getattr(user, 'app_user', None)
    elif isinstance(user, AppUser):
        app_user = user
        auth_user = user.user_auth

    results = {}
    
    # We MUST have an AppUser for In-App notifications
    if app_user and 'In-App' in channels:
        send_web_notification(app_user, title, message)
        results['In-App'] = 'Sent'
    elif not app_user and 'In-App' in channels:
        print(f"⚠️ Warning: No AppUser found for {user}. Skipping In-App notification.")
        results['In-App'] = 'Skipped'

    # Email can use either object
    email = auth_user.email if auth_user else (app_user.email if app_user else None)
    if 'Email' in channels and email:
        results['Email'] = 'Sent' if send_email_notification(email, title, message) else 'Failed'
        
    # Phone requires AppUser
    phone = app_user.phone if app_user else None
    if phone:
        if 'SMS' in channels:
            results['SMS'] = 'Sent' if send_sms_notification(phone, message) else 'Failed'
        if 'WhatsApp' in channels:
            results['WhatsApp'] = 'Sent' if send_whatsapp_notification(phone, message) else 'Failed'
            
    return results


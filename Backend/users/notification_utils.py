import os
import logging
from twilio.rest import Client
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import Notification
from .email_templates import (
    get_welcome_email, get_order_confirmation_email, 
    get_tracking_update_email, get_promotional_email
)

logger = logging.getLogger(__name__)

# Twilio Setup will be fetched from settings inside functions to ensure real-time updates.


# Local log for debugging (so user can see messages without working SMTP)
LOG_FILE = os.path.join(settings.BASE_DIR, 'notifications.log')

def log_to_file(channel, to, body):
    from datetime import datetime
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.now()}] [{channel}] TO: {to}\n")
            f.write(f"BODY: {body}\n")
            f.write("-" * 50 + "\n")
    except Exception as e:
        logger.error(f"Failed to write to notification log: {e}")

def normalize_phone_number(phone):
    if not phone:
        return None

    value = str(phone).strip()
    if value.startswith('whatsapp:'):
        value = value[len('whatsapp:'):]

    # Remove all non-digits, keep leading '+' if present
    digits = ''.join(ch for ch in value if ch.isdigit())
    has_plus = value.startswith('+')

    if not digits:
        return None

    # Handle India case: if 10 digits and no country code, add +91
    if len(digits) == 10 and not has_plus:
        return f'+91{digits}'
    
    # Handle India case: if 12 digits starting with 91, add +
    if len(digits) == 12 and digits.startswith('91') and not has_plus:
        return f'+{digits}'

    # Otherwise just return digits with +
    if has_plus:
        return f'+{digits}'
    return f'+{digits}'

def send_web_notification(user, title, message):
    """
    Saves an in-app notification to the database.
    """
    from .models import Notification
    return Notification.objects.create(
        user=user,
        type='In-App',
        title=title,
        message=message,
        status='Sent'
    )

def send_email_notification(to_email, subject, message, app_user=None, html_content=None, attachments=None):
    """
    Sends an email using Django's SMTP backend and logs to DB.
    'attachments' should be a list of tuples: (filename, content, mimetype)
    Returns status: 'Sent', 'Skipped', or 'Failed'.
    """
    if not to_email:
        return 'Failed'
    
    status_val = 'Failed'
    
    # Check for placeholder credentials
    if not settings.EMAIL_HOST_USER or 'your-email@gmail.com' in str(settings.EMAIL_HOST_USER):
        log_to_file("EMAIL", to_email, f"Subject: {subject}\n{message}")
        print(f"--- EMAIL LOGGED TO notifications.log ---")
        status_val = 'Skipped'
    else:
        try:
            msg = EmailMultiAlternatives(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [to_email]
            )
            if html_content:
                msg.attach_alternative(html_content, "text/html")
            
            if attachments:
                for filename, content, mimetype in attachments:
                    msg.attach(filename, content, mimetype)
            
            msg.send(fail_silently=False)
            log_to_file("EMAIL", to_email, f"Subject: {subject}\n{message}")
            status_val = 'Sent'
        except Exception as e:
            logger.error(f"Email Failed to {to_email}: {e}")
            log_to_file("EMAIL_ERROR", to_email, str(e))
            status_val = 'Failed'

    if app_user:
        Notification.objects.create(
            user=app_user,
            type='Email',
            title=subject,
            message=message,
            status=status_val
        )
    return status_val

def send_sms_notification(to_phone, message, app_user=None):
    """
    Sends an SMS via Twilio and logs to DB.
    """
    if not to_phone:
        logger.warning("SMS skipped: No phone number provided.")
        return 'Skipped'

    status_val = 'Failed'
    normalized_phone = normalize_phone_number(to_phone)

    # Fetch from settings
    twilio_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    twilio_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    twilio_phone = getattr(settings, 'TWILIO_PHONE_NUMBER', None)

    # Check for placeholder credentials
    is_placeholder = (
        not twilio_sid or 
        not twilio_token or 
        str(twilio_sid).startswith('AC...') or 
        not twilio_phone or 
        str(twilio_phone) == '+1...'
    )


    if is_placeholder:
        log_to_file("SMS_SKIPPED", normalized_phone or to_phone, f"[PLACEHOLDER CREDENTIALS] {message}")
        print(f"--- SMS SKIPPED (Placeholder Credentials) ---")
        status_val = 'Skipped'
    elif not normalized_phone:
        logger.warning(f"SMS failed: Could not normalize phone {to_phone}")
        log_to_file("SMS_ERROR", to_phone, "Failed to normalize phone number.")
        status_val = 'Failed'
    else:
        try:
            client = Client(twilio_sid, twilio_token)
            twilio_msg = client.messages.create(body=message, from_=twilio_phone, to=normalized_phone)
            
            if twilio_msg.error_code:
                error_info = f"Error {twilio_msg.error_code}: {twilio_msg.error_message}"
                log_to_file("SMS_FAILED", normalized_phone, f"{error_info}\nBODY: {message}")
                status_val = 'Sent' # We log it as sent to Twilio, but failed in delivery
            else:
                log_to_file("SMS_SENT", normalized_phone, message)
                status_val = 'Sent'

        except Exception as e:
            err_str = str(e)
            logger.warning(f"SMS Failed to {normalized_phone}: {err_str}")
            # Identify common trial account errors (Twilio Error 21608)
            log_tag = "SMS_EXCEPTION"
            if "21608" in err_str:
                log_tag = "SMS_TRIAL_ERROR"
                print(f"--- SMS FAILED: Recipient {normalized_phone} is not verified (Twilio Trial Account limit) ---")
            
            log_to_file(log_tag, normalized_phone, err_str)
            status_val = 'Failed'

    if app_user:
        Notification.objects.create(
            user=app_user,
            type='SMS',
            title="SMS Notification",
            message=message,
            status=status_val
        )
    return status_val

def send_whatsapp_notification(to_phone, message, app_user=None):
    """
    Sends a WhatsApp message via Twilio and logs to DB.
    """
    if not to_phone:
        logger.warning("WhatsApp skipped: No phone number provided.")
        return 'Skipped'

    status_val = 'Failed'
    normalized_phone = normalize_phone_number(to_phone)

    # Fetch from settings
    twilio_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    twilio_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    twilio_whatsapp = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', None)

    is_placeholder = (
        not twilio_sid or 
        not twilio_token or 
        str(twilio_sid).startswith('AC...') or 
        not twilio_whatsapp or 
        str(twilio_whatsapp).endswith('+1...') # Flexible check
    )


    if is_placeholder:
        log_to_file("WHATSAPP_SKIPPED", normalized_phone or to_phone, f"[PLACEHOLDER CREDENTIALS] {message}")
        print(f"--- WHATSAPP SKIPPED (Placeholder Credentials) ---")
        status_val = 'Skipped'
    elif not normalized_phone:
        logger.warning(f"WhatsApp failed: Could not normalize phone {to_phone}")
        log_to_file("WHATSAPP_ERROR", to_phone, "Failed to normalize phone number.")
        status_val = 'Failed'
    else:
        try:
            client = Client(twilio_sid, twilio_token)
            formatted_to = f'whatsapp:{normalized_phone}'
            formatted_from = twilio_whatsapp
            if not str(formatted_from).startswith('whatsapp:'):
                formatted_from = f'whatsapp:{formatted_from}'
            
            twilio_msg = client.messages.create(body=message, from_=formatted_from, to=formatted_to)

            
            if twilio_msg.error_code:
                error_info = f"Error {twilio_msg.error_code}: {twilio_msg.error_message}"
                log_to_file("WHATSAPP_FAILED", normalized_phone, f"{error_info}\nBODY: {message}")
                status_val = 'Failed'
            else:
                log_to_file("WHATSAPP_SENT", normalized_phone, message)
                status_val = 'Sent'
        except Exception as e:
            err_str = str(e)
            logger.warning(f"WhatsApp Failed to {normalized_phone}: {err_str}")
            
            # Identify common errors
            log_tag = "WHATSAPP_EXCEPTION"
            if "21608" in err_str:
                log_tag = "WHATSAPP_TRIAL_ERROR"
                print(f"--- WHATSAPP FAILED: Recipient {normalized_phone} not verified ---")
            elif "sandbox" in err_str.lower():
                log_tag = "WHATSAPP_SANDBOX_ERROR"
                print(f"--- WHATSAPP FAILED: Sandbox session expired or not joined ---")

            log_to_file(log_tag, normalized_phone, err_str)
            status_val = 'Failed'

    if app_user:
        Notification.objects.create(
            user=app_user,
            type='WhatsApp',
            title="WhatsApp Notification",
            message=message,
            status=status_val
        )
    return status_val

def trigger_all_notifications(user, title, message, channels=['In-App', 'Email', 'SMS', 'WhatsApp'], phone=None, email_attachments=None):
    """
    Triggers notifications across multiple channels.
    'user' can be User or AppUser.
    'email_attachments' should be a list of (filename, content, mimetype)
    """
    from django.contrib.auth.models import User
    from .models import AppUser

    app_user = user if isinstance(user, AppUser) else getattr(user, 'app_user', None)
    auth_user = user if isinstance(user, User) else getattr(user, 'user_auth', None)

    results = {}
    
    if 'In-App' in channels and app_user:
        send_web_notification(app_user, title, message)
        results['In-App'] = 'Sent'

    # Determine Email
    email = None
    if auth_user and auth_user.email:
        email = auth_user.email
    elif app_user and app_user.email:
        email = app_user.email

    if 'Email' in channels:
        if email:
            # Auto-select template based on title or content
            html_content = None
            uname = auth_user.username if auth_user else (app_user.username if app_user else "Subscriber")
            
            if "Welcome" in title or "Subscribed" in title:
                html_content = get_welcome_email(uname)
            elif "Order Confirmed" in title:
                # Try to extract Order ID and Amount from message
                import re
                oid_match = re.search(r'#(\d+)', message)
                price_match = re.search(r'Rs\.(\d+)', message)
                
                oid = oid_match.group(1) if oid_match else "Recent"
                price = price_match.group(1) if price_match else "---"
                html_content = get_order_confirmation_email(oid, price)
            elif "Order Update" in title or "Status" in title:
                html_content = get_tracking_update_email("Update", title, message)
            else:
                html_content = get_promotional_email(title, message)
                
            results['Email'] = send_email_notification(
                email, title, message, 
                app_user=app_user, 
                html_content=html_content,
                attachments=email_attachments
            )
        else:
            results['Email'] = 'Skipped'

    # Determine Phone
    if not phone:
        if app_user and app_user.phone:
            phone = app_user.phone
        elif auth_user and hasattr(auth_user, 'profile') and getattr(auth_user.profile, 'phone', None):
            phone = auth_user.profile.phone

    if 'SMS' in channels:
        print(f"DEBUG: Triggering SMS for {phone}")
        if phone:
            results['SMS'] = send_sms_notification(phone, message, app_user=app_user)
        else:
            results['SMS'] = 'Skipped'

    if 'WhatsApp' in channels:
        if phone:
            results['WhatsApp'] = send_whatsapp_notification(phone, message, app_user=app_user)
        else:
            results['WhatsApp'] = 'Skipped'
            
    return results

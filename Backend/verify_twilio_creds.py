import os
import django
from twilio.rest import Client
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def verify_credentials():
    print("--- Twilio Credential Verifier ---")
    sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    
    if not sid or 'AC...' in str(sid):
        print("[ERROR] SID is placeholder or missing")
        return

    try:
        client = Client(sid, token)
        # Try to list messages (will fail if credentials are bad)
        # We limit to 1 to be fast
        messages = client.messages.list(limit=5)
        print("[SUCCESS] Credentials are valid. Connection successful.")
        for msg in messages:
            print(f"SID: {msg.sid}, Status: {msg.status}, To: {msg.to}")
            if msg.error_code:
                print(f"  Error Code: {msg.error_code}")
                print(f"  Error Message: {msg.error_message}")
    except Exception as e:
        print(f"[FAILED] Twilio Error: {e}")

if __name__ == "__main__":
    verify_credentials()

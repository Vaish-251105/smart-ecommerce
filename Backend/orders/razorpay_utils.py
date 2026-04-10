import razorpay
from django.conf import settings

def get_razorpay_client():
    return razorpay.Client(auth=(
        getattr(settings, 'RAZORPAY_KEY_ID', ''),
        getattr(settings, 'RAZORPAY_KEY_SECRET', '')
    ))

def create_razorpay_order(amount_in_rupees, receipt_id):
    """
    Creates a Razorpay order. Amount should be in paise (amount * 100).
    """
    client = get_razorpay_client()
    data = {
        "amount": int(amount_in_rupees * 100),
        "currency": "INR",
        "receipt": f"receipt_{receipt_id}",
        "payment_capture": 1 # Auto capture
    }
    try:
        order = client.order.create(data=data)
        print(f"✅ Razorpay Order Created: {order['id']} for Amount: {data['amount']} paise")
        return order
    except Exception as e:
        print(f"❌ Razorpay Order Creation Failed: {e}")
        return None

def verify_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    Verifies the payment signature sent by frontend.
    """
    client = get_razorpay_client()
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }
    try:
        client.utility.verify_payment_signature(params_dict)
        print("✅ Razorpay Signature Verified Successfully")
        return True
    except Exception as e:
        print(f"❌ Razorpay Signature Verification Failed: {e}")
        # Print keys used for debugging (masked)
        key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
        print(f"Debug Info - Key ID used: {key_id[:8]}... (masking rest)")
        return False

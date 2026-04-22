import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from django.http import HttpResponse
from django.utils import timezone

def generate_invoice_pdf(order):
    """
    Generates an invoice PDF for the given order.
    Returns the PDF content as bytes.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    p.setFont('Helvetica-Bold', 22)
    p.drawCentredString(width/2, height - 50, "Bloom & Buy")
    
    p.setFont('Helvetica', 12)
    p.drawCentredString(width/2, height - 70, "Your Premium Flower & Gift Boutique")
    p.line(50, height - 80, width - 50, height - 80)

    # Invoice Info
    p.setFont('Helvetica-Bold', 16)
    p.drawString(50, height - 110, f"INVOICE")
    
    p.setFont('Helvetica', 11)
    p.drawString(50, height - 130, f"Order ID: #{order.id}")
    order_date = order.created_at or timezone.now()
    p.drawString(50, height - 145, f"Date: {order_date.strftime('%B %d, %Y %H:%M')}")
    p.drawString(50, height - 160, f"Payment Status: {order.payment_status or 'Paid'}")

    # Shipping Details
    p.setFont('Helvetica-Bold', 12)
    p.drawString(50, height - 190, "Shipping To:")
    p.setFont('Helvetica', 11)
    
    y = height - 210
    address = order.delivery_address or {}
    p.drawString(60, y, f"Customer: {address.get('full_name', order.user.get_full_name() or order.user.username)}")
    y -= 15
    p.drawString(60, y, f"Address: {address.get('line1', '')}")
    y -= 15
    p.drawString(60, y, f"City: {address.get('city', '')}, {address.get('state', '')} - {address.get('pincode', '')}")
    y -= 15
    p.drawString(60, y, f"Phone: {address.get('phone') or address.get('phone_number', 'N/A')}")

    # Table Header
    y -= 40
    p.setFont('Helvetica-Bold', 12)
    p.line(50, y + 15, width - 50, y + 15)
    p.drawString(50, y, "Item Description")
    p.drawString(350, y, "Qty")
    p.drawString(400, y, "Price")
    p.drawString(480, y, "Total")
    p.line(50, y - 5, width - 50, y - 5)

    # Items
    p.setFont('Helvetica', 11)
    y -= 25
    for item in order.items.all():
        p.drawString(50, y, f"{item.product.name}")
        p.drawString(355, y, f"{item.quantity}")
        p.drawString(400, y, f"Rs.{item.price}")
        p.drawString(480, y, f"Rs.{item.quantity * item.price}")
        y -= 20
        if y < 150:
            p.showPage()
            p.setFont('Helvetica', 11)
            y = height - 50

    # Totals
    y -= 20
    p.line(350, y + 15, width - 50, y + 15)
    p.setFont('Helvetica-Bold', 11)
    p.drawString(350, y, "Subtotal:")
    p.drawRightString(width - 50, y, f"Rs.{order.subtotal}")
    
    y -= 20
    p.setFont('Helvetica', 11)
    p.drawString(350, y, "Discount:")
    p.drawRightString(width - 50, y, f"-Rs.{order.discount}")
    
    y -= 15
    p.drawString(350, y, "CGST (9%):")
    p.drawRightString(width - 50, y, f"Rs.{order.cgst}")
    
    y -= 15
    p.drawString(350, y, "SGST (9%):")
    p.drawRightString(width - 50, y, f"Rs.{order.sgst}")

    y -= 15
    p.drawString(350, y, "Shipping:")
    p.drawRightString(width - 50, y, f"Rs.{order.shipping}")
    
    y -= 25
    p.setFont('Helvetica-Bold', 14)
    p.drawString(350, y, "Grand Total:")
    p.drawRightString(width - 50, y, f"Rs.{order.total_price}")
    
    # Footer
    p.setFont('Helvetica-Oblique', 10)
    p.drawCentredString(width/2, 50, "Thank you for shopping with Bloom & Buy!")
    p.drawCentredString(width/2, 35, "This is a computer-generated invoice.")

    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Booking

import logging
from django.core.mail import EmailMessage # Залишаємо для відправки листа

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Booking)
def booking_created_handler(sender, instance, created, **kwargs):
    if not created:
        return

    send_booking_notification(instance)

def send_booking_notification(booking):
    user = booking.user
    subject = f"Booking Confirmation: {booking.item}"
    body_html = f"""
    <h2>Booking Confirmation</h2>
    <p>Hello {user.first_name or user.username},</p>
    <p>Your booking has been confirmed:</p>
    <ul>
        <li><strong>Item:</strong> {booking.item}</li>
        <li><strong>Start:</strong> {booking.start}</li>
        <li><strong>End:</strong> {booking.end}</li>
    </ul>
    <p>Best regards,<br/>52Rent Team</p>
    """

    try:
        email = EmailMessage(
            subject,
            body_html,
            'noreply@yourdomain.com',
            [user.email],
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)

        logger.info(f"Local MailHog email sent for booking #{booking.pk}")
    except Exception as e:
        logger.error(f"Failed to send local email for booking #{booking.pk}: {e}")

from pathlib import Path
from django.conf import settings
from django.core.mail import send_mail
from ..models import AuditLog, NotificationContact


try:
    import africastalking
except Exception:  # pragma: no cover
    africastalking = None


def _log_sms(numbers, message):
    log_file = Path(settings.BASE_DIR) / 'sms_outbox.log'
    with log_file.open('a', encoding='utf-8') as handle:
        for number in numbers:
            handle.write(f"TO: {number}\n{message}\n---\n")


def _send_sms(numbers, message):
    if not numbers:
        return
    if settings.SMS_BACKEND == 'africastalking' and africastalking and settings.AFRICASTALKING_USERNAME and settings.AFRICASTALKING_API_KEY:
        africastalking.initialize(username=settings.AFRICASTALKING_USERNAME, api_key=settings.AFRICASTALKING_API_KEY)
        africastalking.SMS.send(message, numbers, sender_id=getattr(settings, 'SMS_DEFAULT_SENDER', None))
    else:
        _log_sms(numbers, message)


def notify_alert(alert, actor=None):
    contacts = NotificationContact.objects.filter(active=True)
    region_contacts = [c for c in contacts if c.receive_all_regions or not c.region or c.region.lower() == (alert.aoi.region or '').lower()]
    emails = [c.email for c in region_contacts if c.notify_email and c.email]
    numbers = [c.phone_number for c in region_contacts if c.notify_sms and c.phone_number]

    message = (
        f"KWS ALERT\n\n"
        f"{alert.alert_type} detected in {alert.aoi.name}.\n"
        f"Region: {alert.aoi.region}\n"
        f"Coordinates: {alert.latitude}, {alert.longitude}\n"
        f"Area affected: {alert.area_hectares} ha\n"
        f"Confidence: {alert.confidence_score}\n"
        f"Alert URL: /alerts/{alert.pk}/\n"
    )

    if emails:
        send_mail(
            subject=f"Land Surveillance Alert: {alert.aoi.name}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=emails,
            fail_silently=True,
        )
    if numbers:
        _send_sms(numbers, message)

    AuditLog.objects.create(
        action='Alert notifications dispatched',
        user=actor,
        alert=alert,
        details=f'Emails: {len(emails)}, SMS: {len(numbers)}',
    )

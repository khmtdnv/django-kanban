from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import OTP
from .tasks import send_sms


@receiver(post_save, sender=OTP)
def send_otp_sms(sender, instance, created, **kwargs):
    if not created:
        return

    phone_str = str(instance.phone_number)
    code_str = str(instance.code)

    def _send():
        send_sms.delay(phone_str, code_str)  # type: ignore

    transaction.on_commit(_send)

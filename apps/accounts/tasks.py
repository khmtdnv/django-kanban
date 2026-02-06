from celery import shared_task


@shared_task(bind=True, max_retries=5, default_retry_delay=60)
def send_sms(self, phone_number, code):
    print(f"SMS to {phone_number}: Your verification code is {code}")

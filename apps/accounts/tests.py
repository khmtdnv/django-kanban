# import pytest
from django.urls import reverse
from rest_framework import status

from apps.accounts.models import OTP


def test_send_otp_valid_number(api_client, db):
    url = reverse("accounts:send_code")
    data = {"phone_number": "+79931384192"}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK


def test_send_otp_invalid_number(api_client, db):
    url = reverse("accounts:send_code")
    data = {"phone_number": "1234567890"}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_send_otp_invalid_dict(api_client, db):
    url = reverse("accounts:send_code")
    data = {"phone": "+79931384192"}
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_verify_otp(api_client, db):
    send_otp_url = reverse("accounts:send_code")
    send_otp_data = {"phone_number": "+79931384192"}
    send_otp_response = api_client.post(send_otp_url, send_otp_data)
    assert send_otp_response.status_code == status.HTTP_200_OK

    otp_obj = OTP.objects.get(phone_number=send_otp_data["phone_number"])
    url = reverse("accounts:verify_code")
    data = {
        "phone_number": otp_obj.phone_number,
        "code": otp_obj.code,
    }
    response = api_client.post(url, data)
    assert response.status_code == status.HTTP_200_OK

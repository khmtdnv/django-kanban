import secrets
import string
from datetime import timedelta

import phonenumbers
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from common.models import BaseModel


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Номер телефона обязателен")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone_number, password, **extra_fields)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    phone_number = PhoneNumberField(
        db_index=True,
        unique=True,
        verbose_name="Номер телефона",
        help_text=("Номер телефона в формате +71234567890"),
        region="RU",
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    class Meta(BaseModel.Meta):
        abstract = False
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return str(self.phone_number)

    def save(self, *args, **kwargs):
        if self.phone_number:
            phone_number = phonenumbers.parse(str(self.phone_number), "RU")
            self.phone_number = phonenumbers.format_number(
                phone_number, phonenumbers.PhoneNumberFormat.E164
            )

        super().save(*args, **kwargs)


class OTPManager(models.Manager):
    def create_otp(self, phone_number, code_length=6, validity_minutes=5):
        code = "".join(secrets.choice(string.digits) for _ in range(code_length))
        expires_at = timezone.now() + timedelta(minutes=validity_minutes)

        self.filter(phone_number=phone_number, is_used=False).delete()

        return self.get_or_create(
            phone_number=phone_number,
            code=code,
            expires_at=expires_at,
        )

    def get_latest_otp_by_phone(self, phone_number):
        return self.filter(phone_number=phone_number).order_by("-created_at").first()

    def get_valid_otp(self, phone_number, code):
        otp = self.get_latest_otp_by_phone(phone_number)
        if otp and otp.code == code and otp.is_valid():
            return otp
        return None


class OTP(BaseModel):
    phone_number = PhoneNumberField(
        verbose_name="Номер телефона",
        help_text=("Номер телефона в формате 8 (123) 456-78-90"),
    )
    code = models.CharField("Одноразовый код", max_length=6)
    expires_at = models.DateTimeField("Время истечения кода")
    is_used = models.BooleanField("Использовано", default=False)

    objects = OTPManager()

    class Meta(BaseModel.Meta):
        abstract = False
        ordering = ["-created_at"]

    def __str__(self):
        return f"OTP {self.code} для {self.phone_number} (до {self.expires_at})"

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from common.throttling import AppScopedRateThrottle

from .models import OTP
from .serializers import OTPSerializer, PhoneSerializer

User = get_user_model()


class SendOTPView(generics.GenericAPIView):
    serializer_class = PhoneSerializer
    throttle_classes = (AppScopedRateThrottle,)
    throttle_scope = "auth"

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone_number"]
        OTP.objects.create_otp(phone)
        return Response(
            {"detail": f"Код отправлен: {phone}"},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = OTPSerializer
    throttle_classes = (AppScopedRateThrottle,)
    throttle_scope = "auth"

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone_number"]
        code = serializer.validated_data["code"]
        otp = OTP.objects.get_valid_otp(phone, code)
        if not otp:
            raise ValidationError("Невалдиный код или истекло время жизни кода")

        user, created = User.objects.get_or_create(phone_number=phone)

        refresh = RefreshToken.for_user(user)
        otp.is_used = True
        otp.save()
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )

from django.contrib.auth import get_user_model
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

User = get_user_model()


class PhoneSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()


class OTPSerializer(serializers.Serializer):
    phone_number = PhoneNumberField()
    code = serializers.CharField(max_length=6)


class UserSerializer(serializers.ModelSerializer):
    phone_number = PhoneNumberField()

    class Meta:
        model = User
        fields = ("id", "phone_number")

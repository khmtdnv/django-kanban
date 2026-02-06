from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from phonenumber_field.formfields import PhoneNumberField

User = get_user_model()


class PhoneRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["phone_number", "password1", "password2"]


class PhoneLoginForm(AuthenticationForm):
    username = PhoneNumberField()

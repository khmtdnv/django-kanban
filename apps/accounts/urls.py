from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import SendOTPView, VerifyOTPView

app_name = "accounts"


urlpatterns = [
    path("send_code/", SendOTPView.as_view(), name="send_code"),
    path("verify_code/", VerifyOTPView.as_view(), name="verify_code"),
    path("token_refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

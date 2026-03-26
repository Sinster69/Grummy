from django.urls import path
from .views import verify_email, verify_otp

urlpatterns = [
    path("verify/<uidb64>/<token>/", verify_email, name="verify-email"),
    path("verify-otp/", verify_otp, name="verify-otp"),
]

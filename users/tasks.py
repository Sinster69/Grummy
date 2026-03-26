from celery import shared_task
from django.core.mail import send_mail
from django.urls import reverse


@shared_task
def send_signup_email(email):
    send_mail(
        "Welcome",
        "Your account has been created successfully.",
        "noreply@example.com",
        [email],
        fail_silently=False,
    )


@shared_task
def send_login_email(email):
    send_mail(
        "Login Alert",
        "You just logged into your account.",
        "noreply@example.com",
        [email],
        fail_silently=False,
    )


@shared_task
def send_otp_email(email, otp):
    send_mail(
        "Your OTP Code",
        f"Your OTP is: {otp}",
        "noreply@example.com",
        [email],
        fail_silently=False,
    )

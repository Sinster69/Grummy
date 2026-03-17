from celery import shared_task
from django.core.mail import send_mail


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

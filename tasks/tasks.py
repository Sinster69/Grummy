from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_task_email(email, task_title):
    send_mail(
        "New Delivery Task Created",
        f"Task '{task_title}' has been created.",
        "noreply@example.com",
        [email],
        fail_silently=False,
    )

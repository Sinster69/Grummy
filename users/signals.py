from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile
from .tasks import send_signup_email, send_login_email


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, raw=False, **kwargs):
    if created and not raw:
        Profile.objects.get_or_create(user=instance)
        send_signup_email.delay(instance.email)


@receiver(post_save, sender=User)
def save_profile(sender, instance, raw=False, **kwargs):
    if not raw and hasattr(instance, "profile"):
        instance.profile.save()


@receiver(user_logged_in)
def login_email(sender, request, user, **kwargs):
    send_login_email.delay(user.email)

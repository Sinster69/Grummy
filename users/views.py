from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.http import urlsafe_base64_encode
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User

from .forms import UserRegisterForm, OTPForm
from .models import EmailOTP
from .tokens import email_verification_token
from .tasks import send_verification_email, send_otp_email


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            # 👇 CHANGE STARTS HERE
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            # 👆 IMPORTANT

            # Generate token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = email_verification_token.make_token(user)
            domain = get_current_site(request).domain

            # Generate OTP
            otp_obj, created = EmailOTP.objects.get_or_create(user=user)
            otp = otp_obj.generate_otp()
            otp_obj.otp = otp
            otp_obj.save()

            # Send email via Celery
            send_verification_email.delay(user.id, user.email, domain, uid, token)
            send_otp_email.delay(user.email, otp)

            messages.success(
                request,
                "Account created! Please check your email to verify your account.",
            )

            return redirect("login")
            return redirect("verify-otp")

    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})


def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except:

        user = None

    if user and email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse("✅ Email verified successfully! You can now login.")
    else:
        return HttpResponse("❌ Invalid or expired link.")


def verify_otp(request):
    if request.method == "POST":
        form = OTPForm(request.POST)

        if form.is_valid():
            otp_entered = form.cleaned_data["otp"]

            otp_obj = EmailOTP.objects.filter(otp=otp_entered).first()

            if otp_obj:
                user = otp_obj.user
                user.is_active = True
                user.save()

                otp_obj.delete()

                return HttpResponse("✅ Account verified! You can now login.")
            else:
                return HttpResponse("❌ Invalid OTP")

        else:
            form = OTPForm()

        return render(request, "users/verify_otp.html", {"form": form})


@login_required
def profile(request):
    return render(request, "users/profile.html")

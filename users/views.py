from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from .forms import UserRegisterForm, OTPForm
from .models import EmailOTP
from .tasks import send_otp_email


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            otp_obj, created = EmailOTP.objects.get_or_create(user=user)
            otp_obj.generate_otp()

            send_otp_email.delay(user.email, otp_obj.otp)

            return redirect("verify-otp")

    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})


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

                return redirect("login")

            else:
                return HttpResponse("Invalid OTP")

    else:
        form = OTPForm()

    return render(request, "users/verify_otp.html", {"form": form})


@login_required
def profile(request):
    return render(request, "users/profile.html")

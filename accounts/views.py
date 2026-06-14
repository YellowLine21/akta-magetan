import logging
import secrets

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import BadHeaderError, send_mail
from django.shortcuts import redirect, render

from .forms import LoginForm, RegisterForm
from .models import CustomUser

logger = logging.getLogger(__name__)


def landing(request):
    """Halaman utama / landing page."""
    return render(request, "registration/landing.html")


def register_view(request):
    """Halaman registrasi akun baru."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # Generate token verifikasi email
            token = secrets.token_urlsafe(32)
            user.email_token = token
            user.email_verified = False
            user.save()

            # Kirim email verifikasi
            verification_url = request.build_absolute_uri(
                f"/akun/verifikasi-email/{token}/"
            )

            try:
                send_mail(
                    subject="Verifikasi Email — Akta Kelahiran Magetan",
                    message=(
                        f"Halo {user.nama},\n\n"
                        f"Klik link berikut untuk memverifikasi email Anda:\n{verification_url}\n\n"
                        "Link berlaku selama 24 jam.\n\n"
                        "Salam,\nDinas Kependudukan Kabupaten Magetan"
                    ),
                    from_email="weekendworkers.ww@gmail.com",
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    f"Registrasi berhasil! Kami mengirimkan link verifikasi ke {user.email}. "
                    "Silakan cek email Anda (termasuk folder Spam).",
                )

            except BadHeaderError:
                logger.error(
                    "BadHeaderError saat mengirim email verifikasi ke %s", user.email
                )
                messages.warning(
                    request,
                    "Akun berhasil dibuat, tetapi email verifikasi gagal dikirim "
                    "(header email tidak valid). Hubungi administrator.",
                )

            except OSError as exc:
                # Mencakup ConnectionRefusedError, socket.error, dll.
                logger.error(
                    "OSError saat mengirim email verifikasi ke %s: %s",
                    user.email,
                    exc,
                )
                messages.warning(
                    request,
                    "Akun berhasil dibuat, tetapi email verifikasi gagal dikirim "
                    "(tidak dapat terhubung ke server email). "
                    "Coba lagi nanti atau hubungi administrator.",
                )

            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "Gagal mengirim email verifikasi ke %s: %s", user.email, exc
                )
                messages.warning(
                    request,
                    "Akun berhasil dibuat, tetapi email verifikasi gagal dikirim. "
                    "Hubungi administrator jika masalah berlanjut.",
                )

            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


def verify_email(request, token):
    """Verifikasi email pengguna via token."""
    try:
        user = CustomUser.objects.get(email_token=token)
        user.email_verified = True
        user.email_token = None
        user.save()
        messages.success(request, "Email berhasil diverifikasi! Silakan login.")
    except CustomUser.DoesNotExist:
        messages.error(request, "Token verifikasi tidak valid atau sudah kadaluarsa.")
    return redirect("login")


def login_view(request):
    """Halaman login menggunakan NIK dan password."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            nik = form.cleaned_data["nik"]
            password = form.cleaned_data["password"]
            user = authenticate(request, nik=nik, password=password)
            if user is not None:
                if not user.email_verified:
                    messages.warning(
                        request,
                        "Email Anda belum diverifikasi. Cek kotak masuk email Anda.",
                    )
                    return redirect("login")
                login(request, user)
                messages.success(request, f"Selamat datang, {user.nama}!")
                return redirect("permohonan:daftar")
            else:
                messages.error(request, "NIK atau password salah. Silakan coba lagi.")
    else:
        form = LoginForm()

    return render(request, "registration/login.html", {"form": form})


def logout_view(request):
    """Logout pengguna."""
    logout(request)
    messages.info(request, "Anda telah berhasil keluar.")
    return redirect("landing")


@login_required
def dashboard(request):
    """Halaman dashboard setelah login."""
    return render(request, "registration/dashboard.html", {"user": request.user})

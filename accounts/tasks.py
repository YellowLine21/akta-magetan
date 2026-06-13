from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_verification_email(email, nama, verification_url):
    send_mail(
        subject="Verifikasi Email — Akta Kelahiran Magetan",
        message=(
            f"Halo {nama},\n\n"
            f"Klik link berikut untuk memverifikasi email Anda:\n{verification_url}\n\n"
            "Link berlaku selama 24 jam.\n\n"
            "Salam,\nDinas Kependudukan Kabupaten Magetan"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

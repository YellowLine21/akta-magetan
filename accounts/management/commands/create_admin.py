from django.core.management.base import BaseCommand
from accounts.models import CustomUser
import os

class Command(BaseCommand):
    help = 'Create a superuser admin account'

    def handle(self, *args, **options):
        nik = os.environ.get('ADMIN_NIK', '1234567890123456')
        email = os.environ.get('ADMIN_EMAIL', 'admin@magetan.local')
        password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        nama = os.environ.get('ADMIN_NAMA', 'Administrator')
        no_hp = os.environ.get('ADMIN_NO_HP', '081234567890')

        if CustomUser.objects.filter(nik=nik).exists():
            self.stdout.write(self.style.WARNING(f'Admin user with NIK {nik} already exists'))
            return

        user = CustomUser.objects.create_superuser(
            nik=nik,
            password=password,
            email=email,
            nama=nama,
            no_hp=no_hp,
            email_verified=True
        )
        self.stdout.write(self.style.SUCCESS(f'Successfully created admin user: {user.nama} ({user.nik})'))

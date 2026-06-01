import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'akta_magetan.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

nik = os.getenv('SUPERUSER_NIK', '0000000000000000')
email = os.getenv('SUPERUSER_EMAIL', 'admin@example.com')
password = os.getenv('SUPERUSER_PASSWORD', 'admin123')
nama = os.getenv('SUPERUSER_USERNAME', 'Admin')

if not User.objects.filter(nik=nik).exists():
    User.objects.create_superuser(nik=nik, password=password, email=email, nama=nama)
    print(f"Superuser with NIK '{nik}' created successfully!")
else:
    print(f"Superuser with NIK '{nik}' already exists.")

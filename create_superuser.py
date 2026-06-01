import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'akta_magetan.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.getenv('SUPERUSER_USERNAME', 'admin')
email = os.getenv('SUPERUSER_EMAIL', 'admin@example.com')
password = os.getenv('SUPERUSER_PASSWORD', 'admin123')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superuser '{username}' created successfully!")
else:
    print(f"Superuser '{username}' already exists.")

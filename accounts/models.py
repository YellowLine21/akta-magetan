from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, nik, password=None, **extra_fields):
        if not nik:
            raise ValueError("NIK wajib diisi")
        user = self.model(nik=nik, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, nik, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(nik, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nik = models.CharField(max_length=16, unique=True, verbose_name="NIK")
    nama = models.CharField(max_length=150, verbose_name="Nama Lengkap")
    no_hp = models.CharField(max_length=15, verbose_name="Nomor HP")
    email = models.EmailField(unique=True, verbose_name="Email")
    email_verified = models.BooleanField(default=False, verbose_name="Email Terverifikasi")
    email_token = models.CharField(max_length=64, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "nik"
    REQUIRED_FIELDS = ["nama", "email"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Pengguna"
        verbose_name_plural = "Pengguna"

    def __str__(self):
        return f"{self.nama} ({self.nik})"

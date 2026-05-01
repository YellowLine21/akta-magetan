from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ("nik", "nama", "email", "no_hp", "is_staff", "email_verified")
    search_fields = ("nik", "nama", "email")
    ordering      = ("-date_joined",)

    fieldsets = (
        (None,           {"fields": ("nik", "password")}),
        ("Info Pribadi", {"fields": ("nama", "email", "no_hp")}),
        ("Status",       {"fields": ("email_verified", "is_active", "is_staff", "is_superuser")}),
        ("Tanggal",      {"fields": ("date_joined",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields":  ("nik", "nama", "email", "no_hp", "password1", "password2"),
        }),
    )
    readonly_fields = ("date_joined",)
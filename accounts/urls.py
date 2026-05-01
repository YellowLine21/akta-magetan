from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing, name="landing"),
    path("akun/daftar/", views.register_view, name="register"),
    path("akun/masuk/", views.login_view, name="login"),
    path("akun/keluar/", views.logout_view, name="logout"),
    path("akun/verifikasi-email/<str:token>/", views.verify_email, name="verify_email"),
    path("dashboard/", views.dashboard, name="dashboard"),
]

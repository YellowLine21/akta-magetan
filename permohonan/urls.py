from django.urls import path
from . import views

app_name = "permohonan"

urlpatterns = [
    path("",                          views.daftar_permohonan, name="daftar"),
    path("baru/",                     views.langkah_data,      name="langkah_data"),
    path("<uuid:pk>/data/",           views.langkah_data,      name="langkah_data_edit"),
    path("<uuid:pk>/upload/",         views.langkah_upload,    name="langkah_upload"),
    path("<uuid:pk>/review/",         views.langkah_review,    name="langkah_review"),
    path("<uuid:pk>/notifikasi/",     views.notifikasi,        name="notifikasi"),
]

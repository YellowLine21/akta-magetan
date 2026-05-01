from django.urls import path
from .views.admin_views import (
    admin_dashboard,
    admin_daftar,
    admin_detail,
    admin_upload_hasil,
    admin_hapus_hasil,
)

app_name = "admin_custom"

urlpatterns = [
    path("",                              admin_dashboard,     name="dashboard"),
    path("permohonan/",                   admin_daftar,        name="daftar"),
    path("permohonan/<uuid:pk>/",         admin_detail,        name="detail"),
    path("permohonan/<uuid:pk>/upload-hasil/", admin_upload_hasil, name="upload_hasil"),
    path("permohonan/<uuid:pk>/hapus-hasil/",  admin_hapus_hasil,  name="hapus_hasil"),
]
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from .models import Permohonan, Berkas, RiwayatStatus, StatusPermohonan
from .models import HasilAkta

class BerkasInline(admin.TabularInline):
    model        = Berkas
    extra        = 0
    readonly_fields = ("jenis", "nama_file", "file_link", "diunggah_pada")
    fields       = ("jenis", "nama_file", "file_link", "diunggah_pada")
    can_delete   = False

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Lihat File</a>', obj.file.url)
        return "—"
    file_link.short_description = "File"


class RiwayatInline(admin.TabularInline):
    model       = RiwayatStatus
    extra       = 0
    readonly_fields = ("status_lama", "status_baru", "catatan", "diubah_oleh", "dibuat_pada")
    can_delete  = False


@admin.register(Permohonan)
class PermohonanAdmin(admin.ModelAdmin):
    list_display  = (
        "nama_anak", "nik_anak", "pemohon", "status_badge",
        "dibuat_pada", "diajukan_pada", "aksi_ubah_status"
    )
    list_filter   = ("status", "dibuat_pada")
    search_fields = ("nama_anak", "nik_anak", "pemohon__nama", "pemohon__nik")
    readonly_fields = (
        "id", "pemohon", "dibuat_pada", "diperbarui_pada", "diajukan_pada",
    )
    inlines       = [BerkasInline, RiwayatInline]

    fieldsets = (
        ("Informasi Permohonan", {
            "fields": ("id", "pemohon", "status", "dibuat_pada", "diajukan_pada"),
        }),
        ("Data Anak", {
            "fields": ("nama_anak", "nik_anak", "tempat_lahir", "tanggal_lahir", "nomor_akta"),
        }),
        ("Data Ayah", {
            "fields": ("nama_ayah", "nik_ayah", "no_nikah_ayah"),
        }),
        ("Data Ibu", {
            "fields": ("nama_ibu", "nik_ibu", "no_nikah_ibu"),
        }),
        ("Data Pernikahan", {
            "fields": ("tanggal_menikah",),
            "classes": ("collapse",),
        }),
    )

    def status_badge(self, obj):
        warna = {
            StatusPermohonan.DRAFT:        "#6B7280",
            StatusPermohonan.DIAJUKAN:     "#2563EB",
            StatusPermohonan.VERIFIKASI:   "#D97706",
            StatusPermohonan.DIPROSES:     "#7C3AED",
            StatusPermohonan.PERLU_REVISI: "#DC2626",
            StatusPermohonan.SELESAI:      "#059669",
            StatusPermohonan.DITOLAK:      "#991B1B",
        }.get(obj.status, "#6B7280")
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;font-size:12px;">{}</span>',
            warna, obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def aksi_ubah_status(self, obj):
        return format_html(
            '<a href="/admin/permohonan/permohonan/{}/change/" style="font-size:12px;">Ubah Status</a>',
            obj.pk
        )
    aksi_ubah_status.short_description = "Aksi"

    def save_model(self, request, obj, form, change):
        if change:
            old = Permohonan.objects.get(pk=obj.pk)
            if old.status != obj.status:
                RiwayatStatus.objects.create(
                    permohonan  = obj,
                    status_lama = old.status,
                    status_baru = obj.status,
                    diubah_oleh = request.user,
                    catatan     = f"Status diubah oleh admin: {request.user.get_full_name() or request.user.nik}",
                )
        super().save_model(request, obj, form, change)

@admin.register(HasilAkta)
class HasilAktaAdmin(admin.ModelAdmin):
    list_display  = ("permohonan", "nama_file", "diunggah_oleh", "diunggah_pada")
    readonly_fields = ("diunggah_pada", "diunggah_oleh")

    def save_model(self, request, obj, form, change):
        obj.diunggah_oleh = request.user
        super().save_model(request, obj, form, change)
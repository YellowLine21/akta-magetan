from django.db import models
from django.conf import settings
import uuid


class StatusPermohonan(models.TextChoices):
    DRAFT         = "draft",         "Draft"
    DIAJUKAN      = "diajukan",      "Diajukan"
    VERIFIKASI    = "verifikasi",     "Sedang Diverifikasi"
    DIPROSES      = "diproses",      "Sedang Diproses"
    PERLU_REVISI  = "perlu_revisi",  "Perlu Revisi"
    SELESAI       = "selesai",       "Selesai"
    DITOLAK       = "ditolak",       "Ditolak"


class Permohonan(models.Model):
    """Data utama permohonan keabsahan akta kelahiran."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pemohon = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="permohonan",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusPermohonan.choices,
        default=StatusPermohonan.DRAFT,
    )

    # ── DATA ANAK ──────────────────────────────────
    nama_anak          = models.CharField(max_length=150, verbose_name="Nama Lengkap")
    nik_anak           = models.CharField(max_length=16,  verbose_name="NIK Anak")
    tempat_lahir       = models.CharField(max_length=100, verbose_name="Tempat Lahir")
    tanggal_lahir      = models.DateField(verbose_name="Tanggal Lahir")
    nomor_akta         = models.CharField(max_length=50,  verbose_name="Nomor Akta Kelahiran")

    # ── DATA AYAH ──────────────────────────────────
    nama_ayah          = models.CharField(max_length=150, verbose_name="Nama Ayah")
    nik_ayah           = models.CharField(max_length=16,  verbose_name="NIK Ayah")
    no_nikah_ayah      = models.CharField(max_length=50,  blank=True, null=True, verbose_name="No. Buku Nikah Ayah")

    # ── DATA IBU ───────────────────────────────────
    nama_ibu           = models.CharField(max_length=150, verbose_name="Nama Ibu")
    nik_ibu            = models.CharField(max_length=16,  verbose_name="NIK Ibu")
    no_nikah_ibu       = models.CharField(max_length=50,  blank=True, null=True, verbose_name="No. Buku Nikah Ibu")

    # ── DATA PERNIKAHAN (opsional) ─────────────────
    tanggal_menikah    = models.DateField(blank=True, null=True, verbose_name="Tanggal Menikah")

    # ── TIMESTAMPS ────────────────────────────────
    dibuat_pada        = models.DateTimeField(auto_now_add=True)
    diperbarui_pada    = models.DateTimeField(auto_now=True)
    diajukan_pada      = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Permohonan"
        verbose_name_plural = "Permohonan"
        ordering = ["-dibuat_pada"]

    def __str__(self):
        return f"{self.nama_anak} — {self.get_status_display()}"

    def get_progress_persen(self):
        urutan = [
            StatusPermohonan.DRAFT,
            StatusPermohonan.DIAJUKAN,
            StatusPermohonan.VERIFIKASI,
            StatusPermohonan.DIPROSES,
            StatusPermohonan.SELESAI,
        ]
        try:
            idx = urutan.index(self.status)
            return int((idx / (len(urutan) - 1)) * 100)
        except ValueError:
            return 0


def upload_berkas_path(instance, filename):
    return f"berkas/{instance.permohonan.id}/{instance.jenis}/{filename}"


class Berkas(models.Model):
    """Dokumen pendukung yang diunggah pemohon."""

    class JenisBerkas(models.TextChoices):
        AKTA_KELAHIRAN = "akta_kelahiran", "Akta Kelahiran"
        KK             = "kk",             "Kartu Keluarga"
        BUKU_NIKAH     = "buku_nikah",     "Buku Nikah Orang Tua"
        KTP_AYAH       = "ktp_ayah",       "KTP Ayah / Akta Kematian Ayah"
        KTP_IBU        = "ktp_ibu",        "KTP Ibu / Akta Kematian Ibu"

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    permohonan   = models.ForeignKey(Permohonan, on_delete=models.CASCADE, related_name="berkas")
    jenis        = models.CharField(max_length=30, choices=JenisBerkas.choices)
    file         = models.FileField(upload_to=upload_berkas_path)
    nama_file    = models.CharField(max_length=255)
    diunggah_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Berkas"
        verbose_name_plural = "Berkas"
        unique_together = [("permohonan", "jenis")]

    def __str__(self):
        return f"{self.get_jenis_display()} — {self.permohonan.nama_anak}"


class RiwayatStatus(models.Model):
    """Log perubahan status permohonan."""
    permohonan  = models.ForeignKey(Permohonan, on_delete=models.CASCADE, related_name="riwayat")
    status_lama = models.CharField(max_length=20, choices=StatusPermohonan.choices, blank=True)
    status_baru = models.CharField(max_length=20, choices=StatusPermohonan.choices)
    catatan     = models.TextField(blank=True)
    diubah_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-dibuat_pada"]
        verbose_name = "Riwayat Status"
        verbose_name_plural = "Riwayat Status"

def upload_hasil_path(instance, filename):
    """File hasil akta disimpan di: media/hasil/<id_permohonan>/<filename>"""
    return f"hasil/{instance.permohonan.id}/{filename}"


class HasilAkta(models.Model):
    """Dokumen hasil keabsahan akta yang diunggah oleh admin/petugas."""
    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    permohonan   = models.OneToOneField(
        Permohonan,
        on_delete=models.CASCADE,
        related_name="hasil_akta",
    )
    file         = models.FileField(upload_to=upload_hasil_path)
    nama_file    = models.CharField(max_length=255)
    catatan      = models.TextField(blank=True, verbose_name="Catatan untuk pemohon")
    diunggah_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="hasil_diunggah",
    )
    diunggah_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Hasil Akta"
        verbose_name_plural = "Hasil Akta"

    def __str__(self):
        return f"Hasil Akta — {self.permohonan.nama_anak}"
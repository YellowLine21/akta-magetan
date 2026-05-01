from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Permohonan, Berkas, RiwayatStatus, StatusPermohonan
from .forms import FormDataAkta, FormUploadBerkas


# ─── HELPER ──────────────────────────────────────────────────────────────────

def _simpan_berkas(permohonan, files_dict):
    """Simpan setiap file yang diupload ke model Berkas."""
    mapping = {
        "akta_kelahiran": Berkas.JenisBerkas.AKTA_KELAHIRAN,
        "kk":             Berkas.JenisBerkas.KK,
        "buku_nikah":     Berkas.JenisBerkas.BUKU_NIKAH,
        "ktp_ayah":       Berkas.JenisBerkas.KTP_AYAH,
        "ktp_ibu":        Berkas.JenisBerkas.KTP_IBU,
    }
    for field_name, jenis in mapping.items():
        f = files_dict.get(field_name)
        if f:
            Berkas.objects.update_or_create(
                permohonan=permohonan,
                jenis=jenis,
                defaults={"file": f, "nama_file": f.name},
            )


def _catat_riwayat(permohonan, status_baru, user, catatan=""):
    RiwayatStatus.objects.create(
        permohonan=permohonan,
        status_lama=permohonan.status,
        status_baru=status_baru,
        diubah_oleh=user,
        catatan=catatan,
    )
    permohonan.status = status_baru
    if status_baru == StatusPermohonan.DIAJUKAN:
        permohonan.diajukan_pada = timezone.now()
    permohonan.save()


# ─── LANGKAH 1: FORM DATA AKTA ───────────────────────────────────────────────

@login_required
def langkah_data(request, pk=None):
    """Isi data identitas anak & orang tua."""
    permohonan = None
    if pk:
        permohonan = get_object_or_404(Permohonan, pk=pk, pemohon=request.user)

    if request.method == "POST":
        form = FormDataAkta(request.POST, instance=permohonan)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.pemohon = request.user
            obj.status  = StatusPermohonan.DRAFT
            obj.save()
            messages.success(request, "Data akta berhasil disimpan. Lanjutkan upload berkas.")
            return redirect("permohonan:langkah_upload", pk=obj.pk)
    else:
        form = FormDataAkta(instance=permohonan)

    return render(request, "permohonan/langkah_data.html", {
        "form": form,
        "permohonan": permohonan,
        "langkah_aktif": 1,
    })


# ─── LANGKAH 2: UPLOAD BERKAS ────────────────────────────────────────────────

@login_required
def langkah_upload(request, pk):
    """Upload dokumen pendukung."""
    permohonan = get_object_or_404(Permohonan, pk=pk, pemohon=request.user)

    if request.method == "POST":
        form = FormUploadBerkas(request.POST, request.FILES)
        if form.is_valid():
            _simpan_berkas(permohonan, request.FILES)
            messages.success(request, "Berkas berhasil diunggah. Periksa kembali data Anda.")
            return redirect("permohonan:langkah_review", pk=permohonan.pk)
    else:
        form = FormUploadBerkas()

    berkas_tersedia = {b.jenis: b for b in permohonan.berkas.all()}

    return render(request, "permohonan/langkah_upload.html", {
        "form": form,
        "permohonan": permohonan,
        "berkas_tersedia": berkas_tersedia,
        "langkah_aktif": 2,
    })


# ─── LANGKAH 3: REVIEW ───────────────────────────────────────────────────────

@login_required
def langkah_review(request, pk):
    """Halaman review — tampilkan semua data sebelum submit."""
    permohonan = get_object_or_404(Permohonan, pk=pk, pemohon=request.user)
    berkas_list = permohonan.berkas.all()

    if request.method == "POST":
        # Tombol "Ajukan Permohonan"
        _catat_riwayat(permohonan, StatusPermohonan.DIAJUKAN, request.user, "Permohonan diajukan oleh pemohon.")
        messages.success(request, "Permohonan berhasil diajukan! Kami akan memproses dalam 2 hari kerja.")
        return redirect("permohonan:notifikasi", pk=permohonan.pk)

    return render(request, "permohonan/langkah_review.html", {
        "permohonan": permohonan,
        "berkas_list": berkas_list,
        "langkah_aktif": 3,
    })


# ─── LANGKAH 4: NOTIFIKASI / STATUS ──────────────────────────────────────────

@login_required
def notifikasi(request, pk):
    """Halaman pelacakan status permohonan."""
    permohonan = get_object_or_404(Permohonan, pk=pk, pemohon=request.user)
    riwayat    = permohonan.riwayat.all()

    return render(request, "permohonan/notifikasi.html", {
        "permohonan": permohonan,
        "riwayat": riwayat,
        "langkah_aktif": 4,
    })


# ─── DAFTAR PERMOHONAN MILIK USER ────────────────────────────────────────────

@login_required
def daftar_permohonan(request):
    """Semua permohonan milik user yang login."""
    permohonan_list = Permohonan.objects.filter(pemohon=request.user)
    return render(request, "permohonan/daftar.html", {"permohonan_list": permohonan_list})

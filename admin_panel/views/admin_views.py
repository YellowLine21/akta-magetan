import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.http import JsonResponse
from django.http import FileResponse, Http404

from permohonan.models import Permohonan, Berkas, RiwayatStatus, StatusPermohonan, HasilAkta


def _catat_dan_ubah_status(permohonan, status_baru, user, catatan=""):
    """Helper: catat riwayat lalu ubah status."""
    RiwayatStatus.objects.create(
        permohonan  = permohonan,
        status_lama = permohonan.status,
        status_baru = status_baru,
        diubah_oleh = user,
        catatan     = catatan,
    )
    permohonan.status = status_baru
    permohonan.save()


# ─── DASHBOARD ADMIN ─────────────────────────────────────────────────────────

@staff_member_required
def admin_dashboard(request):
    """Ringkasan statistik semua permohonan."""
    total      = Permohonan.objects.count()
    per_status = {
        s.value: Permohonan.objects.filter(status=s).count()
        for s in StatusPermohonan
    }
    terbaru = Permohonan.objects.select_related("pemohon").order_by("-dibuat_pada")[:5]

    return render(request, "admin_custom/dashboard.html", {
        "total": total,
        "per_status": per_status,
        "terbaru": terbaru,
        "StatusPermohonan": StatusPermohonan,
    })


# ─── DAFTAR PERMOHONAN ────────────────────────────────────────────────────────

@staff_member_required
def admin_daftar(request):
    """Tabel semua permohonan dengan filter & pencarian."""
    qs = Permohonan.objects.select_related("pemohon").order_by("-dibuat_pada")

    # Filter status
    status_filter = request.GET.get("status", "")
    if status_filter:
        qs = qs.filter(status=status_filter)

    # Pencarian
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(nama_anak__icontains=q) |
            Q(nik_anak__icontains=q)  |
            Q(pemohon__nama__icontains=q) |
            Q(pemohon__nik__icontains=q)  |
            Q(nomor_akta__icontains=q)
        )

    return render(request, "admin_custom/daftar.html", {
        "permohonan_list": qs,
        "status_filter": status_filter,
        "q": q,
        "StatusPermohonan": StatusPermohonan,
        "jumlah": qs.count(),
    })


# ─── DETAIL PERMOHONAN ────────────────────────────────────────────────────────

@staff_member_required
def admin_detail(request, pk):
    """Halaman detail: data lengkap + berkas + riwayat + ubah status."""
    permohonan = get_object_or_404(Permohonan.objects.select_related("pemohon"), pk=pk)
    berkas_list = permohonan.berkas.all()
    riwayat     = permohonan.riwayat.select_related("diubah_oleh").all()

    if request.method == "POST":
        status_baru = request.POST.get("status_baru")
        catatan     = request.POST.get("catatan", "").strip()

        valid_status = [s.value for s in StatusPermohonan]
        if status_baru not in valid_status:
            messages.error(request, "Status tidak valid.")
        elif status_baru == permohonan.status:
            messages.warning(request, "Status tidak berubah.")
        else:
            _catat_dan_ubah_status(permohonan, status_baru, request.user, catatan)
            messages.success(
                request,
                f"Status diubah ke '{permohonan.get_status_display()}' dan riwayat dicatat."
            )
            return redirect("admin_custom:detail", pk=pk)

    return render(request, "admin_custom/detail.html", {
        "p": permohonan,
        "berkas_list": berkas_list,
        "riwayat": riwayat,
        "StatusPermohonan": StatusPermohonan,
        "semua_status": StatusPermohonan.choices,
    })

EKSTENSI_DIIZINKAN = [".pdf", ".jpg", ".jpeg", ".png"]
UKURAN_MAKS_MB     = 10


def _validasi_file_hasil(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in EKSTENSI_DIIZINKAN:
        raise ValueError(f"Format '{ext}' tidak diizinkan. Gunakan PDF, JPG, atau PNG.")
    if file.size > UKURAN_MAKS_MB * 1024 * 1024:
        raise ValueError(f"Ukuran file maksimal {UKURAN_MAKS_MB} MB.")


@staff_member_required
def admin_upload_hasil(request, pk):
    """
    Upload dokumen hasil keabsahan akta oleh admin.
    Otomatis mengubah status permohonan menjadi SELESAI.
    """
    from permohonan.models import HasilAkta, StatusPermohonan, RiwayatStatus

    permohonan = get_object_or_404(
        __import__('permohonan.models', fromlist=['Permohonan']).Permohonan,
        pk=pk
    )

    if request.method != "POST":
        return redirect("admin_custom:detail", pk=pk)

    file    = request.FILES.get("file_hasil")
    catatan = request.POST.get("catatan_hasil", "").strip()

    if not file:
        messages.error(request, "Pilih file terlebih dahulu.")
        return redirect("admin_custom:detail", pk=pk)

    try:
        _validasi_file_hasil(file)
    except ValueError as e:
        messages.error(request, str(e))
        return redirect("admin_custom:detail", pk=pk)

    # Simpan atau timpa hasil akta yang sudah ada
    hasil, _ = HasilAkta.objects.update_or_create(
        permohonan=permohonan,
        defaults={
            "file":          file,
            "nama_file":     file.name,
            "catatan":       catatan,
            "diunggah_oleh": request.user,
        },
    )

    # Ubah status ke SELESAI jika belum
    if permohonan.status != StatusPermohonan.SELESAI:
        RiwayatStatus.objects.create(
            permohonan  = permohonan,
            status_lama = permohonan.status,
            status_baru = StatusPermohonan.SELESAI,
            diubah_oleh = request.user,
            catatan     = catatan or "Dokumen hasil akta telah diunggah oleh petugas.",
        )
        permohonan.status = StatusPermohonan.SELESAI
        permohonan.save()

    messages.success(
        request,
        f"Dokumen hasil akta '{file.name}' berhasil diunggah. Status diubah ke Selesai."
    )
    return redirect("admin_custom:detail", pk=pk)


@staff_member_required
def admin_hapus_hasil(request, pk):
    """Hapus dokumen hasil akta (khusus admin)."""
    from permohonan.models import HasilAkta

    hasil = get_object_or_404(HasilAkta, permohonan__pk=pk)
    nama  = hasil.nama_file
    hasil.file.delete(save=False)   # hapus file fisik dari disk
    hasil.delete()
    messages.success(request, f"Dokumen '{nama}' berhasil dihapus.")
    return redirect("admin_custom:detail", pk=pk)
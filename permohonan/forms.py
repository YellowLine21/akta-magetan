from django import forms
from .models import Permohonan, Berkas


ATTRS_TEXT  = lambda ph: {"placeholder": ph, "class": "form-input"}
ATTRS_DATE  = lambda: {"type": "date", "class": "form-input"}
ATTRS_FILE  = lambda: {"class": "form-file", "accept": ".pdf,.jpg,.jpeg,.png"}


class FormDataAkta(forms.ModelForm):
    """Langkah 1 — Data identitas anak & orang tua."""

    tanggal_lahir   = forms.DateField(widget=forms.DateInput(attrs=ATTRS_DATE()))
    tanggal_menikah = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs=ATTRS_DATE()),
        label="Tanggal Menikah (opsional)",
    )

    class Meta:
        model  = Permohonan
        fields = [
            "nama_anak", "nik_anak", "tempat_lahir", "tanggal_lahir", "nomor_akta",
            "nama_ayah", "nik_ayah", "no_nikah_ayah",
            "nama_ibu",  "nik_ibu",  "no_nikah_ibu",
            "tanggal_menikah",
        ]
        widgets = {
            "nama_anak":    forms.TextInput(attrs=ATTRS_TEXT("Nama lengkap anak")),
            "nik_anak":     forms.TextInput(attrs=ATTRS_TEXT("16 digit NIK anak")),
            "tempat_lahir": forms.TextInput(attrs=ATTRS_TEXT("Kota/kabupaten tempat lahir")),
            "nomor_akta":   forms.TextInput(attrs=ATTRS_TEXT("Nomor akta kelahiran")),
            "nama_ayah":    forms.TextInput(attrs=ATTRS_TEXT("Nama lengkap ayah")),
            "nik_ayah":     forms.TextInput(attrs=ATTRS_TEXT("16 digit NIK ayah")),
            "no_nikah_ayah":forms.TextInput(attrs=ATTRS_TEXT("Nomor buku nikah (opsional)")),
            "nama_ibu":     forms.TextInput(attrs=ATTRS_TEXT("Nama lengkap ibu")),
            "nik_ibu":      forms.TextInput(attrs=ATTRS_TEXT("16 digit NIK ibu")),
            "no_nikah_ibu": forms.TextInput(attrs=ATTRS_TEXT("Nomor buku nikah (opsional)")),
        }
        labels = {
            "no_nikah_ayah": "No. Buku Nikah Ayah (opsional)",
            "no_nikah_ibu":  "No. Buku Nikah Ibu (opsional)",
        }

    def _clean_nik(self, field):
        val = self.cleaned_data.get(field, "")
        if not val.isdigit():
            raise forms.ValidationError("NIK hanya boleh berisi angka.")
        if len(val) != 16:
            raise forms.ValidationError("NIK harus 16 digit.")
        return val

    def clean_nik_anak(self):  return self._clean_nik("nik_anak")
    def clean_nik_ayah(self):  return self._clean_nik("nik_ayah")
    def clean_nik_ibu(self):   return self._clean_nik("nik_ibu")


class FormUploadBerkas(forms.Form):
    """Langkah 2 — Upload dokumen pendukung."""
    akta_kelahiran = forms.FileField(
        label="Akta Kelahiran (wajib)",
        widget=forms.FileInput(attrs=ATTRS_FILE()),
    )
    kk = forms.FileField(
        label="Kartu Keluarga (wajib)",
        widget=forms.FileInput(attrs=ATTRS_FILE()),
    )
    buku_nikah = forms.FileField(
        label="Buku Nikah Orang Tua (wajib)",
        widget=forms.FileInput(attrs=ATTRS_FILE()),
    )
    ktp_ayah = forms.FileField(
        label="KTP Ayah / Akta Kematian Ayah (wajib)",
        widget=forms.FileInput(attrs=ATTRS_FILE()),
    )
    ktp_ibu = forms.FileField(
        label="KTP Ibu / Akta Kematian Ibu (wajib)",
        widget=forms.FileInput(attrs=ATTRS_FILE()),
    )

    MAX_SIZE_MB = 5

    def clean(self):
        cleaned = super().clean()
        for field_name, f in list(cleaned.items()):
            if f and hasattr(f, "size"):
                if f.size > self.MAX_SIZE_MB * 1024 * 1024:
                    self.add_error(field_name, f"Ukuran file maksimal {self.MAX_SIZE_MB} MB.")
        return cleaned

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import CustomUser


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Buat password kuat"}),
        min_length=8,
    )
    password_confirm = forms.CharField(
        label="Konfirmasi Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Ulangi password"}),
    )

    class Meta:
        model = CustomUser
        fields = ["nama", "nik", "no_hp", "email"]
        widgets = {
            "nama": forms.TextInput(attrs={"placeholder": "Nama lengkap sesuai KTP"}),
            "nik": forms.TextInput(attrs={"placeholder": "16 digit NIK KTP"}),
            "no_hp": forms.TextInput(attrs={"placeholder": "Contoh: 08123456789"}),
            "email": forms.EmailInput(attrs={"placeholder": "Alamat email aktif"}),
        }

    def clean_nik(self):
        nik = self.cleaned_data.get("nik")
        if not nik.isdigit():
            raise forms.ValidationError("NIK hanya boleh berisi angka.")
        if len(nik) != 16:
            raise forms.ValidationError("NIK harus terdiri dari 16 digit.")
        return nik

    def clean_no_hp(self):
        no_hp = self.cleaned_data.get("no_hp")
        if not no_hp.startswith("08") and not no_hp.startswith("+62"):
            raise forms.ValidationError("Nomor HP harus diawali 08 atau +62.")
        return no_hp

    def clean(self):
        cleaned_data = super().clean()
        pw = cleaned_data.get("password")
        pw_confirm = cleaned_data.get("password_confirm")
        if pw and pw_confirm and pw != pw_confirm:
            raise forms.ValidationError("Password dan konfirmasi password tidak cocok.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    nik = forms.CharField(
        label="NIK",
        max_length=16,
        widget=forms.TextInput(attrs={"placeholder": "Masukkan 16 digit NIK"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Masukkan password"}),
    )

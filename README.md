# Akta Magetan — Sistem Permohonan Akta Kelahiran

Aplikasi Django untuk pengelolaan permohonan akta kelahiran di Kabupaten Magetan.

---

## Environment Variables

Semua variabel berikut **wajib** dikonfigurasi di Railway (atau file `.env` untuk development lokal) sebelum aplikasi dapat berjalan dengan benar.

### Wajib

| Variabel | Keterangan |
|---|---|
| `SECRET_KEY` | Django secret key. Generate dengan `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DATABASE_URL` | URL koneksi PostgreSQL (disediakan otomatis oleh Railway Postgres plugin) |
| `EMAIL_HOST_USER` | Alamat Gmail yang digunakan sebagai pengirim email verifikasi, mis. `noreply@example.com` |
| `EMAIL_HOST_PASSWORD` | **App Password** Gmail (bukan password akun biasa). Buat di [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords). Pastikan 2-Step Verification aktif di akun Gmail tersebut. |

### Opsional

| Variabel | Default | Keterangan |
|---|---|---|
| `DEBUG` | `False` | Set `True` hanya untuk development lokal |
| `ALLOWED_HOSTS` | `*` | Daftar host yang diizinkan, dipisah koma |

---

## Konfigurasi Email (Gmail SMTP)

Aplikasi menggunakan Gmail SMTP untuk mengirim email verifikasi saat registrasi pengguna baru.

**Langkah setup App Password Gmail:**

1. Buka [myaccount.google.com](https://myaccount.google.com) dengan akun Gmail pengirim.
2. Aktifkan **2-Step Verification** jika belum aktif.
3. Buka **Security → App passwords**.
4. Buat App Password baru (pilih app: *Mail*, device: *Other*).
5. Salin 16-karakter password yang dihasilkan.
6. Set sebagai nilai `EMAIL_HOST_PASSWORD` di Railway.

> **Catatan:** App Password berbeda dari password login Gmail biasa. Jangan gunakan password akun Gmail langsung — Gmail akan menolak koneksi SMTP.

---

## Development Lokal

Buat file `.env` di root project (jangan di-commit ke Git):

```
SECRET_KEY=django-insecure-ganti-dengan-key-acak
DEBUG=True
EMAIL_HOST_USER=emailanda@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
```

Install dependensi dan jalankan server:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## Deploy ke Railway

1. Push kode ke GitHub.
2. Buat project baru di Railway dan hubungkan ke repository ini.
3. Tambahkan plugin **PostgreSQL** — `DATABASE_URL` akan terisi otomatis.
4. Set semua environment variables wajib di tab **Variables**.
5. Railway akan otomatis menjalankan build dan deploy.

# imsydz Dev - Platform Penjualan Template Website

Platform fullstack untuk penjualan template website dengan sistem autentikasi, manajemen lisensi, dan dashboard admin yang lengkap.

## 🚀 Fitur Utama

### Untuk User
- **Autentikasi Lengkap**: Register, login, logout dengan session management
- **Katalog Template**: Browse template dengan filter kategori dan pencarian
- **Detail Template**: Halaman detail dengan preview dan informasi lengkap
- **Sistem Pembelian**: Proses pembelian template dengan upload bukti pembayaran
- **Dashboard User**: Kelola template yang dimiliki dan riwayat transaksi
- **Download Template**: Download template yang sudah dibeli dengan lisensi valid

### Untuk Admin
- **Dashboard Admin**: Overview statistik platform dan aktivitas terbaru
- **Manajemen Template**: Upload, edit, dan hapus template
- **Manajemen User**: Kelola user dan role
- **Manajemen Transaksi**: Review dan konfirmasi pembayaran
- **Manajemen Lisensi**: Kelola lisensi template user
- **Upload File**: Sistem upload untuk template dan gambar preview

### Fitur Teknis
- **Responsive Design**: Kompatibel dengan desktop dan mobile
- **Modern UI**: Desain dengan TailwindCSS dan animasi AOS
- **Security**: Password hashing, session management, dan middleware protection
- **File Management**: Upload dan download file dengan validasi
- **Database**: SQLite dengan SQLAlchemy ORM
- **Search & Filter**: Pencarian template dan filter kategori

## 🛠️ Teknologi yang Digunakan

- **Backend**: Python Flask 3.0+
- **Frontend**: HTML5, TailwindCSS, JavaScript
- **Database**: SQLite dengan SQLAlchemy
- **Authentication**: Flask-Login
- **File Upload**: Werkzeug
- **Icons**: Font Awesome 6
- **Animations**: AOS (Animate On Scroll)

## 📋 Persyaratan Sistem

- Python 3.11+
- pip (Python package manager)
- Virtual environment (recommended)

## 🔧 Instalasi

### 1. Clone Repository
```bash
git clone <repository-url>
cd imsydz-dev
```

### 2. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# atau
venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Jalankan Aplikasi
```bash
cd src
python main.py
```

Aplikasi akan berjalan di `http://localhost:5000`

## 👤 Akun Default

### Admin
- **Username**: `imsyad`
- **Password**: `imsyad1373`
- **Role**: `admin`

Gunakan akun ini untuk mengakses dashboard admin dan mengelola platform.

## 📁 Struktur Proyek

```
imsydz-dev/
├── src/
│   ├── main.py                 # Entry point aplikasi
│   ├── middleware.py           # Middleware dan decorators
│   ├── models/                 # Database models
│   │   ├── __init__.py
│   │   ├── user.py            # Model User
│   │   ├── template.py        # Model Template
│   │   ├── license.py         # Model License
│   │   └── transaction.py     # Model Transaction
│   ├── routes/                 # Route handlers
│   │   ├── auth.py            # Authentication routes
│   │   ├── main.py            # Main routes
│   │   ├── template.py        # Template routes
│   │   └── admin.py           # Admin routes
│   ├── templates/             # HTML templates
│   │   ├── base.html          # Base template
│   │   ├── main/              # Main pages
│   │   ├── auth/              # Auth pages
│   │   └── admin/             # Admin pages
│   └── static/                # Static files
│       └── uploads/           # Upload directory
├── venv/                      # Virtual environment
├── requirements.txt           # Python dependencies
├── todo.md                   # Development progress
└── README.md                 # Documentation
```

## 🎯 Penggunaan

### Untuk User

1. **Registrasi**: Buat akun baru di `/auth/register`
2. **Login**: Masuk ke akun di `/auth/login`
3. **Browse Template**: Lihat katalog template di `/templates`
4. **Beli Template**: Pilih template dan lakukan pembelian
5. **Upload Bukti**: Upload bukti pembayaran
6. **Download**: Download template setelah dikonfirmasi admin

### Untuk Admin

1. **Login Admin**: Gunakan akun admin default
2. **Dashboard**: Akses `/admin/dashboard` untuk overview
3. **Tambah Template**: Upload template baru di `/admin/add-template`
4. **Kelola Transaksi**: Review pembayaran di `/admin/transactions`
5. **Kelola User**: Manajemen user di `/admin/users`

## 🔐 Sistem Keamanan

### Authentication
- Password di-hash menggunakan Werkzeug
- Session management dengan Flask-Login
- Middleware untuk proteksi route admin

### Authorization
- Role-based access control (admin/user)
- License validation untuk download template
- File upload validation dan sanitization

### Data Protection
- SQL injection protection dengan SQLAlchemy ORM
- XSS protection dengan template escaping
- CSRF protection dengan Flask-WTF

## 📊 Database Schema

### Users
- `id`: Primary key
- `username`: Unique username
- `email`: User email
- `password_hash`: Hashed password
- `role`: User role (admin/user)
- `created_at`: Registration timestamp

### Templates
- `id`: Primary key
- `name`: Template name
- `description`: Template description
- `price`: Template price
- `category`: Template category
- `tags`: JSON array of tags
- `file_path`: Path to template file
- `image`: Preview image URL

### Licenses
- `id`: Primary key
- `user_id`: Foreign key to Users
- `template_id`: Foreign key to Templates
- `license_key`: Unique license key
- `status`: License status (valid/invalid)
- `created_at`: License creation timestamp

### Transactions
- `id`: Primary key
- `user_id`: Foreign key to Users
- `template_id`: Foreign key to Templates
- `amount`: Transaction amount
- `status`: Transaction status (pending/confirmed/rejected)
- `payment_proof`: Path to payment proof image

## 🎨 Customization

### Styling
Template menggunakan TailwindCSS dengan custom color scheme:
- **Primary**: Blue gradient
- **Secondary**: Purple gradient
- **Accent**: Orange dan purple

### Configuration
Edit `main.py` untuk mengubah:
- Database URL
- Upload directories
- Secret key
- Debug mode

## 🚀 Deployment

### Development
```bash
python src/main.py
```

### Production
Gunakan WSGI server seperti Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

## 🐛 Troubleshooting

### Common Issues

1. **Template Not Found Error**
   - Pastikan semua file template ada di folder `templates/`
   - Check import path di route handlers

2. **Database Error**
   - Hapus file `instance/database.db` dan restart aplikasi
   - Database akan dibuat ulang dengan seeder data

3. **Upload Error**
   - Pastikan folder `static/uploads/` ada dan writable
   - Check file size dan format yang diupload

4. **Permission Error**
   - Pastikan user memiliki akses ke folder project
   - Check virtual environment activation

## 📝 Development Notes

### Seeder Data
Aplikasi include 4 template contoh:
- Modern Landing Page (Rp 150,000)
- Portfolio Creative (Rp 200,000)
- E-Commerce Store (Rp 500,000)
- Company Profile (Rp 300,000)

### File Upload
- Template files: ZIP/RAR max 50MB
- Images: JPG/PNG/WebP max 2MB
- Payment proof: JPG/PNG max 5MB

### API Endpoints
- `/api/templates` - Get templates (with filters)
- `/api/template/<id>` - Get template detail
- `/api/user/licenses` - Get user licenses

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

Untuk bantuan dan support:
- **WhatsApp**: +62 895-3409-3450
- **Email**: imsyad@imsydz.dev
- **Website**: https://imsydz.dev

---

**imsydz Dev** - Platform Penjualan Template Website Terpercaya


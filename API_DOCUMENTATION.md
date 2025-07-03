# API Documentation - imsydz Dev Platform

Dokumentasi lengkap untuk API endpoints yang tersedia di platform imsydz Dev.

## Base URL
```
http://localhost:5000
```

## Authentication

### Login
**POST** `/auth/login`

Login user dan mendapatkan session.

**Request Body:**
```json
{
    "username": "string",
    "password": "string",
    "remember": "boolean (optional)"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login berhasil",
    "redirect": "/dashboard"
}
```

### Register
**POST** `/auth/register`

Registrasi user baru.

**Request Body:**
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "confirm_password": "string"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Registrasi berhasil",
    "redirect": "/auth/login"
}
```

### Logout
**POST** `/auth/logout`

Logout user dan hapus session.

**Response:**
```json
{
    "success": true,
    "message": "Logout berhasil",
    "redirect": "/"
}
```

## Templates

### Get All Templates
**GET** `/templates`

Mendapatkan daftar semua template dengan filter dan pagination.

**Query Parameters:**
- `page` (int): Halaman (default: 1)
- `per_page` (int): Item per halaman (default: 12)
- `category` (string): Filter kategori
- `search` (string): Pencarian nama template
- `sort` (string): Urutan (newest, oldest, price_low, price_high, name)

**Response:**
```json
{
    "templates": [
        {
            "id": 1,
            "name": "Modern Landing Page",
            "description": "Template landing page modern...",
            "price": 150000,
            "category": "landing-page",
            "tags": ["modern", "responsive", "startup"],
            "image": "/static/uploads/images/template1.jpg",
            "created_at": "2025-01-01T00:00:00Z"
        }
    ],
    "pagination": {
        "page": 1,
        "pages": 5,
        "per_page": 12,
        "total": 50,
        "has_next": true,
        "has_prev": false
    },
    "categories": ["landing-page", "portfolio", "ecommerce", "corporate"]
}
```

### Get Template Detail
**GET** `/template/<int:id>`

Mendapatkan detail template berdasarkan ID.

**Response:**
```json
{
    "template": {
        "id": 1,
        "name": "Modern Landing Page",
        "description": "Template landing page modern dengan desain responsif...",
        "price": 150000,
        "category": "landing-page",
        "tags": ["modern", "responsive", "startup"],
        "image": "/static/uploads/images/template1.jpg",
        "file_path": "/static/uploads/templates/template1.zip",
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z"
    },
    "user_license": {
        "id": 1,
        "license_key": "LIC-ABC123",
        "status": "valid",
        "created_at": "2025-01-01T00:00:00Z"
    },
    "related_templates": [
        {
            "id": 2,
            "name": "Portfolio Creative",
            "price": 200000,
            "image": "/static/uploads/images/template2.jpg"
        }
    ]
}
```

### Buy Template
**POST** `/template/<int:id>/buy`

Membeli template (memerlukan login).

**Request Body:**
```json
{
    "payment_method": "transfer",
    "payment_proof": "file (multipart/form-data)"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Pembelian berhasil, menunggu konfirmasi admin",
    "transaction_id": 123,
    "redirect": "/dashboard"
}
```

### Download Template
**GET** `/template/<int:id>/download`

Download template (memerlukan lisensi valid).

**Response:**
- File download (ZIP)
- Error 403 jika tidak memiliki lisensi

### Preview Template
**GET** `/template/<int:id>/preview`

Preview template online.

**Response:**
- HTML preview template
- Error 403 jika tidak memiliki lisensi

## User Dashboard

### Get User Dashboard
**GET** `/dashboard`

Mendapatkan data dashboard user (memerlukan login).

**Response:**
```json
{
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "role": "user",
        "created_at": "2025-01-01T00:00:00Z"
    },
    "stats": {
        "total_templates": 5,
        "total_spent": 1500000,
        "pending_transactions": 1
    },
    "recent_templates": [
        {
            "id": 1,
            "name": "Modern Landing Page",
            "license_status": "valid",
            "purchased_at": "2025-01-01T00:00:00Z"
        }
    ],
    "recent_transactions": [
        {
            "id": 1,
            "template_name": "Modern Landing Page",
            "amount": 150000,
            "status": "confirmed",
            "created_at": "2025-01-01T00:00:00Z"
        }
    ]
}
```

## Admin Endpoints

### Get Admin Dashboard
**GET** `/admin/dashboard`

Mendapatkan data dashboard admin (memerlukan role admin).

**Response:**
```json
{
    "stats": {
        "total_users": 100,
        "total_templates": 25,
        "pending_transactions": 5,
        "total_revenue": 10000000,
        "confirmed_transactions": 45,
        "total_transactions": 50,
        "total_licenses": 45,
        "active_licenses": 40
    },
    "recent_transactions": [
        {
            "id": 1,
            "user": {
                "username": "john_doe"
            },
            "template": {
                "name": "Modern Landing Page"
            },
            "amount": 150000,
            "status": "pending",
            "created_at": "2025-01-01T00:00:00Z"
        }
    ],
    "recent_users": [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "created_at": "2025-01-01T00:00:00Z"
        }
    ]
}
```

### Add Template
**POST** `/admin/add-template`

Menambah template baru (memerlukan role admin).

**Request Body (multipart/form-data):**
```
name: string
description: string
price: number
category: string
tags: string (JSON array)
template_file: file (ZIP/RAR)
template_image: file (JPG/PNG)
```

**Response:**
```json
{
    "success": true,
    "message": "Template berhasil ditambahkan",
    "template_id": 123,
    "redirect": "/admin/templates"
}
```

### Get All Transactions
**GET** `/admin/transactions`

Mendapatkan semua transaksi (memerlukan role admin).

**Query Parameters:**
- `page` (int): Halaman (default: 1)
- `status` (string): Filter status (pending, confirmed, rejected)

**Response:**
```json
{
    "transactions": [
        {
            "id": 1,
            "user": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com"
            },
            "template": {
                "id": 1,
                "name": "Modern Landing Page",
                "price": 150000
            },
            "amount": 150000,
            "status": "pending",
            "payment_proof": "/static/uploads/payments/proof1.jpg",
            "created_at": "2025-01-01T00:00:00Z"
        }
    ],
    "pagination": {
        "page": 1,
        "pages": 3,
        "total": 25
    }
}
```

### Confirm Transaction
**POST** `/admin/transaction/<int:id>/confirm`

Konfirmasi transaksi dan buat lisensi (memerlukan role admin).

**Response:**
```json
{
    "success": true,
    "message": "Transaksi dikonfirmasi dan lisensi dibuat",
    "license_key": "LIC-ABC123"
}
```

### Reject Transaction
**POST** `/admin/transaction/<int:id>/reject`

Tolak transaksi (memerlukan role admin).

**Request Body:**
```json
{
    "reason": "string (optional)"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Transaksi ditolak"
}
```

## Error Responses

### 400 Bad Request
```json
{
    "error": "Bad Request",
    "message": "Invalid input data",
    "details": {
        "field": "error description"
    }
}
```

### 401 Unauthorized
```json
{
    "error": "Unauthorized",
    "message": "Login required"
}
```

### 403 Forbidden
```json
{
    "error": "Forbidden",
    "message": "Insufficient permissions"
}
```

### 404 Not Found
```json
{
    "error": "Not Found",
    "message": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal Server Error",
    "message": "Something went wrong"
}
```

## Rate Limiting

- **General API**: 100 requests per minute per IP
- **Upload endpoints**: 10 requests per minute per user
- **Download endpoints**: 50 requests per minute per user

## File Upload Specifications

### Template Files
- **Format**: ZIP, RAR
- **Max Size**: 50MB
- **Content**: HTML, CSS, JS files with documentation

### Images
- **Format**: JPG, PNG, WebP
- **Max Size**: 2MB (preview images), 5MB (payment proof)
- **Dimensions**: Recommended 1200x800px for preview images

## Security

### Authentication
- Session-based authentication
- Password hashing with Werkzeug
- CSRF protection on forms

### Authorization
- Role-based access control
- License validation for downloads
- Admin-only endpoints protection

### File Security
- File type validation
- Filename sanitization
- Upload directory isolation

## SDK Examples

### JavaScript (Fetch API)
```javascript
// Login
const login = async (username, password) => {
    const response = await fetch('/auth/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
    });
    return response.json();
};

// Get templates
const getTemplates = async (page = 1, category = '') => {
    const params = new URLSearchParams({ page, category });
    const response = await fetch(`/templates?${params}`);
    return response.json();
};
```

### Python (Requests)
```python
import requests

# Login
def login(username, password):
    response = requests.post('http://localhost:5000/auth/login', json={
        'username': username,
        'password': password
    })
    return response.json()

# Get templates
def get_templates(page=1, category=''):
    params = {'page': page, 'category': category}
    response = requests.get('http://localhost:5000/templates', params=params)
    return response.json()
```

## Webhook Events

### Transaction Confirmed
Triggered when admin confirms a transaction.

**Payload:**
```json
{
    "event": "transaction.confirmed",
    "data": {
        "transaction_id": 123,
        "user_id": 456,
        "template_id": 789,
        "license_key": "LIC-ABC123",
        "timestamp": "2025-01-01T00:00:00Z"
    }
}
```

### License Created
Triggered when a new license is created.

**Payload:**
```json
{
    "event": "license.created",
    "data": {
        "license_id": 123,
        "user_id": 456,
        "template_id": 789,
        "license_key": "LIC-ABC123",
        "timestamp": "2025-01-01T00:00:00Z"
    }
}
```

---

**Note**: Semua endpoint yang memerlukan autentikasi harus menyertakan session cookie yang valid. Untuk testing, gunakan tools seperti Postman atau curl dengan cookie support.


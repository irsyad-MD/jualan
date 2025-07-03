# Deployment Guide - imsydz Dev Platform

Panduan lengkap untuk deploy aplikasi imsydz Dev ke berbagai platform production.

## 📋 Persiapan Deployment

### 1. Environment Variables
Buat file `.env` untuk konfigurasi production:

```bash
# Database
DATABASE_URL=sqlite:///production.db

# Security
SECRET_KEY=your-super-secret-key-here
FLASK_ENV=production

# Upload Configuration
UPLOAD_FOLDER=/var/www/uploads
MAX_CONTENT_LENGTH=52428800  # 50MB

# Admin Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-admin-password
ADMIN_EMAIL=admin@yourdomain.com

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Payment Configuration
PAYMENT_METHODS=transfer,ewallet,crypto
BANK_ACCOUNT=1234567890
BANK_NAME=Bank Central Asia
ACCOUNT_HOLDER=imsydz Dev
```

### 2. Production Configuration
Update `main.py` untuk production:

```python
import os
from dotenv import load_dotenv

load_dotenv()

app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'fallback-secret-key'),
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///production.db'),
    UPLOAD_FOLDER=os.getenv('UPLOAD_FOLDER', '/var/www/uploads'),
    MAX_CONTENT_LENGTH=int(os.getenv('MAX_CONTENT_LENGTH', 52428800)),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    WTF_CSRF_ENABLED=True,
    SESSION_COOKIE_SECURE=True,  # HTTPS only
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)
)

# Disable debug in production
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### 3. Requirements Update
Tambahkan dependencies production:

```bash
pip install gunicorn python-dotenv psycopg2-binary
pip freeze > requirements.txt
```

## 🐳 Docker Deployment

### 1. Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directories
RUN mkdir -p /app/static/uploads/{templates,images,payments}

# Set permissions
RUN chmod -R 755 /app/static/uploads

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "src.main:app"]
```

### 2. Docker Compose
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=sqlite:///production.db
    volumes:
      - ./uploads:/app/static/uploads
      - ./instance:/app/instance
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./uploads:/var/www/uploads
    depends_on:
      - web
    restart: unless-stopped
```

### 3. Build dan Run
```bash
# Build image
docker build -t imsydz-dev .

# Run dengan docker-compose
docker-compose up -d

# Check logs
docker-compose logs -f web
```

## 🌐 VPS Deployment (Ubuntu)

### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx supervisor git

# Create user
sudo adduser imsydz
sudo usermod -aG sudo imsydz
su - imsydz
```

### 2. Application Setup
```bash
# Clone repository
git clone <your-repo-url> /home/imsydz/imsydz-dev
cd /home/imsydz/imsydz-dev

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn python-dotenv

# Create directories
sudo mkdir -p /var/www/imsydz-dev/uploads/{templates,images,payments}
sudo chown -R imsydz:imsydz /var/www/imsydz-dev
```

### 3. Gunicorn Configuration
Create `/home/imsydz/imsydz-dev/gunicorn.conf.py`:

```python
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
user = "imsydz"
group = "imsydz"
```

### 4. Supervisor Configuration
Create `/etc/supervisor/conf.d/imsydz-dev.conf`:

```ini
[program:imsydz-dev]
command=/home/imsydz/imsydz-dev/venv/bin/gunicorn -c gunicorn.conf.py src.main:app
directory=/home/imsydz/imsydz-dev
user=imsydz
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/imsydz-dev.log
environment=PATH="/home/imsydz/imsydz-dev/venv/bin"
```

```bash
# Start supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start imsydz-dev
```

### 5. Nginx Configuration
Create `/etc/nginx/sites-available/imsydz-dev`:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # File Upload Limits
    client_max_body_size 50M;

    # Static Files
    location /static/ {
        alias /var/www/imsydz-dev/uploads/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/imsydz-dev /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## ☁️ Cloud Platform Deployment

### 1. Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "web: gunicorn src.main:app" > Procfile

# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Deploy
heroku create imsydz-dev
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
git push heroku main
```

### 2. Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### 3. DigitalOcean App Platform
Create `app.yaml`:

```yaml
name: imsydz-dev
services:
- name: web
  source_dir: /
  github:
    repo: your-username/imsydz-dev
    branch: main
  run_command: gunicorn --worker-tmp-dir /dev/shm --config gunicorn.conf.py src.main:app
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: FLASK_ENV
    value: production
  - key: SECRET_KEY
    value: your-secret-key
```

## 🔒 SSL Certificate Setup

### 1. Let's Encrypt (Free)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 2. Cloudflare (Free)
1. Add domain to Cloudflare
2. Update nameservers
3. Enable SSL/TLS encryption
4. Set SSL mode to "Full (strict)"

## 📊 Monitoring & Logging

### 1. Application Monitoring
```python
# Add to main.py
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/imsydz-dev.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('imsydz Dev startup')
```

### 2. System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Setup log rotation
sudo nano /etc/logrotate.d/imsydz-dev
```

```
/var/log/imsydz-dev.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 imsydz imsydz
}
```

## 🔧 Performance Optimization

### 1. Database Optimization
```python
# Use PostgreSQL for production
pip install psycopg2-binary

# Update DATABASE_URL
DATABASE_URL=postgresql://user:password@localhost/imsydz_dev
```

### 2. Caching
```python
# Install Redis
pip install redis flask-caching

# Add caching
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis'})
```

### 3. CDN Setup
```python
# Use Cloudflare or AWS CloudFront for static files
STATIC_URL = 'https://cdn.yourdomain.com/static/'
```

## 🔄 Backup Strategy

### 1. Database Backup
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
sqlite3 /home/imsydz/imsydz-dev/instance/database.db ".backup /backups/db_$DATE.db"
find /backups -name "db_*.db" -mtime +7 -delete
```

### 2. File Backup
```bash
#!/bin/bash
# backup_files.sh
tar -czf /backups/uploads_$(date +%Y%m%d).tar.gz /var/www/imsydz-dev/uploads/
```

### 3. Automated Backup
```bash
# Add to crontab
0 2 * * * /home/imsydz/scripts/backup.sh
0 3 * * 0 /home/imsydz/scripts/backup_files.sh
```

## 🚨 Security Checklist

- [ ] Change default admin credentials
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS with valid SSL certificate
- [ ] Set up firewall (UFW)
- [ ] Regular security updates
- [ ] File upload validation
- [ ] Rate limiting
- [ ] CSRF protection
- [ ] SQL injection protection
- [ ] XSS protection

## 📞 Support

Jika mengalami masalah deployment:

1. Check logs: `sudo journalctl -u nginx -f`
2. Check application logs: `sudo supervisorctl tail -f imsydz-dev`
3. Verify configuration: `nginx -t`
4. Contact support: imsyad@imsydz.dev

---

**Happy Deploying!** 🚀


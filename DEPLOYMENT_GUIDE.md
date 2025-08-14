# Django PDF Reader - Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying your Django PDF Reader application to various platforms including Vercel, Railway, Heroku, and traditional VPS.

## Prerequisites
- Git repository with your Django project
- Python 3.8+ installed locally
- Database setup (MySQL/PostgreSQL)
- Environment variables configured

## Platform-Specific Deployment Guides

### 1. Vercel Deployment (Recommended for Frontend-Heavy Apps)

#### Step 1: Prepare Your Project for Vercel

Create a `vercel.json` configuration file in your project root:

```json
{
  "builds": [
    {
      "src": "pdf_reader/wsgi.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "pdf_reader/wsgi.py"
    }
  ],
  "env": {
    "DJANGO_SETTINGS_MODULE": "pdf_reader.settings"
  }
}
```

#### Step 2: Create Vercel-Specific Requirements

Create `requirements-vercel.txt`:

```txt
# Core Django
Django==4.2.7
asgiref==3.9.1
sqlparse==0.5.3
tzdata==2025.2

# Database (Use PostgreSQL for Vercel)
psycopg2-binary==2.9.9

# Static Files
whitenoise==6.6.0

# Environment
python-decouple==3.8

# PDF Processing
PyPDF2==3.0.1
pdfplumber==0.10.3

# AI/NLP (Lighter versions for Vercel)
transformers==4.36.2
torch==2.0.1
sentence-transformers==2.5.1

# Vector Storage
numpy==1.24.4
faiss-cpu==1.7.4

# Security
cryptography==41.0.8
django-cors-headers==4.3.1
```

#### Step 3: Update Settings for Vercel

Create `pdf_reader/vercel_settings.py`:

```python
from .settings import *

# Vercel-specific settings
DEBUG = False
ALLOWED_HOSTS = ['.vercel.app', '.now.sh', 'localhost', '127.0.0.1']

# Database - Use PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DATABASE'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files (use cloud storage in production)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings for production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

#### Step 4: Deploy to Vercel

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```

3. **Deploy:**
   ```bash
   vercel
   ```

4. **Set Environment Variables in Vercel Dashboard:**
   - Go to your project dashboard
   - Navigate to Settings > Environment Variables
   - Add the following variables:
     ```
     SECRET_KEY=your-secret-key
     DEBUG=False
     POSTGRES_DATABASE=your-db-name
     POSTGRES_USER=your-db-user
     POSTGRES_PASSWORD=your-db-password
     POSTGRES_HOST=your-db-host
     POSTGRES_PORT=5432
     ```

### 2. Railway Deployment (Recommended for Full-Stack Apps)

#### Step 1: Prepare for Railway

Create `railway.json`:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn pdf_reader.wsgi:application --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

#### Step 2: Create Railway-Specific Requirements

Create `requirements-railway.txt`:

```txt
# Core Django
Django==4.2.7
asgiref==3.9.1
sqlparse==0.5.3
tzdata==2025.2

# Database
psycopg2-binary==2.9.9

# Production Server
gunicorn==21.2.0
whitenoise==6.6.0

# Environment
python-decouple==3.8

# PDF Processing
PyPDF2==3.0.1
pdfplumber==0.10.3

# AI/NLP
transformers==4.36.2
torch==2.0.1
sentence-transformers==2.5.1

# Vector Storage
numpy==1.24.4
faiss-cpu==1.7.4

# Security
cryptography==41.0.8
django-cors-headers==4.3.1
```

#### Step 3: Deploy to Railway

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway:**
   ```bash
   railway login
   ```

3. **Initialize Railway Project:**
   ```bash
   railway init
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

### 3. Heroku Deployment

#### Step 1: Create Heroku-Specific Files

Create `Procfile`:

```
web: gunicorn pdf_reader.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate
```

Create `runtime.txt`:

```
python-3.11.7
```

#### Step 2: Update Settings for Heroku

Create `pdf_reader/heroku_settings.py`:

```python
from .settings import *
import dj_database_url

# Heroku-specific settings
DEBUG = False
ALLOWED_HOSTS = ['.herokuapp.com', 'localhost', '127.0.0.1']

# Database
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL')
    )
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Media files (use AWS S3 or similar)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

#### Step 3: Deploy to Heroku

1. **Install Heroku CLI:**
   ```bash
   # Windows
   winget install --id=Heroku.HerokuCLI
   ```

2. **Login to Heroku:**
   ```bash
   heroku login
   ```

3. **Create Heroku App:**
   ```bash
   heroku create your-pdf-reader-app
   ```

4. **Add PostgreSQL:**
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

5. **Set Environment Variables:**
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   ```

6. **Deploy:**
   ```bash
   git push heroku main
   ```

### 4. Traditional VPS Deployment (Ubuntu/DigitalOcean)

#### Step 1: Server Setup

1. **Connect to your VPS:**
   ```bash
   ssh root@your-server-ip
   ```

2. **Update system:**
   ```bash
   apt update && apt upgrade -y
   ```

3. **Install dependencies:**
   ```bash
   apt install python3 python3-pip python3-venv nginx mysql-server -y
   ```

#### Step 2: Project Setup

1. **Clone repository:**
   ```bash
   git clone https://github.com/mathivarman/PDF_Reader.git
   cd PDF_Reader
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install requirements:**
   ```bash
   pip install -r requirements.txt
   ```

#### Step 3: Database Setup

1. **Configure MySQL:**
   ```bash
   mysql_secure_installation
   ```

2. **Create database:**
   ```bash
   mysql -u root -p
   CREATE DATABASE pdf_reader;
   CREATE USER 'pdf_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON pdf_reader.* TO 'pdf_user'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
   ```

#### Step 4: Django Configuration

1. **Create .env file:**
   ```bash
   nano .env
   ```

   Add the following:
   ```
   SECRET_KEY=your-secret-key
   DEBUG=False
   ALLOWED_HOSTS=your-domain.com,www.your-domain.com
   DATABASE_URL=mysql://pdf_user:your_password@localhost/pdf_reader
   ```

2. **Run migrations:**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

#### Step 5: Gunicorn Setup

1. **Create gunicorn service:**
   ```bash
   nano /etc/systemd/system/pdf-reader.service
   ```

   Add the following:
   ```ini
   [Unit]
   Description=PDF Reader Gunicorn daemon
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/root/PDF_Reader
   Environment="PATH=/root/PDF_Reader/venv/bin"
   ExecStart=/root/PDF_Reader/venv/bin/gunicorn --workers 3 --bind unix:/root/PDF_Reader/pdf_reader.sock pdf_reader.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

2. **Start and enable service:**
   ```bash
   systemctl start pdf-reader
   systemctl enable pdf-reader
   ```

#### Step 6: Nginx Configuration

1. **Create Nginx config:**
   ```bash
   nano /etc/nginx/sites-available/pdf-reader
   ```

   Add the following:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com www.your-domain.com;

       location = /favicon.ico { access_log off; log_not_found off; }
       
       location /static/ {
           root /root/PDF_Reader;
       }

       location /media/ {
           root /root/PDF_Reader;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/root/PDF_Reader/pdf_reader.sock;
       }
   }
   ```

2. **Enable site:**
   ```bash
   ln -s /etc/nginx/sites-available/pdf-reader /etc/nginx/sites-enabled
   nginx -t
   systemctl restart nginx
   ```

## Environment Variables Setup

Create a `.env` file in your project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=your-database-connection-string

# Security
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# File Upload
MAX_FILE_SIZE=15728640  # 15MB in bytes

# AI/NLP Models
TRANSFORMERS_CACHE=/tmp/transformers_cache
TORCH_HOME=/tmp/torch_cache

# Redis (if using Celery)
REDIS_URL=your-redis-url

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## Post-Deployment Checklist

### 1. Security Verification
- [ ] HTTPS is enabled
- [ ] DEBUG is set to False
- [ ] Secret key is properly configured
- [ ] Database credentials are secure
- [ ] File upload limits are set
- [ ] CSRF protection is enabled

### 2. Performance Optimization
- [ ] Static files are served efficiently
- [ ] Database queries are optimized
- [ ] Caching is configured
- [ ] CDN is set up (optional)

### 3. Monitoring Setup
- [ ] Error logging is configured
- [ ] Performance monitoring is active
- [ ] Health checks are working
- [ ] Backup strategy is in place

### 4. Testing
- [ ] All features work correctly
- [ ] File uploads function properly
- [ ] PDF processing works
- [ ] Search functionality is operational
- [ ] User authentication works

## Troubleshooting Common Issues

### 1. Static Files Not Loading
```bash
python manage.py collectstatic --noinput
```

### 2. Database Connection Issues
- Check database credentials
- Ensure database server is running
- Verify network connectivity

### 3. Permission Errors
```bash
chmod -R 755 /path/to/your/project
chown -R www-data:www-data /path/to/your/project
```

### 4. Memory Issues
- Reduce number of Gunicorn workers
- Optimize database queries
- Use lighter AI models

## Maintenance

### Regular Tasks
1. **Database backups:**
   ```bash
   mysqldump -u username -p database_name > backup.sql
   ```

2. **Log rotation:**
   ```bash
   logrotate /etc/logrotate.d/pdf-reader
   ```

3. **Security updates:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

4. **System updates:**
   ```bash
   apt update && apt upgrade
   ```

## Support and Resources

- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Railway Documentation](https://docs.railway.app/)
- [Heroku Python Documentation](https://devcenter.heroku.com/categories/python-support)

---

**Note:** Choose the deployment platform that best fits your needs:
- **Vercel**: Great for frontend-heavy apps, limited backend processing
- **Railway**: Good for full-stack apps with moderate processing
- **Heroku**: Traditional choice, good for most Django apps
- **VPS**: Full control, best for heavy processing and custom requirements

#!/bin/bash

# Fix Logs Directory Issue
# Run this to fix the missing logs directory

echo "🔧 Fixing Logs Directory Issue..."
echo "================================="

# Get username
USERNAME=$(whoami)
echo "👤 Username: $USERNAME"

# Step 1: Create necessary directories
echo ""
echo "📋 Step 1: Creating necessary directories..."
cd /home/$USERNAME/PDF_Reader

# Create logs directory
mkdir -p logs
mkdir -p media
mkdir -p staticfiles

echo "✅ Created logs, media, and staticfiles directories"

# Step 2: Create .env file
echo ""
echo "📋 Step 2: Creating environment file..."
cat > .env << EOF
# Django Settings
DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production-1234567890abcdef
ALLOWED_HOSTS=$USERNAME.pythonanywhere.com

# Database Settings (PythonAnywhere MySQL)
DB_NAME=$USERNAME\$legal_doc_explainer
DB_USER=$USERNAME
DB_PASSWORD=YOUR_MYSQL_PASSWORD_HERE
DB_HOST=$USERNAME.mysql.pythonanywhere-services.com
DB_PORT=3306

# Security Settings
CSRF_TRUSTED_ORIGINS=https://$USERNAME.pythonanywhere.com
SECURE_SSL_REDIRECT=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True

# AI API Keys (optional)
HUGGINGFACE_TOKEN=your-huggingface-token
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key
EOF

echo "⚠️  IMPORTANT: Edit .env file and update DB_PASSWORD with your MySQL password!"

# Step 3: Activate virtual environment and run Django setup
echo ""
echo "📋 Step 3: Running Django setup..."
source pdf_reader_env/bin/activate

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser
echo "Creating superuser..."
python manage.py createsuperuser --username admin --email admin@example.com --noinput

# Test Django
echo "Testing Django..."
python manage.py check --deploy

echo ""
echo "✅ Logs directory issue fixed!"
echo ""
echo "📋 Next steps:"
echo "1. Edit .env file and update DB_PASSWORD"
echo "2. Go to Web tab in PythonAnywhere"
echo "3. Add a new web app with Manual configuration"
echo "4. Update WSGI file with the provided configuration"
echo "5. Configure static files"
echo "6. Reload web app"
echo ""
echo "🔗 Your app will be available at: https://$USERNAME.pythonanywhere.com"

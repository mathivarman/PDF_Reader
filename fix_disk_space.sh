#!/bin/bash

# Fix Disk Space and Continue Deployment
# Run this on PythonAnywhere to fix the current issue

echo "🔧 Fixing Disk Space Issue..."
echo "============================="

# Get username
USERNAME=$(whoami)
echo "👤 Username: $USERNAME"

# Step 1: Check current disk usage
echo ""
echo "📋 Step 1: Checking disk usage..."
df -h /home/$USERNAME

# Step 2: Clean up any partial installations
echo ""
echo "📋 Step 2: Cleaning up partial installations..."
cd /home/$USERNAME/PDF_Reader

# Remove any partial PyTorch installations
pip uninstall torch torchvision torchaudio -y 2>/dev/null || true

# Step 3: Install basic requirements only
echo ""
echo "📋 Step 3: Installing basic requirements..."
source pdf_reader_env/bin/activate

# Install only essential packages
pip install Django==4.2.7
pip install django-crispy-forms==2.0
pip install crispy-bootstrap5==0.7
pip install mysqlclient==2.1.1
pip install python-decouple==3.8
pip install PyPDF2==3.0.1
pip install pdfplumber==0.9.0

# Step 4: Create .env file
echo ""
echo "📋 Step 4: Creating environment file..."
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

# Step 5: Run Django setup
echo ""
echo "📋 Step 5: Running Django setup..."
python manage.py migrate
python manage.py collectstatic --noinput

# Step 6: Create superuser
echo ""
echo "📋 Step 6: Creating superuser..."
python manage.py createsuperuser --username admin --email admin@example.com --noinput

# Step 7: Test Django
echo ""
echo "📋 Step 7: Testing Django..."
python manage.py check --deploy

echo ""
echo "✅ Fix completed!"
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
echo ""
echo "⚠️  Note: This is a basic version without advanced AI features due to disk space."
echo "   Core PDF upload and basic functionality will work."

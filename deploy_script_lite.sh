#!/bin/bash

# PythonAnywhere Lite Deployment Script
# Optimized for free tier disk space limitations

echo "🚀 Starting PythonAnywhere Lite Deployment..."
echo "============================================="

# Get username from current directory
USERNAME=$(whoami)
echo "👤 Username: $USERNAME"

# Step 1: Clone repository
echo ""
echo "📋 Step 1: Cloning repository..."
if [ -d "PDF_Reader" ]; then
    echo "Repository already exists, pulling latest changes..."
    cd PDF_Reader
    git pull origin master
else
    echo "Cloning repository..."
    git clone https://github.com/mathivarman/PDF_Reader.git
    cd PDF_Reader
fi

# Step 2: Create virtual environment
echo ""
echo "📋 Step 2: Setting up virtual environment..."
if [ -d "pdf_reader_env" ]; then
    echo "Virtual environment already exists, activating..."
    source pdf_reader_env/bin/activate
else
    echo "Creating virtual environment..."
    python3.9 -m venv pdf_reader_env
    source pdf_reader_env/bin/activate
fi

# Step 3: Check disk space
echo ""
echo "📋 Step 3: Checking disk space..."
df -h /home/$USERNAME
echo "Available space:"
df -h /home/$USERNAME | tail -1 | awk '{print $4}'

# Step 4: Install dependencies (lite version)
echo ""
echo "📋 Step 4: Installing dependencies (lite version)..."
echo "Using lite requirements to avoid disk space issues..."

# Try to install lite requirements
if [ -f "requirements-pythonanywhere-lite.txt" ]; then
    echo "Installing lite requirements..."
    pip install -r requirements-pythonanywhere-lite.txt
else
    echo "Lite requirements not found, installing basic requirements..."
    pip install Django==4.2.7 django-crispy-forms==2.0 crispy-bootstrap5==0.7 mysqlclient==2.1.1 python-decouple==3.8 PyPDF2==3.0.1 pdfplumber==0.9.0
fi

# Step 5: Create .env file
echo ""
echo "📋 Step 5: Creating environment file..."
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

# Step 6: Run Django setup
echo ""
echo "📋 Step 6: Running Django setup..."
python manage.py migrate
python manage.py collectstatic --noinput

# Step 7: Create superuser
echo ""
echo "📋 Step 7: Creating superuser..."
echo "Creating admin user with username 'admin' and email 'admin@example.com'..."
python manage.py createsuperuser --username admin --email admin@example.com --noinput

# Step 8: Test Django
echo ""
echo "📋 Step 8: Testing Django..."
python manage.py check --deploy

echo ""
echo "✅ Lite deployment script completed!"
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
echo "⚠️  Note: This is a lite version without PyTorch due to disk space limitations."
echo "   Some AI features may be limited. Consider upgrading to paid plan for full features."
echo ""
echo "📄 See PYTHONANYWHERE_DEPLOYMENT_STEP_BY_STEP.md for detailed instructions"

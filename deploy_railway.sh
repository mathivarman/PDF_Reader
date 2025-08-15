#!/bin/bash

# Railway Deployment Script for PDF Reader
# This script helps prepare your project for Railway deployment

echo "🚀 Railway Deployment Preparation Script"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from your project root."
    exit 1
fi

echo "✅ Found Django project"

# Check git status
echo "📋 Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  You have uncommitted changes. Committing them..."
    git add .
    git commit -m "Prepare for Railway deployment - $(date)"
    echo "✅ Changes committed"
else
    echo "✅ No uncommitted changes"
fi

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push origin master
echo "✅ Pushed to GitHub"

# Create Railway-specific requirements if it doesn't exist
if [ ! -f "requirements-railway.txt" ]; then
    echo "📦 Creating Railway requirements file..."
    cat > requirements-railway.txt << 'EOF'
# Railway Deployment Requirements
Django==4.2.7
python-decouple==3.8
psycopg2-binary==2.9.7
PyPDF2==3.0.1
pdfplumber==0.9.0
scikit-learn==1.3.2
numpy==1.24.3
pandas==2.0.3
Pillow==10.0.1
cryptography==41.0.7
psutil==5.9.6
gunicorn==21.2.0
whitenoise==6.6.0
EOF
    echo "✅ Created requirements-railway.txt"
fi

# Create Procfile if it doesn't exist
if [ ! -f "Procfile" ]; then
    echo "📄 Creating Procfile..."
    echo "web: gunicorn pdf_reader.wsgi:application --bind 0.0.0.0:\$PORT" > Procfile
    echo "✅ Created Procfile"
fi

# Create runtime.txt if it doesn't exist
if [ ! -f "runtime.txt" ]; then
    echo "🐍 Creating runtime.txt..."
    echo "python-3.11.7" > runtime.txt
    echo "✅ Created runtime.txt"
fi

# Generate a secret key
echo "🔑 Generating secret key..."
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
echo "✅ Generated secret key"

echo ""
echo "🎉 Project prepared for Railway deployment!"
echo ""
echo "📋 Next Steps:"
echo "1. Go to https://railway.app"
echo "2. Sign up with GitHub"
echo "3. Click 'New Project'"
echo "4. Select 'Deploy from GitHub repo'"
echo "5. Choose your PDF_Reader repository"
echo "6. Railway will auto-detect Django and deploy"
echo ""
echo "🔧 Environment Variables to set in Railway:"
echo "DEBUG=False"
echo "SECRET_KEY=$SECRET_KEY"
echo "ALLOWED_HOSTS=your-app-name.railway.app"
echo "CSRF_TRUSTED_ORIGINS=https://your-app-name.railway.app"
echo "SECURE_SSL_REDIRECT=True"
echo "CSRF_COOKIE_SECURE=True"
echo "SESSION_COOKIE_SECURE=True"
echo ""
echo "📖 For detailed instructions, see: RAILWAY_DEPLOYMENT_GUIDE.md"
echo ""
echo "�� Happy deploying!"

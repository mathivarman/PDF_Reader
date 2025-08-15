#!/bin/bash

# PythonAnywhere Deployment Script
# Run this on PythonAnywhere's Bash console

echo "🚀 Starting PythonAnywhere Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "manage.py not found. Please run this script from your project root directory."
    exit 1
fi

print_status "Setting up PythonAnywhere environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "pdf_reader_env" ]; then
    print_status "Creating virtual environment..."
    python3.9 -m venv pdf_reader_env
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source pdf_reader_env/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing requirements..."
if [ -f "requirements-pythonanywhere.txt" ]; then
    pip install -r requirements-pythonanywhere.txt
else
    pip install -r requirements-render-lite.txt
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating template..."
    cat > .env << EOF
DEBUG=False
SECRET_KEY=your-secret-key-here-change-this
HUGGINGFACE_TOKEN=your-huggingface-token
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key
EOF
    print_warning "Please edit .env file with your actual API keys"
fi

# Run Django setup
print_status "Running Django migrations..."
python manage.py migrate

# Collect static files
print_status "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed
read -p "Do you want to create a superuser? (y/n): " create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    python manage.py createsuperuser
fi

print_status "✅ PythonAnywhere setup complete!"
print_status ""
print_status "Next steps:"
print_status "1. Go to 'Web' tab in PythonAnywhere"
print_status "2. Add a new web app (Manual configuration)"
print_status "3. Configure WSGI file (see PYTHONANYWHERE_FREE_DEPLOYMENT.md)"
print_status "4. Set up static file mappings"
print_status "5. Reload your web app"
print_status ""
print_status "Your app will be available at: https://YOUR_USERNAME.pythonanywhere.com"

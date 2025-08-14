#!/bin/bash

# Django PDF Reader Deployment Script
# This script helps automate common deployment tasks

echo "🚀 Django PDF Reader Deployment Script"
echo "======================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to generate secret key
generate_secret_key() {
    python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
}

# Function to check prerequisites
check_prerequisites() {
    echo "📋 Checking prerequisites..."
    
    if ! command_exists python3; then
        echo "❌ Python 3 is not installed"
        exit 1
    fi
    
    if ! command_exists pip; then
        echo "❌ pip is not installed"
        exit 1
    fi
    
    if ! command_exists git; then
        echo "❌ Git is not installed"
        exit 1
    fi
    
    echo "✅ Prerequisites check passed"
}

# Function to setup environment
setup_environment() {
    echo "🔧 Setting up environment..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements
    echo "Installing requirements..."
    pip install -r requirements.txt
    
    echo "✅ Environment setup completed"
}

# Function to prepare for deployment
prepare_deployment() {
    echo "📦 Preparing for deployment..."
    
    # Collect static files
    python manage.py collectstatic --noinput
    
    # Run migrations
    python manage.py migrate
    
    # Generate secret key if not exists
    if [ ! -f ".env" ]; then
        echo "Creating .env file..."
        cat > .env << EOF
SECRET_KEY=$(generate_secret_key)
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EOF
        echo "✅ .env file created"
    fi
    
    echo "✅ Deployment preparation completed"
}

# Function to deploy to Vercel
deploy_vercel() {
    echo "🚀 Deploying to Vercel..."
    
    if ! command_exists vercel; then
        echo "Installing Vercel CLI..."
        npm install -g vercel
    fi
    
    # Deploy
    vercel --prod
    
    echo "✅ Vercel deployment completed"
}

# Function to deploy to Railway
deploy_railway() {
    echo "🚂 Deploying to Railway..."
    
    if ! command_exists railway; then
        echo "Installing Railway CLI..."
        npm install -g @railway/cli
    fi
    
    # Deploy
    railway up
    
    echo "✅ Railway deployment completed"
}

# Function to deploy to Heroku
deploy_heroku() {
    echo "🦸 Deploying to Heroku..."
    
    if ! command_exists heroku; then
        echo "Please install Heroku CLI first:"
        echo "Windows: winget install --id=Heroku.HerokuCLI"
        echo "macOS: brew install heroku/brew/heroku"
        echo "Linux: curl https://cli-assets.heroku.com/install.sh | sh"
        exit 1
    fi
    
    # Check if Heroku app exists
    if ! heroku apps:info >/dev/null 2>&1; then
        echo "Creating Heroku app..."
        heroku create
    fi
    
    # Add PostgreSQL if not exists
    if ! heroku addons:info heroku-postgresql >/dev/null 2>&1; then
        echo "Adding PostgreSQL..."
        heroku addons:create heroku-postgresql:mini
    fi
    
    # Deploy
    git push heroku main
    
    echo "✅ Heroku deployment completed"
}

# Function to show deployment options
show_options() {
    echo ""
    echo "Choose deployment platform:"
    echo "1) Vercel (Recommended for frontend-heavy apps)"
    echo "2) Railway (Good for full-stack apps)"
    echo "3) Heroku (Traditional choice)"
    echo "4) Prepare for deployment only"
    echo "5) Exit"
    echo ""
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            check_prerequisites
            setup_environment
            prepare_deployment
            deploy_vercel
            ;;
        2)
            check_prerequisites
            setup_environment
            prepare_deployment
            deploy_railway
            ;;
        3)
            check_prerequisites
            setup_environment
            prepare_deployment
            deploy_heroku
            ;;
        4)
            check_prerequisites
            setup_environment
            prepare_deployment
            ;;
        5)
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Please try again."
            show_options
            ;;
    esac
}

# Main execution
if [ "$1" = "vercel" ]; then
    check_prerequisites
    setup_environment
    prepare_deployment
    deploy_vercel
elif [ "$1" = "railway" ]; then
    check_prerequisites
    setup_environment
    prepare_deployment
    deploy_railway
elif [ "$1" = "heroku" ]; then
    check_prerequisites
    setup_environment
    prepare_deployment
    deploy_heroku
elif [ "$1" = "prepare" ]; then
    check_prerequisites
    setup_environment
    prepare_deployment
else
    show_options
fi

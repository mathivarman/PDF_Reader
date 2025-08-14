@echo off
echo 🆓 Render Free Deployment Script
echo ================================

echo.
echo 📋 Prerequisites Check:
echo ----------------------

:: Check if git is installed
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Git is not installed. Please install Git first.
    echo Download from: https://git-scm.com/download/win
    pause
    exit /b 1
)

:: Check if Python is installed
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python first.
    echo Download from: https://python.org/downloads
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed!

echo.
echo 🔧 Preparing for FREE Render deployment...
echo -----------------------------------------

:: Check if we're in the right directory
if not exist "manage.py" (
    echo ❌ manage.py not found. Please run this script from your Django project root.
    pause
    exit /b 1
)

:: Check if render.yaml exists
if not exist "render.yaml" (
    echo ❌ render.yaml not found. Creating it now...
    (
        echo services:
        echo   - type: web
        echo     name: pdf-reader-demo
        echo     env: python
        echo     plan: free
        echo     buildCommand: pip install -r requirements.txt
        echo     startCommand: gunicorn pdf_reader.wsgi:application
        echo     envVars:
        echo       - key: SECRET_KEY
        echo         generateValue: true
        echo       - key: DEBUG
        echo         value: False
        echo       - key: ALLOWED_HOSTS
        echo         value: .onrender.com
        echo     autoDeploy: true
        echo.
        echo databases:
        echo   - name: pdf-reader-db
        echo     plan: free
    ) > render.yaml
    echo ✅ render.yaml created!
)

:: Generate secret key
echo 🔑 Generating Django secret key...
for /f "delims=" %%i in ('python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"') do set "secret_key=%%i"

:: Create .env file for local reference
if not exist ".env" (
    echo 📝 Creating .env file for reference...
    (
        echo SECRET_KEY=!secret_key!
        echo DEBUG=False
        echo ALLOWED_HOSTS=*.onrender.com
        echo DATABASE_URL=postgresql://... (Render will set this)
    ) > .env
    echo ✅ .env file created!
)

echo.
echo 📦 Preparing files for deployment...
echo -----------------------------------

:: Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

:: Run migrations locally (if possible)
echo 🔄 Running migrations...
python manage.py migrate

echo.
echo 🚀 Ready for FREE Render deployment!
echo ====================================

echo.
echo 📋 Next Steps (100%% FREE):
echo --------------------------
echo 1. Go to https://render.com
echo 2. Sign up with GitHub (FREE)
echo 3. Click "New +"
echo 4. Choose "Web Service"
echo 5. Connect your GitHub repository
echo 6. Select your PDF_Reader repo
echo 7. Configure:
echo    - Name: pdf-reader-demo
echo    - Environment: Python 3
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: gunicorn pdf_reader.wsgi:application
echo 8. Click "Create Web Service"
echo.
echo 🗄️  Add Database (FREE):
echo 1. In dashboard, click "New +"
echo 2. Choose "PostgreSQL"
echo 3. Name: pdf-reader-db
echo 4. Click "Create Database"
echo.
echo 🔧 Environment Variables (Render will auto-set most):
echo    SECRET_KEY=!secret_key!
echo    DEBUG=False
echo    ALLOWED_HOSTS=your-app-name.onrender.com
echo.
echo 🌐 Your FREE demo link will be: https://your-app-name.onrender.com
echo.
echo 📚 For detailed instructions, see: RENDER_FREE_DEPLOYMENT.md
echo.

:: Check if git repository is ready
git status >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Not a git repository. Please initialize git:
    echo    git init
    echo    git add .
    echo    git commit -m "Initial commit"
    echo    git remote add origin YOUR_GITHUB_REPO_URL
    echo    git push -u origin main
) else (
    echo ✅ Git repository detected
    echo 📤 Push to GitHub to trigger Render deployment:
    echo    git add .
    echo    git commit -m "Ready for Render deployment"
    echo    git push origin main
)

echo.
echo 🎉 FREE deployment preparation complete!
echo ========================================
echo.
echo 💡 Render Free Tier Benefits:
echo - 750 hours/month (enough for demo)
echo - PostgreSQL database included
echo - Automatic HTTPS
echo - Custom domains
echo - No credit card required
echo.
pause

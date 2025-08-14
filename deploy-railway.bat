@echo off
echo 🚂 Railway Deployment Script for PDF Reader
echo ===========================================

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
echo 🔧 Preparing for Railway deployment...
echo -------------------------------------

:: Check if we're in the right directory
if not exist "manage.py" (
    echo ❌ manage.py not found. Please run this script from your Django project root.
    pause
    exit /b 1
)

:: Check if railway.json exists
if not exist "railway.json" (
    echo ❌ railway.json not found. Creating it now...
    (
        echo {
        echo   "$schema": "https://railway.app/railway.schema.json",
        echo   "build": {
        echo     "builder": "NIXPACKS"
        echo   },
        echo   "deploy": {
        echo     "startCommand": "python manage.py migrate && gunicorn pdf_reader.wsgi:application --bind 0.0.0.0:$PORT",
        echo     "healthcheckPath": "/",
        echo     "healthcheckTimeout": 100,
        echo     "restartPolicyType": "ON_FAILURE"
        echo   }
        echo }
    ) > railway.json
    echo ✅ railway.json created!
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
        echo ALLOWED_HOSTS=*.railway.app
        echo DATABASE_URL=postgresql://... (Railway will set this)
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
echo 🚀 Ready for Railway deployment!
echo ================================

echo.
echo 📋 Next Steps:
echo --------------
echo 1. Go to https://railway.app
echo 2. Sign up with GitHub
echo 3. Click "New Project"
echo 4. Select "Deploy from GitHub repo"
echo 5. Choose your PDF_Reader repository
echo 6. Click "Deploy Now"
echo.
echo 🔧 After deployment, set these environment variables in Railway:
echo    SECRET_KEY=!secret_key!
echo    DEBUG=False
echo    ALLOWED_HOSTS=*.railway.app
echo.
echo 🌐 Your demo link will be: https://your-app-name.railway.app
echo.
echo 📚 For detailed instructions, see: RAILWAY_DEPLOYMENT.md
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
    echo 📤 Push to GitHub to trigger Railway deployment:
    echo    git add .
    echo    git commit -m "Ready for Railway deployment"
    echo    git push origin main
)

echo.
echo 🎉 Deployment preparation complete!
echo ===================================
pause

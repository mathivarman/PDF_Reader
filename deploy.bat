@echo off
setlocal enabledelayedexpansion

echo 🚀 Django PDF Reader Deployment Script
echo ======================================

:: Function to check if command exists
:check_command
set "command=%~1"
where %command% >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ %command% is not installed
    exit /b 1
)
exit /b 0

:: Function to generate secret key
:generate_secret_key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
exit /b 0

:: Function to check prerequisites
:check_prerequisites
echo 📋 Checking prerequisites...

call :check_command python
if %errorlevel% neq 0 exit /b 1

call :check_command pip
if %errorlevel% neq 0 exit /b 1

call :check_command git
if %errorlevel% neq 0 exit /b 1

echo ✅ Prerequisites check passed
exit /b 0

:: Function to setup environment
:setup_environment
echo 🔧 Setting up environment...

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install requirements
echo Installing requirements...
pip install -r requirements.txt

echo ✅ Environment setup completed
exit /b 0

:: Function to prepare for deployment
:prepare_deployment
echo 📦 Preparing for deployment...

:: Collect static files
python manage.py collectstatic --noinput

:: Run migrations
python manage.py migrate

:: Generate secret key if not exists
if not exist ".env" (
    echo Creating .env file...
    for /f "delims=" %%i in ('python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"') do set "secret_key=%%i"
    (
        echo SECRET_KEY=!secret_key!
        echo DEBUG=False
        echo ALLOWED_HOSTS=localhost,127.0.0.1
        echo DATABASE_URL=sqlite:///db.sqlite3
    ) > .env
    echo ✅ .env file created
)

echo ✅ Deployment preparation completed
exit /b 0

:: Function to deploy to Vercel
:deploy_vercel
echo 🚀 Deploying to Vercel...

call :check_command vercel
if %errorlevel% neq 0 (
    echo Installing Vercel CLI...
    npm install -g vercel
)

:: Deploy
vercel --prod

echo ✅ Vercel deployment completed
exit /b 0

:: Function to deploy to Railway
:deploy_railway
echo 🚂 Deploying to Railway...

call :check_command railway
if %errorlevel% neq 0 (
    echo Installing Railway CLI...
    npm install -g @railway/cli
)

:: Deploy
railway up

echo ✅ Railway deployment completed
exit /b 0

:: Function to deploy to Heroku
:deploy_heroku
echo 🦸 Deploying to Heroku...

call :check_command heroku
if %errorlevel% neq 0 (
    echo Please install Heroku CLI first:
    echo Windows: winget install --id=Heroku.HerokuCLI
    exit /b 1
)

:: Check if Heroku app exists
heroku apps:info >nul 2>&1
if %errorlevel% neq 0 (
    echo Creating Heroku app...
    heroku create
)

:: Add PostgreSQL if not exists
heroku addons:info heroku-postgresql >nul 2>&1
if %errorlevel% neq 0 (
    echo Adding PostgreSQL...
    heroku addons:create heroku-postgresql:mini
)

:: Deploy
git push heroku main

echo ✅ Heroku deployment completed
exit /b 0

:: Function to show deployment options
:show_options
echo.
echo Choose deployment platform:
echo 1) Vercel (Recommended for frontend-heavy apps)
echo 2) Railway (Good for full-stack apps)
echo 3) Heroku (Traditional choice)
echo 4) Prepare for deployment only
echo 5) Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    call :check_prerequisites
    call :setup_environment
    call :prepare_deployment
    call :deploy_vercel
) else if "%choice%"=="2" (
    call :check_prerequisites
    call :setup_environment
    call :prepare_deployment
    call :deploy_railway
) else if "%choice%"=="3" (
    call :check_prerequisites
    call :setup_environment
    call :prepare_deployment
    call :deploy_heroku
) else if "%choice%"=="4" (
    call :check_prerequisites
    call :setup_environment
    call :prepare_deployment
) else if "%choice%"=="5" (
    echo 👋 Goodbye!
    exit /b 0
) else (
    echo ❌ Invalid choice. Please try again.
    call :show_options
)
exit /b 0

:: Main execution
if "%1"=="vercel" (
    call :check_prerequisites
    call :setup_environment
    call :prepare_deployment
    call :deploy_vercel
) else if "%1"=="railway" (
    call :check_prerequisites
    call :setup_environment
    call :prepare_deployment
    call :deploy_railway
) else if "%1"=="heroku" (
    call :check_prerequisites
    call :setup_environment
    call :prepare_deployment
    call :deploy_heroku
) else if "%1"=="prepare" (
    call :check_prerequisites
    call :setup_environment
    call :prepare_deployment
) else (
    call :show_options
)

pause

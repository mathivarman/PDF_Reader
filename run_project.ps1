Write-Host "Starting PDF Reader Project..." -ForegroundColor Green
Write-Host ""

# Activate virtual environment
& ".\pdf_reader_env\Scripts\Activate.ps1"

# Run migrations (if needed)
Write-Host "Running migrations..." -ForegroundColor Yellow
python manage.py migrate

# Start the development server
Write-Host ""
Write-Host "Starting development server..." -ForegroundColor Green
Write-Host "The application will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
python manage.py runserver

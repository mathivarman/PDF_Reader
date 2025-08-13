@echo off
echo Starting PDF Reader Project...
echo.

REM Activate virtual environment
call pdf_reader_env\Scripts\activate

REM Run migrations (if needed)
echo Running migrations...
python manage.py migrate

REM Start the development server
echo.
echo Starting development server...
echo The application will be available at: http://127.0.0.1:8000
echo Press Ctrl+C to stop the server
echo.
python manage.py runserver

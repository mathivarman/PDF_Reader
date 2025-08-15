# PDF Reader

A Django-based web application for reading and managing PDF files with a modern Bootstrap interface and MySQL database.

## Tech Stack

- **Backend**: Python 3.x, Django 4.2.7
- **Database**: MySQL
- **Frontend**: Bootstrap 5
- **Additional**: Django Crispy Forms, Pillow for image processing

## Environment Setup

### Prerequisites

1. Python 3.8 or higher
2. MySQL Server
3. Git

### Installation Steps

1. **Clone the repository** (if applicable)
   ```bash
   git clone <repository-url>
   cd pdf-reader
   ```

2. **Activate the virtual environment**
   ```bash
   # On Windows
   pdf_reader_env\Scripts\activate
   
   # On macOS/Linux
   source pdf_reader_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MySQL database**
   - Create a MySQL database named `pdf_reader_db`
   - Update database settings in `settings.py` if needed

5. **Run Django migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser** (optional)
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
pdf_reader/
├── manage.py
├── requirements.txt
├── README.md
├── pdf_reader_env/          # Virtual environment
└── pdf_reader/              # Django project
    ├── __init__.py
    ├── settings.py
    ├── urls.py
    ├── wsgi.py
    └── asgi.py
```

## Features (Planned)

- PDF file upload and storage
- PDF viewing and reading interface
- User authentication and authorization
- PDF metadata extraction
- Search functionality
- Responsive Bootstrap UI

## Development

The project is now fully set up and ready to run! 

### Quick Start

1. **Run the project** (choose one):
   ```bash
   # Windows Batch
   run_project.bat
   
   # PowerShell
   .\run_project.ps1
   
   # Manual
   pdf_reader_env\Scripts\activate
   python manage.py runserver
   ```

2. **Open your browser** and go to: http://127.0.0.1:8000

### Current Features

- ✅ Beautiful Bootstrap 5 responsive design
- ✅ Modern hero section with feature cards
- ✅ Navigation and footer
- ✅ Django admin interface
- ✅ Static and media file handling
- ✅ Crispy Forms integration

### Next Steps

- PDF upload functionality
- PDF viewer implementation
- User authentication
- Database models for PDF storage
- Search functionality

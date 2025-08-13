"""
Database configuration for AI Legal Document Explainer.
Supports both development (SQLite) and production (MySQL) environments.
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

def get_database_config():
    """
    Get database configuration based on environment.
    Returns appropriate database settings for development or production.
    """
    
    # Force SQLite for now to avoid MySQL issues
    # DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Always use SQLite for development
    return {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
            'OPTIONS': {
                'timeout': 20,  # SQLite timeout
            }
        }
    }

# Database connection details for reference
DATABASE_INFO = {
    'development': {
        'type': 'SQLite',
        'file': str(BASE_DIR / 'db.sqlite3'),
        'description': 'Local SQLite database for development',
        'advantages': [
            'No setup required',
            'File-based storage',
            'Perfect for development',
            'No external dependencies'
        ],
        'limitations': [
            'Not suitable for production',
            'Limited concurrent connections',
            'No advanced features'
        ]
    },
    'production': {
        'type': 'MySQL',
        'description': 'MySQL database for production',
        'environment_variables': {
            'DB_NAME': 'Database name (default: legal_doc_explainer)',
            'DB_USER': 'Database username (default: root)',
            'DB_PASSWORD': 'Database password',
            'DB_HOST': 'Database host (default: localhost)',
            'DB_PORT': 'Database port (default: 3306)',
        },
        'advantages': [
            'High performance',
            'ACID compliance',
            'Concurrent connections',
            'Advanced features',
            'Scalable'
        ],
        'setup_requirements': [
            'MySQL server installed',
            'Database created',
            'User with appropriate permissions',
            'Environment variables configured'
        ]
    }
}

def get_database_status():
    """
    Get current database status and connection details.
    Useful for debugging and monitoring.
    """
    from django.conf import settings
    from django.db import connection
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            connection_status = "Connected"
    except Exception as e:
        connection_status = f"Error: {str(e)}"
    
    db_config = settings.DATABASES['default']
    
    return {
        'engine': db_config['ENGINE'],
        'name': db_config.get('NAME', 'N/A'),
        'host': db_config.get('HOST', 'N/A'),
        'port': db_config.get('PORT', 'N/A'),
        'user': db_config.get('USER', 'N/A'),
        'connection_status': connection_status,
        'debug_mode': settings.DEBUG,
    }

def print_database_info():
    """
    Print database configuration information.
    Useful for debugging and setup verification.
    """
    print("=" * 60)
    print("AI Legal Document Explainer - Database Configuration")
    print("=" * 60)
    
    status = get_database_status()
    
    print(f"\n📊 Current Database Status:")
    print(f"   Engine: {status['engine']}")
    print(f"   Name: {status['name']}")
    print(f"   Host: {status['host']}")
    print(f"   Port: {status['port']}")
    print(f"   User: {status['user']}")
    print(f"   Status: {status['connection_status']}")
    print(f"   Debug Mode: {status['debug_mode']}")
    
    print(f"\n🔧 Environment Configuration:")
    if status['debug_mode']:
        print("   Using SQLite for development")
        print("   Database file: db.sqlite3")
    else:
        print("   Using MySQL for production")
        print("   Environment variables required:")
        for var, desc in DATABASE_INFO['production']['environment_variables'].items():
            print(f"     {var}: {desc}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    print_database_info()

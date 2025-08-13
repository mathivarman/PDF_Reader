#!/usr/bin/env python3
"""
Script to reset the database and create all tables fresh.
This will delete the existing database and create a new one with all tables.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pdf_reader.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.conf import settings
import shutil

def reset_database():
    """Reset the database by deleting the SQLite file and recreating all tables."""
    
    print("🔄 Resetting Database...")
    
    # Get the database file path
    db_path = Path(settings.DATABASES['default']['NAME'])
    
    # Check if we're using SQLite
    if 'sqlite' in settings.DATABASES['default']['ENGINE']:
        print(f"📁 Using SQLite database: {db_path}")
        
        # Delete the existing database file if it exists
        if db_path.exists():
            print(f"🗑️  Deleting existing database: {db_path}")
            db_path.unlink()
        
        # Create migrations
        print("📝 Creating migrations...")
        execute_from_command_line(['manage.py', 'makemigrations', 'main'])
        
        # Run migrations
        print("🚀 Running migrations...")
        execute_from_command_line(['manage.py', 'migrate'])
        
        # Create superuser (optional)
        print("✅ Database reset complete!")
        print("\n🎉 You can now:")
        print("   1. Run: python manage.py runserver")
        print("   2. Upload PDF documents")
        print("   3. Test all functionality")
        
    else:
        print("❌ Not using SQLite. Please set DEBUG=True in settings.py")
        print("Current database engine:", settings.DATABASES['default']['ENGINE'])

if __name__ == "__main__":
    reset_database()

#!/usr/bin/env python3
"""
Database Management Script for AI Legal Document Explainer
Provides utilities for database setup, status checking, and management.
"""

import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(project_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pdf_reader.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from pdf_reader.database import print_database_info, DATABASE_INFO

def show_database_status():
    """Show current database status and configuration."""
    print_database_info()

def show_database_info():
    """Show detailed database information."""
    print("=" * 80)
    print("AI Legal Document Explainer - Database Information")
    print("=" * 80)
    
    for environment, info in DATABASE_INFO.items():
        print(f"\n🔧 {environment.upper()} ENVIRONMENT:")
        print(f"   Type: {info['type']}")
        print(f"   Description: {info['description']}")
        
        if environment == 'development':
            print(f"   File: {info['file']}")
        
        print(f"\n   ✅ Advantages:")
        for advantage in info['advantages']:
            print(f"      • {advantage}")
        
        if 'limitations' in info:
            print(f"\n   ⚠️  Limitations:")
            for limitation in info['limitations']:
                print(f"      • {limitation}")
        
        if 'environment_variables' in info:
            print(f"\n   🔑 Environment Variables:")
            for var, desc in info['environment_variables'].items():
                print(f"      {var}: {desc}")
        
        if 'setup_requirements' in info:
            print(f"\n   📋 Setup Requirements:")
            for requirement in info['setup_requirements']:
                print(f"      • {requirement}")
    
    print("\n" + "=" * 80)

def test_database_connection():
    """Test database connection and show results."""
    print("🔍 Testing Database Connection...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result and result[0] == 1:
                print("✅ Database connection successful!")
                return True
            else:
                print("❌ Database connection failed!")
                return False
    except Exception as e:
        print(f"❌ Database connection error: {str(e)}")
        return False

def run_migrations():
    """Run database migrations."""
    print("🔄 Running database migrations...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration error: {str(e)}")
        return False

def create_superuser():
    """Create a superuser account."""
    print("👤 Creating superuser account...")
    try:
        execute_from_command_line(['manage.py', 'createsuperuser'])
        print("✅ Superuser created successfully!")
        return True
    except Exception as e:
        print(f"❌ Superuser creation error: {str(e)}")
        return False

def show_help():
    """Show help information."""
    print("=" * 60)
    print("Database Management Commands")
    print("=" * 60)
    print("\nAvailable commands:")
    print("  status     - Show current database status")
    print("  info       - Show detailed database information")
    print("  test       - Test database connection")
    print("  migrate    - Run database migrations")
    print("  superuser  - Create superuser account")
    print("  help       - Show this help message")
    print("\nUsage: python manage_db.py <command>")
    print("\nExamples:")
    print("  python manage_db.py status")
    print("  python manage_db.py migrate")
    print("  python manage_db.py test")

def main():
    """Main function to handle command line arguments."""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        show_database_status()
    elif command == 'info':
        show_database_info()
    elif command == 'test':
        test_database_connection()
    elif command == 'migrate':
        run_migrations()
    elif command == 'superuser':
        create_superuser()
    elif command == 'help':
        show_help()
    else:
        print(f"❌ Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()

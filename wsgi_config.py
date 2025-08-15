# PythonAnywhere WSGI Configuration
# Copy this content to your WSGI file in PythonAnywhere Web tab

import os
import sys

# Add your project directory to Python path
path = '/home/YOUR_USERNAME/PDF_Reader'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'pdf_reader.production_settings'

# Activate virtual environment
activate_this = '/home/YOUR_USERNAME/PDF_Reader/pdf_reader_env/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Instructions:
# 1. Replace YOUR_USERNAME with your actual PythonAnywhere username
# 2. Copy this content to your WSGI file in the Web tab
# 3. Make sure the paths match your actual project location

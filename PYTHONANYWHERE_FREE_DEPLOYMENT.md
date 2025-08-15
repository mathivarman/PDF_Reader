# PythonAnywhere Free Deployment Guide

PythonAnywhere is one of the best free hosting platforms for Django projects. It offers:
- **Free tier**: 512MB RAM, 1GB storage, 1 web app
- **Python-specific**: Optimized for Python/Django
- **Easy setup**: Web-based interface
- **Reliable**: No compilation issues like other platforms

## Prerequisites

1. **PythonAnywhere Account**: Sign up at [pythonanywhere.com](https://www.pythonanywhere.com)
2. **GitHub Repository**: Your code should be on GitHub
3. **Free API Keys** (optional but recommended):
   - Hugging Face: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
   - OpenAI: [platform.openai.com/api-keys](https://platform.openai.com/api-keys) (free tier)
   - Google: [console.cloud.google.com](https://console.cloud.google.com) (Gemini API)

## Step-by-Step Deployment

### 1. Create PythonAnywhere Account

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Click "Create a Beginner account" (free)
3. Choose a username (this will be your subdomain)
4. Verify your email

### 2. Clone Your Repository

1. **Open Bash Console**:
   - Log into PythonAnywhere
   - Go to "Consoles" tab
   - Click "Bash" to open a new console

2. **Clone your repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   cd YOUR_REPO_NAME
   ```

### 3. Set Up Virtual Environment

```bash
# Create virtual environment
python3.9 -m venv pdf_reader_env

# Activate virtual environment
source pdf_reader_env/bin/activate

# Install requirements
pip install -r requirements-render-lite.txt
```

### 4. Configure Database

PythonAnywhere free tier includes MySQL. Let's set it up:

1. **Go to "Databases" tab** in PythonAnywhere
2. **Create MySQL database**:
   - Database name: `legal_doc_explainer`
   - Username: (auto-generated)
   - Password: (auto-generated)

3. **Update settings**:
   ```bash
   # In your virtual environment
   nano pdf_reader/settings.py
   ```

   Add this database configuration:
   ```python
   # Database configuration for PythonAnywhere
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'YOUR_USERNAME$legal_doc_explainer',
           'USER': 'YOUR_USERNAME',
           'PASSWORD': 'YOUR_MYSQL_PASSWORD',
           'HOST': 'YOUR_USERNAME.mysql.pythonanywhere-services.com',
           'PORT': '3306',
       }
   }
   ```

### 5. Set Environment Variables

1. **Go to "Files" tab**
2. **Navigate to your project directory**
3. **Create `.env` file**:
   ```bash
   nano .env
   ```

   Add your environment variables:
   ```env
   DEBUG=False
   SECRET_KEY=your-secret-key-here
   HUGGINGFACE_TOKEN=your-huggingface-token
   OPENAI_API_KEY=your-openai-key
   GOOGLE_API_KEY=your-google-key
   ```

### 6. Run Django Setup

```bash
# Make sure virtual environment is activated
source pdf_reader_env/bin/activate

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 7. Configure Web App

1. **Go to "Web" tab** in PythonAnywhere
2. **Click "Add a new web app"**
3. **Choose configuration**:
   - Domain: `YOUR_USERNAME.pythonanywhere.com`
   - Framework: Manual configuration
   - Python version: 3.9

4. **Set up WSGI file**:
   - Click on the WSGI configuration file link
   - Replace the content with:

```python
import os
import sys

# Add your project directory to Python path
path = '/home/YOUR_USERNAME/YOUR_REPO_NAME'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'pdf_reader.settings'

# Activate virtual environment
activate_this = '/home/YOUR_USERNAME/YOUR_REPO_NAME/pdf_reader_env/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

# Import Django application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 8. Configure Static Files

1. **In "Web" tab**, scroll down to "Static files"
2. **Add static file mappings**:
   - URL: `/static/`
   - Directory: `/home/YOUR_USERNAME/YOUR_REPO_NAME/staticfiles/`
   - URL: `/media/`
   - Directory: `/home/YOUR_USERNAME/YOUR_REPO_NAME/media/`

### 9. Reload Web App

1. **Click "Reload" button** in the Web tab
2. **Wait for reload to complete**

### 10. Test Your Application

Visit: `https://YOUR_USERNAME.pythonanywhere.com`

## Troubleshooting

### Common Issues:

1. **Import Error: No module named 'django'**
   - Make sure virtual environment is activated in WSGI file
   - Check that requirements are installed

2. **Database Connection Error**
   - Verify database credentials in settings.py
   - Check that MySQL database is created

3. **Static Files Not Loading**
   - Run `python manage.py collectstatic`
   - Check static file mappings in Web tab

4. **500 Internal Server Error**
   - Check error logs in "Web" tab
   - Verify all environment variables are set

### Viewing Logs:

1. **Go to "Web" tab**
2. **Click "Error log"** to see detailed error messages
3. **Click "Server log"** to see general server logs

## Free Tier Limitations

- **CPU**: Limited to 100 seconds per day
- **RAM**: 512MB
- **Storage**: 1GB
- **Custom domains**: Not available (use subdomain)
- **HTTPS**: Included
- **Database**: MySQL included

## Upgrading (Optional)

If you need more resources:
- **Hacker plan**: $5/month - More CPU, RAM, and storage
- **Developer plan**: $12/month - Even more resources
- **Professional plan**: $99/month - Production-ready

## Demo Link Format

Your demo will be available at:
`https://YOUR_USERNAME.pythonanywhere.com`

## Next Steps

1. **Test all features**: Upload PDF, ask questions
2. **Monitor usage**: Check CPU usage in "Account" tab
3. **Set up monitoring**: Add error tracking if needed
4. **Optimize**: If hitting limits, consider upgrading

## Advantages of PythonAnywhere

✅ **Python-native**: No compilation issues
✅ **Easy setup**: Web-based interface
✅ **Reliable**: Stable hosting
✅ **Free database**: MySQL included
✅ **Good documentation**: Extensive help
✅ **Community support**: Active forums

This is one of the best free hosting options for Django projects! 🚀

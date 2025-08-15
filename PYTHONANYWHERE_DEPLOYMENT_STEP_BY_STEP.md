# PythonAnywhere Deployment - Step by Step Guide

## 🚀 Complete Deployment Guide from Scratch

This guide will walk you through deploying your PDF Reader project to PythonAnywhere free tier, starting from zero.

---

## 📋 Prerequisites

### 1. **PythonAnywhere Account**
- Go to [pythonanywhere.com](https://www.pythonanywhere.com)
- Click "Create a Beginner account" (free)
- Choose a username (this will be your subdomain)
- Verify your email

### 2. **GitHub Repository**
- Your code should be on GitHub at: `https://github.com/mathivarman/PDF_Reader.git`

### 3. **Free API Keys** (Optional but Recommended)
- **Hugging Face**: [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)
- **OpenAI**: [platform.openai.com/api-keys](https://platform.openai.com/api-keys) (free tier)
- **Google**: [console.cloud.google.com](https://console.cloud.google.com) (Gemini API)

---

## 🎯 Step-by-Step Deployment

### **Step 1: Access PythonAnywhere**

1. **Log into PythonAnywhere**
   - Go to [pythonanywhere.com](https://www.pythonanywhere.com)
   - Sign in with your account

2. **Navigate to Dashboard**
   - You'll see your dashboard with various tabs

### **Step 2: Clone Your Repository**

1. **Open Bash Console**
   - Click on "Consoles" tab
   - Click "Bash" to open a new console

2. **Clone Repository**
   ```bash
   git clone https://github.com/mathivarman/PDF_Reader.git
   cd PDF_Reader
   ```

3. **Verify Files**
   ```bash
   ls -la
   ```
   You should see your project files including `manage.py`, `pdf_reader/`, `main/`, etc.

### **Step 3: Set Up Virtual Environment**

1. **Create Virtual Environment**
   ```bash
   python3.9 -m venv pdf_reader_env
   ```

2. **Activate Virtual Environment**
   ```bash
   source pdf_reader_env/bin/activate
   ```

3. **Verify Activation**
   ```bash
   which python
   ```
   Should show: `/home/YOUR_USERNAME/PDF_Reader/pdf_reader_env/bin/python`

### **Step 4: Install Dependencies**

1. **Install Requirements**
   ```bash
   pip install -r requirements-pythonanywhere-optimized.txt
   ```

2. **Verify Installation**
   ```bash
   python -c "import django; print(django.get_version())"
   ```
   Should show Django version (4.2.7)

### **Step 5: Set Up Database**

1. **Go to Databases Tab**
   - Click "Databases" tab in PythonAnywhere
   - You'll see your MySQL database details

2. **Note Database Information**
   - Database name: `YOUR_USERNAME$legal_doc_explainer`
   - Username: `YOUR_USERNAME`
   - Password: (shown in the Databases tab)
   - Host: `YOUR_USERNAME.mysql.pythonanywhere-services.com`

### **Step 6: Configure Environment Variables**

1. **Create .env File**
   ```bash
   nano .env
   ```

2. **Add Environment Variables**
   ```env
   # Django Settings
   DEBUG=False
   SECRET_KEY=your-super-secret-key-change-this-in-production-1234567890abcdef
   ALLOWED_HOSTS=YOUR_USERNAME.pythonanywhere.com

   # Database Settings (PythonAnywhere MySQL)
   DB_NAME=YOUR_USERNAME$legal_doc_explainer
   DB_USER=YOUR_USERNAME
   DB_PASSWORD=YOUR_MYSQL_PASSWORD
   DB_HOST=YOUR_USERNAME.mysql.pythonanywhere-services.com
   DB_PORT=3306

   # Security Settings
   CSRF_TRUSTED_ORIGINS=https://YOUR_USERNAME.pythonanywhere.com
   SECURE_SSL_REDIRECT=True
   CSRF_COOKIE_SECURE=True
   SESSION_COOKIE_SECURE=True

   # AI API Keys (optional)
   HUGGINGFACE_TOKEN=your-huggingface-token
   OPENAI_API_KEY=your-openai-key
   GOOGLE_API_KEY=your-google-key
   ```

3. **Save and Exit**
   - Press `Ctrl + X`
   - Press `Y` to confirm
   - Press `Enter` to save

### **Step 7: Run Django Setup**

1. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

2. **Create Superuser** (Optional)
   ```bash
   python manage.py createsuperuser
   ```

3. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

4. **Test Django**
   ```bash
   python manage.py check --deploy
   ```

### **Step 8: Configure Web App**

1. **Go to Web Tab**
   - Click "Web" tab in PythonAnywhere
   - Click "Add a new web app"

2. **Choose Configuration**
   - Domain: `YOUR_USERNAME.pythonanywhere.com`
   - Framework: **Manual configuration**
   - Python version: **3.9**

3. **Set up WSGI File**
   - Click on the WSGI configuration file link
   - Replace the content with:

```python
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
```

### **Step 9: Configure Static Files**

1. **In Web Tab**
   - Scroll down to "Static files" section

2. **Add Static File Mappings**
   - **URL**: `/static/`
   - **Directory**: `/home/YOUR_USERNAME/PDF_Reader/staticfiles/`
   
   - **URL**: `/media/`
   - **Directory**: `/home/YOUR_USERNAME/PDF_Reader/media/`

### **Step 10: Reload Web App**

1. **Click Reload Button**
   - In the Web tab, click the "Reload" button
   - Wait for the reload to complete

2. **Check Status**
   - The status should show "Running"

### **Step 11: Test Your Application**

1. **Visit Your Site**
   - Go to: `https://YOUR_USERNAME.pythonanywhere.com`
   - You should see your PDF Reader application

2. **Test Features**
   - Try uploading a PDF
   - Test the Q&A functionality
   - Check if all features work

---

## 🔧 Troubleshooting

### **Common Issues and Solutions:**

#### **1. Import Error: No module named 'django'**
```bash
# Solution: Make sure virtual environment is activated
source pdf_reader_env/bin/activate
pip install -r requirements-pythonanywhere-optimized.txt
```

#### **2. Database Connection Error**
```bash
# Solution: Check database credentials in .env file
# Make sure DB_NAME, DB_USER, DB_PASSWORD, DB_HOST are correct
```

#### **3. Static Files Not Loading**
```bash
# Solution: Run collectstatic again
python manage.py collectstatic --noinput
# Check static file mappings in Web tab
```

#### **4. 500 Internal Server Error**
- **Check Error Logs**: Go to Web tab → Click "Error log"
- **Check Server Logs**: Go to Web tab → Click "Server log"
- **Verify Environment Variables**: Make sure .env file is correct

#### **5. Memory Issues**
```bash
# Solution: Check memory usage
# PythonAnywhere free tier has 512MB RAM limit
# Consider using lighter models or upgrading
```

### **Viewing Logs:**

1. **Go to "Web" tab**
2. **Click "Error log"** to see detailed error messages
3. **Click "Server log"** to see general server logs

---

## 📊 PythonAnywhere Free Tier Limits

- **CPU**: Limited to 100 seconds per day
- **RAM**: 512MB
- **Storage**: 1GB
- **Custom domains**: Not available (use subdomain)
- **HTTPS**: Included
- **Database**: MySQL included

---

## 🎉 Success Checklist

- [ ] PythonAnywhere account created
- [ ] Repository cloned successfully
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Database configured
- [ ] Environment variables set
- [ ] Django migrations applied
- [ ] Static files collected
- [ ] Web app configured
- [ ] WSGI file updated
- [ ] Static files mapped
- [ ] Web app reloaded
- [ ] Application accessible at your URL
- [ ] All features working correctly

---

## 🔗 Your Demo Link

Your application will be available at:
`https://YOUR_USERNAME.pythonanywhere.com`

---

## 📞 Support

If you encounter issues:
1. Check the error logs in PythonAnywhere
2. Verify all steps were completed correctly
3. Ensure all environment variables are set
4. Check PythonAnywhere documentation

---

**🎯 You're now ready to deploy! Follow these steps carefully and your PDF Reader will be live on PythonAnywhere!**

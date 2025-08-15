# 🚀 Railway Deployment Guide for PDF Reader

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ Your PDF Reader project on GitHub
- ✅ A GitHub account
- ✅ A Railway account (free)

---

## 🎯 Step-by-Step Deployment

### **Step 1: Prepare Your Project**

First, let's make sure your project is ready for Railway deployment:

```bash
# 1. Check your current directory
pwd

# 2. Make sure all changes are committed
git status
git add .
git commit -m "Prepare for Railway deployment"
git push origin master
```

### **Step 2: Create Railway Account**

1. **Go to Railway**: Visit [railway.app](https://railway.app)
2. **Sign Up**: Click "Sign Up" and choose "Continue with GitHub"
3. **Authorize**: Allow Railway to access your GitHub repositories
4. **Verify Email**: Check your email and verify your account

### **Step 3: Deploy Your Project**

1. **Dashboard**: After signing in, you'll see the Railway dashboard
2. **New Project**: Click "New Project"
3. **Deploy from GitHub**: Select "Deploy from GitHub repo"
4. **Select Repository**: Choose your `PDF_Reader` repository
5. **Auto-Detect**: Railway will automatically detect it's a Django project
6. **Deploy**: Click "Deploy" and wait for the build to complete

### **Step 4: Configure Environment Variables**

Once deployed, you need to set up your environment variables:

1. **Go to Variables Tab**: In your Railway project dashboard
2. **Add Variables**: Click "New Variable" and add these:

```
DEBUG=False
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://... (Railway auto-sets this)
ALLOWED_HOSTS=your-app-name.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app-name.railway.app
SECURE_SSL_REDIRECT=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
```

### **Step 5: Set Up Database**

1. **Add Database**: In Railway dashboard, click "New"
2. **Select PostgreSQL**: Choose "PostgreSQL" from the options
3. **Connect**: Railway will automatically connect it to your app
4. **Environment Variable**: The `DATABASE_URL` will be automatically set

### **Step 6: Configure Django Settings**

Railway will automatically detect Django, but you may need to update your settings:

1. **Check Settings**: Make sure your `settings.py` can handle PostgreSQL
2. **Static Files**: Railway handles static files automatically
3. **Database**: Railway sets up the database connection automatically

### **Step 7: Run Migrations**

1. **Go to Deployments**: In your Railway dashboard
2. **Latest Deployment**: Click on your latest deployment
3. **View Logs**: Check the logs to see if migrations ran automatically
4. **Manual Migration** (if needed):
   ```bash
   # In Railway shell or deployment logs
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py createsuperuser
   ```

### **Step 8: Test Your Application**

1. **Visit Your App**: Go to your Railway app URL
2. **Test Features**: Try uploading a PDF, searching, etc.
3. **Check Logs**: Monitor the logs for any errors

---

## 🔧 Configuration Files

### **requirements.txt for Railway**

Create or update your `requirements.txt`:

```txt
# Core Django
Django==4.2.7
python-decouple==3.8

# Database
psycopg2-binary==2.9.7

# PDF Processing
PyPDF2==3.0.1
pdfplumber==0.9.0

# Basic AI/ML
scikit-learn==1.3.2
numpy==1.24.3
pandas==2.0.3

# Image Processing
Pillow==10.0.1

# Security
cryptography==41.0.7
psutil==5.9.6

# Production Server
gunicorn==21.2.0
whitenoise==6.6.0
```

### **Procfile for Railway**

Create a `Procfile` in your project root:

```
web: gunicorn pdf_reader.wsgi:application --bind 0.0.0.0:$PORT
```

### **runtime.txt for Railway**

Create a `runtime.txt` file:

```
python-3.11.7
```

---

## 🚨 Troubleshooting

### **Common Issues and Solutions**

#### **1. Build Fails**
- **Check Logs**: Look at the build logs in Railway dashboard
- **Requirements**: Make sure all packages in `requirements.txt` are compatible
- **Python Version**: Ensure `runtime.txt` specifies a supported Python version

#### **2. Database Connection Issues**
- **Check DATABASE_URL**: Verify the environment variable is set correctly
- **Install psycopg2**: Make sure `psycopg2-binary` is in requirements.txt
- **Run Migrations**: Ensure migrations are applied

#### **3. Static Files Not Loading**
- **Collect Static**: Run `python manage.py collectstatic --noinput`
- **Whitenoise**: Make sure Whitenoise is configured in settings
- **Check Settings**: Verify `STATIC_ROOT` and `STATIC_URL` are set correctly

#### **4. Environment Variables Not Working**
- **Check Names**: Ensure variable names match exactly (case-sensitive)
- **Restart App**: Redeploy after adding new environment variables
- **Check Logs**: Look for errors in the application logs

#### **5. App Crashes on Startup**
- **Check Logs**: Railway provides detailed error logs
- **Test Locally**: Make sure the app runs locally first
- **Debug Mode**: Temporarily set `DEBUG=True` to see detailed errors

---

## 📊 Monitoring and Maintenance

### **Railway Dashboard Features**

1. **Deployments**: View all deployment history
2. **Logs**: Real-time application logs
3. **Metrics**: CPU, memory, and network usage
4. **Variables**: Manage environment variables
5. **Domains**: Custom domain configuration

### **Useful Commands**

```bash
# View logs
railway logs

# Open shell
railway shell

# Run commands
railway run python manage.py migrate

# Check status
railway status
```

---

## 💰 Free Tier Limits

### **Railway Free Tier**
- **$5 credit monthly**: Usually sufficient for small projects
- **Auto-sleep**: Apps sleep after inactivity to save resources
- **Wake on request**: Apps wake up automatically when accessed
- **Database**: PostgreSQL included in free tier

### **Cost Optimization**
- **Monitor usage**: Check your usage in Railway dashboard
- **Optimize requirements**: Remove unnecessary packages
- **Use lite versions**: Consider lighter alternatives for heavy libraries

---

## 🎉 Success Checklist

- ✅ Project deployed to Railway
- ✅ Database connected and migrations applied
- ✅ Environment variables configured
- ✅ Static files collected
- ✅ Superuser created
- ✅ Application accessible via Railway URL
- ✅ PDF upload and processing working
- ✅ Search functionality working
- ✅ No errors in logs

---

## 🔗 Your Live Application

Once deployed, your PDF Reader will be available at:
```
https://your-app-name.railway.app
```

**Share this URL with others to showcase your project!** 🌍

---

## 📞 Need Help?

If you encounter issues:

1. **Check Railway Logs**: Always start with the deployment logs
2. **Railway Documentation**: Visit [docs.railway.app](https://docs.railway.app)
3. **Community**: Join Railway Discord for community support
4. **GitHub Issues**: Check if others have similar issues

**Happy Deploying! 🚀**

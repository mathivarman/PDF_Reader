# 🚀 Railway Quick Start Guide

## ⚡ Deploy in 5 Minutes!

Your PDF Reader project is now ready for Railway deployment. Here's the quick start:

---

## 🎯 Step 1: Deploy to Railway

1. **Go to Railway**: [railway.app](https://railway.app)
2. **Sign Up**: Click "Sign Up" → "Continue with GitHub"
3. **New Project**: Click "New Project"
4. **Deploy from GitHub**: Select "Deploy from GitHub repo"
5. **Choose Repository**: Select your `PDF_Reader` repository
6. **Wait**: Railway will auto-detect Django and deploy

---

## 🔧 Step 2: Configure Environment Variables

In Railway dashboard → Variables tab, add these:

```
DEBUG=False
SECRET_KEY=pwf1qti+76bovup5y1*4-js=yex9=guzs5rggu$e%6bn4zi83d
ALLOWED_HOSTS=your-app-name.railway.app
CSRF_TRUSTED_ORIGINS=https://your-app-name.railway.app
SECURE_SSL_REDIRECT=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
```

---

## 🗄️ Step 3: Add Database

1. **Add PostgreSQL**: In Railway dashboard → "New" → "PostgreSQL"
2. **Connect**: Railway auto-connects it to your app
3. **DATABASE_URL**: Automatically set by Railway

---

## ⚙️ Step 4: Run Django Setup

In Railway dashboard → Deployments → Latest deployment → Logs, run:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py createcachetable
```

---

## 🎉 Step 5: Your App is Live!

Visit: `https://your-app-name.railway.app`

**Your PDF Reader is now live and accessible worldwide!** 🌍

---

## 📋 What's Already Configured

✅ **Railway Settings**: `pdf_reader/railway_settings.py`  
✅ **Requirements**: `requirements-railway.txt` (optimized)  
✅ **Procfile**: Configured for Railway  
✅ **Runtime**: Python 3.11.7  
✅ **Database**: PostgreSQL support  
✅ **Static Files**: Whitenoise configured  
✅ **Security**: HTTPS and security headers  

---

## 🚨 If You Need Help

- **Check Logs**: Railway dashboard → Deployments → Logs
- **Documentation**: [RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md)
- **Checklist**: [RAILWAY_DEPLOYMENT_CHECKLIST.md](RAILWAY_DEPLOYMENT_CHECKLIST.md)
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)

---

## 💰 Free Tier Info

- **$5 credit monthly**: Usually sufficient for small projects
- **Auto-sleep**: Saves resources when not in use
- **Wake on request**: Automatically wakes when accessed
- **PostgreSQL**: Included in free tier

---

**Ready to deploy? Go to [railway.app](https://railway.app) now!** 🚀

# Railway Deployment - Quick Demo Link Setup

## 🚀 Get Your Demo Link in 10 Minutes

### Step 1: Prepare Your Repository
1. **Ensure your code is on GitHub:**
   ```bash
   git add .
   git commit -m "Ready for Railway deployment"
   git push origin main
   ```

2. **Verify these files exist in your project:**
   - ✅ `railway.json` (already created)
   - ✅ `requirements.txt` (already exists)
   - ✅ `manage.py` (already exists)

### Step 2: Deploy to Railway

1. **Go to [Railway.app](https://railway.app)**
   - Sign up with GitHub
   - Click "New Project"

2. **Connect Your Repository:**
   - Select "Deploy from GitHub repo"
   - Choose your `PDF_Reader` repository
   - Click "Deploy Now"

3. **Railway will automatically:**
   - Detect Django project
   - Install dependencies
   - Set up PostgreSQL database
   - Deploy your application

### Step 3: Configure Environment Variables

1. **Go to your project dashboard**
2. **Click on "Variables" tab**
3. **Add these environment variables:**

```env
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=*.railway.app
DATABASE_URL=postgresql://... (Railway auto-sets this)
```

4. **Generate a secret key:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

### Step 4: Get Your Demo Link

1. **Railway automatically provides:**
   - `https://your-app-name.railway.app`

2. **Custom domain (optional):**
   - Go to "Settings" → "Domains"
   - Add your custom domain

### Step 5: Test Your Demo

1. **Visit your demo link**
2. **Test PDF upload functionality**
3. **Verify AI features work**

## 🎯 Demo Link Examples

Your demo link will look like:
- `https://pdf-reader-demo.railway.app`
- `https://smart-pdf-analyzer.railway.app`
- `https://ai-pdf-reader.railway.app`

## 🔧 Troubleshooting

### If deployment fails:
1. **Check logs** in Railway dashboard
2. **Verify requirements.txt** is complete
3. **Ensure all files are committed** to GitHub

### If app doesn't work:
1. **Check environment variables** are set
2. **Verify database migrations** ran
3. **Check static files** are collected

## 📊 Railway Pricing

- **Free Tier:** $5 credit/month
- **Hobby Plan:** $5/month
- **Pro Plan:** $20/month

**For demo purposes:** Free tier is sufficient!

## 🎉 Success!

Once deployed, you'll have:
- ✅ Professional demo link
- ✅ HTTPS enabled
- ✅ Database included
- ✅ Auto-deployment from GitHub
- ✅ Easy scaling if needed

---

**Your Demo Link:** `https://your-app-name.railway.app`

**Share this link in your portfolio, resume, or project submissions!**

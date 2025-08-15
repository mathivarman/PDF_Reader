# PythonAnywhere Deployment Instructions

## Quick Deploy Steps:

1. **Upload to PythonAnywhere:**
   - Go to PythonAnywhere Files tab
   - Upload the entire `pythonanywhere_deploy` folder
   - Rename it to your project name

2. **Open Bash Console:**
   ```bash
   cd your_project_name
   ```

3. **Create Virtual Environment:**
   ```bash
   python3.9 -m venv pdf_reader_env
   source pdf_reader_env/bin/activate
   ```

4. **Install Dependencies:**
   ```bash
   pip install -r requirements-pythonanywhere-optimized.txt
   ```

5. **Set Environment Variables:**
   ```bash
   nano .env
   ```
   Add your environment variables from `env_config.txt`

6. **Run Django Setup:**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

7. **Configure Web App:**
   - Go to Web tab
   - Set WSGI file to use `pdf_reader.production_settings`
   - Configure static files
   - Reload web app

8. **Test Your App:**
   Visit: https://yourusername.pythonanywhere.com

## Important Notes:
- This package is optimized for PythonAnywhere free tier
- Uses CPU-only PyTorch to save memory
- Includes production security settings
- Total size should be under 1GB

## Troubleshooting:
- Check error logs in Web tab
- Ensure all environment variables are set
- Verify database connection

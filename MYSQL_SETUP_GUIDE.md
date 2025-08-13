# MySQL Setup Guide for AI Legal Document Explainer

## Prerequisites ✅
- You have phpMyAdmin installed (which means you have MySQL)
- You have the project running with virtual environment activated

## Step 1: Create the Database in phpMyAdmin

1. **Open phpMyAdmin** in your browser (usually `http://localhost/phpmyadmin`)

2. **Create a new database:**
   - Click "New" in the left sidebar
   - Enter database name: `legal_doc_explainer`
   - Select collation: `utf8mb4_unicode_ci`
   - Click "Create"

3. **Verify the database was created** - you should see it in the left sidebar

## Step 2: Create Environment Configuration File

1. **Create a `.env` file** in your project root (same folder as `manage.py`)

2. **Add the following content** to the `.env` file:

```env
# Environment Mode (True=SQLite, False=MySQL)
DEBUG=False

# MySQL Database Configuration
DB_NAME=legal_doc_explainer
DB_USER=root
DB_PASSWORD=your_mysql_root_password
DB_HOST=localhost
DB_PORT=3306

# Django Configuration
SECRET_KEY=django-insecure-5vs1=d&=8=&#!kpv-15$cr#15^mmbyb5l82k*axtep-50i2+9x
ALLOWED_HOSTS=localhost,127.0.0.1
```

3. **Replace `your_mysql_root_password`** with your actual MySQL root password
   - If you don't have a password set, leave it empty: `DB_PASSWORD=`

## Step 3: Test Database Connection

1. **Check database status:**
```bash
python manage_db.py status
```

2. **Test the connection:**
```bash
python manage_db.py test
```

## Step 4: Run Database Migrations

1. **Create and apply migrations:**
```bash
python manage_db.py migrate
```

2. **Verify tables were created** in phpMyAdmin:
   - Click on your `legal_doc_explainer` database
   - You should see tables like:
     - `main_document`
     - `main_analysis`
     - `main_clause`
     - `main_redflag`
     - `main_question`
     - `main_usersession`
     - `main_documentchunk`

## Step 5: Create Superuser (Optional)

```bash
python manage_db.py superuser
```

## Troubleshooting

### Common Issues:

1. **"Access denied" error:**
   - Check your MySQL root password in the `.env` file
   - Verify the password in phpMyAdmin

2. **"Connection refused" error:**
   - Make sure MySQL service is running
   - Check if the port (3306) is correct

3. **"Database doesn't exist" error:**
   - Make sure you created the database in phpMyAdmin
   - Check the database name in your `.env` file

4. **"Module not found" error:**
   - Make sure you're in the virtual environment
   - Run: `pip install mysqlclient`

### Debug Commands:

```bash
# Check current database status
python manage_db.py status

# Show detailed database information
python manage_db.py info

# Test connection
python manage_db.py test

# Check Django settings
python manage.py check
```

## Verification Steps

After setup, verify everything is working:

1. **Database Status:**
```bash
python manage_db.py status
```
Should show:
- Engine: `django.db.backends.mysql`
- Status: `Connected`
- Debug Mode: `False`

2. **Check Tables in phpMyAdmin:**
- Navigate to your database
- Verify all tables are created

3. **Run the Development Server:**
```bash
python manage.py runserver
```
- Should start without database errors

## Switching Back to SQLite (if needed)

If you want to switch back to SQLite for development:

1. **Edit your `.env` file:**
```env
DEBUG=True
```

2. **Or delete the `.env` file** entirely (will use SQLite by default)

3. **Check status:**
```bash
python manage_db.py status
```

## Database Management Commands

```bash
# Check status
python manage_db.py status

# Show detailed info
python manage_db.py info

# Test connection
python manage_db.py test

# Run migrations
python manage_db.py migrate

# Create superuser
python manage_db.py superuser

# Show help
python manage_db.py help
```

## Next Steps

Once your MySQL database is connected:

1. ✅ Database is configured and connected
2. ✅ Tables are created
3. 🚀 Ready to start developing features!
4. 📝 Continue with Phase 1 development tasks

---

**Need Help?** If you encounter any issues, check the troubleshooting section above or run the debug commands to get more information about the problem.

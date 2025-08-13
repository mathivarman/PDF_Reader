# Database Setup Guide - AI Legal Document Explainer

## Overview

The AI Legal Document Explainer supports two database configurations:

1. **Development Environment**: SQLite (default, no setup required)
2. **Production Environment**: MySQL (recommended for production)

## Quick Start

### For Development (SQLite)

No setup required! The application will automatically use SQLite for development.

```bash
# Check database status
python manage_db.py status

# Run migrations
python manage_db.py migrate

# Test connection
python manage_db.py test
```

### For Production (MySQL)

Follow the steps below to set up MySQL for production.

## MySQL Setup

### 1. Install MySQL

#### Windows
```bash
# Download and install MySQL Community Server
# https://dev.mysql.com/downloads/mysql/
```

#### macOS
```bash
# Using Homebrew
brew install mysql
brew services start mysql
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

### 2. Create Database and User

```sql
-- Connect to MySQL as root
mysql -u root -p

-- Create database
CREATE DATABASE legal_doc_explainer CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user
CREATE USER 'legal_user'@'localhost' IDENTIFIED BY 'your_secure_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON legal_doc_explainer.* TO 'legal_user'@'localhost';
FLUSH PRIVILEGES;

-- Exit MySQL
EXIT;
```

### 3. Configure Environment Variables

Create a `.env` file in your project root:

```env
# Database Configuration
DEBUG=False
DB_NAME=legal_doc_explainer
DB_USER=legal_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=3306

# Django Configuration
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com
```

### 4. Install MySQL Client

```bash
# Install mysqlclient for Django
pip install mysqlclient
```

### 5. Run Migrations

```bash
# Set production mode
set DEBUG=False  # Windows
export DEBUG=False  # Linux/macOS

# Run migrations
python manage_db.py migrate
```

## Database Management Commands

### Check Database Status
```bash
python manage_db.py status
```

### Show Detailed Information
```bash
python manage_db.py info
```

### Test Connection
```bash
python manage_db.py test
```

### Run Migrations
```bash
python manage_db.py migrate
```

### Create Superuser
```bash
python manage_db.py superuser
```

## Database Schema

### Core Tables

1. **Document** - Stores uploaded PDF documents
2. **Analysis** - Stores analysis results (summary, clauses, red flags)
3. **Clause** - Stores detected legal clauses
4. **RedFlag** - Stores detected risks and red flags
5. **Question** - Stores user questions and answers
6. **UserSession** - Tracks user sessions
7. **DocumentChunk** - Stores document chunks for semantic search

### Key Features

- **UUID Primary Keys**: All models use UUID for better security
- **JSON Fields**: Flexible storage for analysis results
- **Audit Trails**: Created/updated timestamps on all models
- **Relationships**: Proper foreign key relationships between models
- **Indexing**: Optimized for common queries

## Performance Considerations

### SQLite (Development)
- **Pros**: No setup, file-based, perfect for development
- **Cons**: Limited concurrent connections, not suitable for production
- **Use Case**: Development and testing

### MySQL (Production)
- **Pros**: High performance, ACID compliance, concurrent connections
- **Cons**: Requires setup and maintenance
- **Use Case**: Production deployment

## Backup and Recovery

### SQLite Backup
```bash
# Simple file copy
cp db.sqlite3 db.sqlite3.backup
```

### MySQL Backup
```bash
# Create backup
mysqldump -u legal_user -p legal_doc_explainer > backup.sql

# Restore backup
mysql -u legal_user -p legal_doc_explainer < backup.sql
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Check if MySQL service is running
   - Verify host and port settings

2. **Access Denied**
   - Check username and password
   - Verify user permissions

3. **Character Set Issues**
   - Ensure database uses utf8mb4 charset
   - Check Django settings for proper encoding

4. **Migration Errors**
   - Check database connection
   - Verify model changes are correct

### Debug Commands

```bash
# Check Django database connection
python manage.py dbshell

# Show migration status
python manage.py showmigrations

# Reset database (WARNING: Deletes all data)
python manage.py flush
```

## Security Best Practices

1. **Use Strong Passwords**: Generate secure passwords for database users
2. **Limit Permissions**: Grant only necessary permissions to database users
3. **Network Security**: Restrict database access to trusted networks
4. **Regular Backups**: Implement automated backup procedures
5. **Monitor Logs**: Keep an eye on database access logs

## Environment-Specific Configuration

### Development
- Uses SQLite by default
- No additional configuration required
- Perfect for local development

### Staging
- Use MySQL with test data
- Mirror production configuration
- Test migrations before production

### Production
- Use MySQL with proper security
- Configure connection pooling
- Implement monitoring and backups

## Monitoring and Maintenance

### Regular Tasks
- Monitor database size and growth
- Check for slow queries
- Review and optimize indexes
- Update database statistics

### Health Checks
```bash
# Test database connection
python manage_db.py test

# Check migration status
python manage.py showmigrations

# Monitor database size (MySQL)
SELECT 
    table_schema AS 'Database',
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.tables 
WHERE table_schema = 'legal_doc_explainer'
GROUP BY table_schema;
```

## Support

For database-related issues:

1. Check the troubleshooting section above
2. Review Django database documentation
3. Check MySQL error logs
4. Use the database management commands for diagnostics

## Next Steps

After setting up the database:

1. Run migrations: `python manage_db.py migrate`
2. Create superuser: `python manage_db.py superuser`
3. Test the application: `python manage.py runserver`
4. Start developing features!

---

**Note**: This guide assumes you have basic knowledge of Django and database administration. For production deployments, consider consulting with a database administrator.

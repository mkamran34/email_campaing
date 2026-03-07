# Production Deployment Guide

This guide provides step-by-step instructions for deploying the Email System to production environments.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Deployment Platforms](#deployment-platforms)
5. [Security Considerations](#security-considerations)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

Before deploying to production, ensure the following:

- [ ] All environment variables are set (.env file configured properly)
- [ ] Database is properly initialized with all tables
- [ ] SSL/TLS certificate is obtained for HTTPS
- [ ] SMTP credentials are verified and tested
- [ ] Application has been tested locally with production settings
- [ ] Database backups are configured
- [ ] Logging is enabled and configured
- [ ] Error tracking (Sentry) is optional but recommended
- [ ] SECRET_KEY is unique and secure (minimum 32 characters)
- [ ] All sensitive data is in environment variables, NOT in code

---

## Environment Setup

### 1. Create Production Environment Variables

Copy the `.env.example` file and configure for production:

```bash
cp .env.example .env.production
```

Edit `.env.production` with your production values:

```dotenv
# Application
FLASK_ENV=production
SECRET_KEY=your-random-secret-key-min-32-chars
PORT=5001

# Database
DB_HOST=your-database-host
DB_USER=your-database-user
DB_PASSWORD=your-secure-password
DB_NAME=email_system
DB_PORT=3306

# SMTP
SMTP_HOST=mail.yourdomain.com
SMTP_PORT=587
SMTP_USERNAME=your-email@domain.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=True
FROM_EMAIL=noreply@yourdomain.com

# Application Config
BATCH_SIZE=100
DAILY_LIMIT=5000
BATCH_DELAY=60

# Logging
LOG_LEVEL=INFO
LOG_FILE=email_system.log
```

### 2. Generate Secure Secret Key

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Use this value for `SECRET_KEY` in your environment.

---

## Database Configuration

### 1. Remote Database Setup

For production, use a managed database service:

**Options:**
- AWS RDS (MySQL)
- Google Cloud SQL
- Azure Database for MySQL
- DigitalOcean Managed Databases
- Heroku PostgreSQL (if migrating)

### 2. Database Initialization

```bash
# Set production environment variables first
export FLASK_ENV=production
export DB_HOST=your-remote-host
export DB_USER=your-user
export DB_PASSWORD=your-password
export DB_NAME=email_system

# Run database setup
python db_setup.py
```

### 3. Database Backups

Set up automated backups:

```bash
# Create backup script (backup_db.sh)
#!/bin/bash
BACKUP_DIR="/backups/email_system"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASSWORD $DB_NAME \
  | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
```

Add to cron for daily backups:
```bash
0 2 * * * /path/to/backup_db.sh
```

---

## Deployment Platforms

### Option 1: Heroku

#### Steps:

1. **Install Heroku CLI**
   ```bash
   brew install heroku/brew/heroku
   heroku login
   ```

2. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set FLASK_ENV=production
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DB_HOST=your-db-host
   # ... set all other variables
   ```

4. **Add MySQL Add-on**
   ```bash
   heroku addons:create cleardb:ignite  # or another MySQL add-on
   ```

5. **Deploy**
   ```bash
   git push heroku main
   heroku logs --tail
   ```

### Option 2: Docker Deployment

#### Local Testing:

```bash
# Build image
docker build -t email-system:latest .

# Run with docker-compose
docker-compose -f docker-compose.yml up -d
```

#### Production Cloud Deployment:

**AWS ECS:**
```bash
# Tag and push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

docker tag email-system:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/email-system:latest
docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/email-system:latest
```

**Google Cloud Run:**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/email-system
gcloud run deploy email-system --image gcr.io/PROJECT_ID/email-system:latest \
  --platform managed --region us-central1
```

### Option 3: Traditional Server (VPS/Dedicated)

#### Steps:

1. **Install Dependencies**
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3.11 python3-pip mysql-client
   ```

2. **Clone Repository**
   ```bash
   cd /var/www
   git clone your-repo-url email-system
   cd email-system
   ```

3. **Setup Virtual Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   sudo nano .env.production  # or use your config management
   ```

5. **Setup Systemd Service**
   ```bash
   sudo nano /etc/systemd/system/email-system.service
   ```

   ```ini
   [Unit]
   Description=Email System Application
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/email-system
   Environment="PATH=/var/www/email-system/.venv/bin"
   EnvironmentFile=/var/www/email-system/.env.production
   ExecStart=/var/www/email-system/.venv/bin/gunicorn wsgi:app \
     --workers 4 --bind 0.0.0.0:5001 --timeout 120
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable email-system
   sudo systemctl start email-system
   sudo systemctl status email-system
   ```

6. **Setup Nginx Reverse Proxy**
   ```bash
   sudo nano /etc/nginx/sites-available/email-system
   ```

   ```nginx
   upstream email_system {
       server 127.0.0.1:5001;
   }

   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;
       return 301 https://$server_name$request_uri;
   }

   server {
       listen 443 ssl http2;
       server_name yourdomain.com www.yourdomain.com;

       ssl_certificate /etc/ssl/certs/your-cert.crt;
       ssl_certificate_key /etc/ssl/private/your-key.key;

       client_max_body_size 10M;

       location / {
           proxy_pass http://email_system;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_read_timeout 120s;
       }

       location /static {
           alias /var/www/email-system/static;
           expires 30d;
       }
   }
   ```

   ```bash
   sudo ln -s /etc/nginx/sites-available/email-system /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

7. **Setup SSL Certificate (Let's Encrypt)**
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
   ```

---

## Security Considerations

### 1. Environment Variables
- **Never** commit `.env` to version control
- Use `.gitignore` to exclude `.env`
- Store secrets in a secure vault (AWS Secrets Manager, HashiCorp Vault)

### 2. Database Security
- Use strong passwords (20+ characters, mixed case, numbers, symbols)
- Enable SSL/TLS for database connections
- Restrict database access to application server only
- Regular backups with encryption
- Use read replicas for backup reliability

### 3. HTTPS/TLS
- Always use HTTPS in production
- Obtain SSL certificate from Let's Encrypt or paid provider
- Set proper security headers

### 4. Application Security
- Enable CSRF protection if handling forms
- Rate limit API endpoints
- Implement request validation
- Keep dependencies updated
- Regular security audits

### 5. Email Security
- Use TLS/SSL for SMTP connections
- Validate email addresses before sending
- Implement bounce handling
- Monitor for spam complaints

### 6. Monitoring & Logging
- Enable application logging
- Set up error tracking (Sentry)
- Monitor system resources
- Alert on errors or failures

---

## Monitoring & Maintenance

### 1. Application Logs

View logs based on deployment method:

**Docker:**
```bash
docker logs -f email_system_app
```

**Heroku:**
```bash
heroku logs --tail
```

**VPS (Systemd):**
```bash
sudo journalctl -u email-system -f
```

### 2. Database Monitoring

```bash
# Check database size
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e \
  "SELECT table_name, ROUND(((data_length + index_length) / 1024 / 1024), 2) \
   FROM information_schema.tables WHERE table_schema = '$DB_NAME';"

# Monitor slow queries (if enabled)
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD \
  --query="SET GLOBAL slow_query_log = 'ON';" mysql
```

### 3. Health Checks

Set up monitoring to check application health:

```bash
# Simple endpoint check
curl -f https://yourdomain.com/ping || alert

# Full health check with database
curl -f https://yourdomain.com/api/health || alert
```

### 4. Dependency Updates

Regularly update dependencies securely:

```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade package-name

# Test in staging before production
pytest tests/
```

---

## Troubleshooting

### Issue: "SQLAlchemy database connection refused"

**Solution:**
```bash
# Verify database credentials
mysql -h $DB_HOST -u $DB_USER -p$DB_PASSWORD -e "SELECT 1;"

# Check network connectivity
telnet $DB_HOST 3306

# Verify firewall rules allow connection
```

### Issue: "SECRET_KEY not set" in production

**Solution:**
```bash
# Generate and set secret key
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
export SECRET_KEY=$SECRET_KEY
# Add to your deployment platform's environment variables
```

### Issue: SMTP authentication fails

**Solution:**
```bash
# Verify SMTP credentials
python3 -c "
import smtplib
s = smtplib.SMTP('$SMTP_HOST', $SMTP_PORT)
s.starttls()
s.login('$SMTP_USERNAME', '$SMTP_PASSWORD')
print('✓ SMTP authentication successful')
"
```

### Issue: High memory usage

**Solution:**
- Adjust Gunicorn workers: `--workers 2` (reduce from 4)
- Implement connection pooling
- Monitor and optimize database queries

### Issue: Application crashes on deployment

**Solution:**
```bash
# Check logs for errors
# Review environment variables are set correctly
# Verify all dependencies installed: pip install -r requirements.txt
# Run database migrations: python db_setup.py
```

---

## Support & Resources

- **Documentation**: See [README.md](README.md)
- **Local Development**: See [DASHBOARD_GUIDE.md](DASHBOARD_GUIDE.md)
- **API Reference**: See [API_VALIDATION.md](API_VALIDATION.md)
- **Authentication**: See [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md)

For issues or questions, check [TROUBLESHOOTING.md](TROUBLESHOOTING.md).

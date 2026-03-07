"""
Configuration file for the email sending system
"""
import os
from dotenv import load_dotenv

load_dotenv()

# MySQL Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'email_system'),
    'port': int(os.getenv('DB_PORT', 3306)),
}

# Email Configuration
SMTP_CONFIG = {
    'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
    'port': int(os.getenv('SMTP_PORT', 587)),
    'username': os.getenv('SMTP_USERNAME', ''),
    'password': os.getenv('SMTP_PASSWORD', ''),
    'use_tls': os.getenv('SMTP_USE_TLS', 'True') == 'True',
    'from_email': os.getenv('FROM_EMAIL', 'noreply@example.com'),
}

# Batch Configuration
BATCH_SIZE = int(os.getenv('BATCH_SIZE', 100))  # emails per batch
DAILY_LIMIT = int(os.getenv('DAILY_LIMIT', 5000))  # max emails per day

# Flask Session Configuration
PERMANENT_SESSION_LIFETIME = 86400 * 7  # 7 days

# Secret key for session encryption
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
if FLASK_ENV == 'production':
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY or SECRET_KEY == 'dev-secret-key-change-in-production':
        raise ValueError('SECRET_KEY environment variable must be set in production')
else:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Production settings
PRODUCTION = FLASK_ENV == 'production'
DEBUG = not PRODUCTION
BATCHES_PER_DAY = DAILY_LIMIT // BATCH_SIZE  # number of batches
BATCH_DELAY = int(os.getenv('BATCH_DELAY', 60))  # seconds between batches

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'email_system.log')

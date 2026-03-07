"""
Database setup script - creates required tables in MySQL
Run this once to initialize the database schema
"""
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_tables():
    """Create required database tables"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Create emails table
        create_emails_table = """
        CREATE TABLE IF NOT EXISTS emails (
            id INT AUTO_INCREMENT PRIMARY KEY,
            recipient VARCHAR(255) NOT NULL,
            subject VARCHAR(255) NOT NULL,
            body LONGTEXT NOT NULL,
            status ENUM('pending', 'sent', 'failed', 'bounced') DEFAULT 'pending',
            error_message TEXT,
            sent_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_status (status),
            INDEX idx_created_at (created_at),
            INDEX idx_sent_at (sent_at)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_emails_table)
        logger.info("✓ emails table created successfully")
        
        # Create daily_statistics table for tracking
        create_stats_table = """
        CREATE TABLE IF NOT EXISTS daily_statistics (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE UNIQUE NOT NULL,
            total_sent INT DEFAULT 0,
            total_failed INT DEFAULT 0,
            total_bounced INT DEFAULT 0,
            total_pending INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_stats_table)
        logger.info("✓ daily_statistics table created successfully")
        
        # Create users table for authentication
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(120) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(120),
            is_active BOOLEAN DEFAULT TRUE,
            role ENUM('admin', 'user') DEFAULT 'user',
            last_login TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_username (username),
            INDEX idx_email (email)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_users_table)
        logger.info("✓ users table created successfully")
        
        connection.commit()
        cursor.close()
        connection.close()
        logger.info("✓ Database setup completed successfully!")
    
    except Error as e:
        logger.error(f"Error setting up database: {e}")
        raise


if __name__ == '__main__':
    print("Creating database tables...")
    create_tables()

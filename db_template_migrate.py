"""
Database migration script to add email templates and scheduler tables
"""
import mysql.connector
from config import DB_CONFIG
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_templates_table():
    """Create email_templates table"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Drop table if exists (for fresh start)
        cursor.execute("DROP TABLE IF EXISTS email_templates")
        
        # Create templates table
        cursor.execute("""
            CREATE TABLE email_templates (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                subject VARCHAR(255) NOT NULL,
                body TEXT NOT NULL,
                plain_text TEXT,
                html_body TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_default BOOLEAN DEFAULT FALSE,
                tags JSON COMMENT 'Template tags for organization',
                variables JSON COMMENT 'Template variables like {{name}}, {{email}}',
                INDEX idx_name (name),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ Created email_templates table")
        
        cursor.close()
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error creating templates table: {e}")
        return False

def create_scheduler_table():
    """Create email_schedules table"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Drop table if exists (for fresh start)
        cursor.execute("DROP TABLE IF EXISTS email_schedules")
        
        # Create schedules table
        cursor.execute("""
            CREATE TABLE email_schedules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                template_id INT,
                recipient_list JSON NOT NULL COMMENT 'List of recipient emails',
                schedule_type ENUM('once', 'recurring', 'daily', 'weekly', 'monthly') NOT NULL,
                schedule_time TIME,
                schedule_day INT COMMENT 'Day of week (0-6) or month (1-31)',
                start_date DATE,
                end_date DATE,
                is_active BOOLEAN DEFAULT TRUE,
                total_recipients INT,
                sent_count INT DEFAULT 0,
                failed_count INT DEFAULT 0,
                status ENUM('draft', 'scheduled', 'running', 'completed', 'failed', 'paused') DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                last_run TIMESTAMP NULL,
                next_run TIMESTAMP NULL,
                created_by VARCHAR(255),
                notes TEXT,
                FOREIGN KEY (template_id) REFERENCES email_templates(id) ON DELETE SET NULL,
                INDEX idx_status (status),
                INDEX idx_next_run (next_run),
                INDEX idx_is_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ Created email_schedules table")
        
        cursor.close()
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error creating schedules table: {e}")
        return False

def create_schedule_logs_table():
    """Create schedule_logs table for tracking"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Drop table if exists
        cursor.execute("DROP TABLE IF EXISTS schedule_logs")
        
        # Create logs table
        cursor.execute("""
            CREATE TABLE schedule_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                schedule_id INT NOT NULL,
                run_id VARCHAR(50) NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP NULL,
                total_sent INT DEFAULT 0,
                total_failed INT DEFAULT 0,
                status ENUM('running', 'completed', 'failed') DEFAULT 'running',
                error_message TEXT,
                FOREIGN KEY (schedule_id) REFERENCES email_schedules(id) ON DELETE CASCADE,
                INDEX idx_schedule_id (schedule_id),
                INDEX idx_run_id (run_id),
                INDEX idx_started_at (started_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✓ Created schedule_logs table")
        
        cursor.close()
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error creating schedule logs table: {e}")
        return False

def main():
    print("Starting database migration for templates and scheduler...")
    
    if create_templates_table() and create_scheduler_table() and create_schedule_logs_table():
        print("\n✓ Database migration completed successfully!")
        return True
    else:
        print("\n✗ Database migration failed!")
        return False

if __name__ == '__main__':
    main()

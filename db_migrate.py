"""
Database migration - Add email validation columns
Run this to add validation fields to the emails table
"""
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def add_validation_columns():
    """Add validation-related columns to emails table"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        db_name = DB_CONFIG.get('database', 'email_system')
        
        # Check if columns exist before adding
        check_column = """
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = 'emails' 
        AND TABLE_SCHEMA = %s
        AND COLUMN_NAME IN ('validation_status', 'validation_notes', 'validated_at')
        """
        
        cursor.execute(check_column, (db_name,))
        existing_columns = {row[0] for row in cursor.fetchall()}
        
        # Add validation_status if missing
        if 'validation_status' not in existing_columns:
            alter_query = """
            ALTER TABLE emails 
            ADD COLUMN validation_status ENUM('unchecked', 'valid', 'invalid', 'needs_review') DEFAULT 'unchecked'
            """
            cursor.execute(alter_query)
            logger.info("✓ Added validation_status column")
        else:
            logger.info("✓ validation_status column already exists")
        
        # Add validation_notes if missing
        if 'validation_notes' not in existing_columns:
            alter_query = """
            ALTER TABLE emails 
            ADD COLUMN validation_notes JSON
            """
            cursor.execute(alter_query)
            logger.info("✓ Added validation_notes column")
        else:
            logger.info("✓ validation_notes column already exists")
        
        # Add validated_at if missing
        if 'validated_at' not in existing_columns:
            alter_query = """
            ALTER TABLE emails 
            ADD COLUMN validated_at TIMESTAMP NULL
            """
            cursor.execute(alter_query)
            logger.info("✓ Added validated_at column")
        else:
            logger.info("✓ validated_at column already exists")
        
        # Add index for validation_status
        try:
            cursor.execute("ALTER TABLE emails ADD INDEX idx_validation_status (validation_status)")
            logger.info("✓ Added index on validation_status")
        except:
            logger.info("✓ Index on validation_status already exists")
        
        connection.commit()
        cursor.close()
        connection.close()
        logger.info("✓ Database migration completed successfully!")
        
    except Error as e:
        logger.error(f"Error during migration: {e}")
        raise


if __name__ == '__main__':
    print("Running database migration...")
    add_validation_columns()

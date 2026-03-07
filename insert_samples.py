"""
Sample data insertion script for testing
Run this to insert test emails into the database
"""
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def insert_sample_emails(count=100):
    """Insert sample emails for testing"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Sample email data
        sample_emails = []
        for i in range(1, count + 1):
            email = (
                f"user{i}@example.com",
                f"Test Email {i}",
                f"This is a test email #{i}. Hello user {i}!",
                "pending"
            )
            sample_emails.append(email)
        
        # Insert emails
        insert_query = """
        INSERT INTO emails (recipient, subject, body, status)
        VALUES (%s, %s, %s, %s)
        """
        
        cursor.executemany(insert_query, sample_emails)
        connection.commit()
        
        logger.info(f"✓ Inserted {cursor.rowcount} sample emails")
        cursor.close()
        connection.close()
    
    except Error as e:
        logger.error(f"Error inserting sample emails: {e}")
        raise


if __name__ == '__main__':
    import sys
    
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    print(f"Inserting {count} sample emails...")
    insert_sample_emails(count)

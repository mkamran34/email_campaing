"""
Database helper functions for email system
"""
import mysql.connector
from mysql.connector import Error
import logging
from config import DB_CONFIG

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages MySQL database connections"""
    
    def __init__(self):
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            logger.info("Database connection established")
            return self.connection
        except Error as e:
            logger.error(f"Error connecting to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Database connection closed")
    
    def get_pending_emails(self, limit):
        """
        Fetch pending emails from database
        
        Args:
            limit: number of emails to fetch
            
        Returns:
            List of email dictionaries with id, recipient, subject, body
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT id, recipient, subject, body 
                FROM emails 
                WHERE status = 'pending' 
                LIMIT %s
            """
            cursor.execute(query, (limit,))
            emails = cursor.fetchall()
            cursor.close()
            logger.info(f"Fetched {len(emails)} pending emails")
            return emails
        except Error as e:
            logger.error(f"Error fetching emails: {e}")
            return []
    
    def update_email_status(self, email_id, status, error_message=None):
        """
        Update email delivery status
        
        Args:
            email_id: ID of the email
            status: 'pending', 'sent', 'failed', 'bounced'
            error_message: optional error details
        """
        try:
            cursor = self.connection.cursor()
            
            if error_message:
                query = """
                    UPDATE emails 
                    SET status = %s, error_message = %s, updated_at = NOW()
                    WHERE id = %s
                """
                cursor.execute(query, (status, error_message, email_id))
            else:
                query = """
                    UPDATE emails 
                    SET status = %s, sent_at = NOW(), updated_at = NOW()
                    WHERE id = %s
                """
                cursor.execute(query, (status, email_id))
            
            self.connection.commit()
            cursor.close()
            logger.debug(f"Email {email_id} status updated to {status}")
        except Error as e:
            logger.error(f"Error updating email status: {e}")
            self.connection.rollback()
    
    def get_daily_sent_count(self):
        """Get number of emails sent today"""
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT COUNT(*) as count 
                FROM emails 
                WHERE status = 'sent' 
                AND DATE(sent_at) = CURDATE()
            """
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else 0
        except Error as e:
            logger.error(f"Error getting daily sent count: {e}")
            return 0    
    def get_emails_for_validation(self, validation_status='unchecked', limit=100, offset=0):
        """
        Fetch emails that need validation
        
        Args:
            validation_status: 'unchecked', 'valid', 'invalid', 'needs_review'
            limit: number of emails to fetch
            offset: pagination offset
            
        Returns:
            List of email dictionaries with id, recipient, subject, validation_status, validation_notes
        """
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT id, recipient, subject, validation_status, validation_notes, validated_at
                FROM emails 
                WHERE validation_status = %s
                ORDER BY id DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (validation_status, limit, offset))
            emails = cursor.fetchall()
            cursor.close()
            logger.info(f"Fetched {len(emails)} emails with validation_status={validation_status}")
            return emails
        except Error as e:
            logger.error(f"Error fetching emails for validation: {e}")
            return []
    
    def get_validation_count(self, validation_status):
        """Get count of emails by validation status"""
        try:
            cursor = self.connection.cursor()
            query = """
                SELECT COUNT(*) as count 
                FROM emails 
                WHERE validation_status = %s
            """
            cursor.execute(query, (validation_status,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else 0
        except Error as e:
            logger.error(f"Error getting validation count: {e}")
            return 0
    
    def save_validation_result(self, email_id, validation_status, validation_notes):
        """
        Save email validation result to database
        
        Args:
            email_id: ID of the email
            validation_status: 'valid', 'invalid', 'needs_review'
            validation_notes: dict with validation details (errors, warnings, suggestions)
        """
        try:
            cursor = self.connection.cursor()
            
            import json
            validation_notes_json = json.dumps(validation_notes) if validation_notes else None
            
            query = """
                UPDATE emails 
                SET validation_status = %s, 
                    validation_notes = %s,
                    validated_at = NOW(),
                    updated_at = NOW()
                WHERE id = %s
            """
            cursor.execute(query, (validation_status, validation_notes_json, email_id))
            
            self.connection.commit()
            cursor.close()
            logger.debug(f"Email {email_id} validation result saved: {validation_status}")
            return True
        except Error as e:
            logger.error(f"Error saving validation result: {e}")
            self.connection.rollback()
            return False
    
    def get_validation_statistics(self):
        """Get statistics about email validation"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN validation_status = 'unchecked' THEN 1 ELSE 0 END) as unchecked,
                    SUM(CASE WHEN validation_status = 'valid' THEN 1 ELSE 0 END) as valid,
                    SUM(CASE WHEN validation_status = 'invalid' THEN 1 ELSE 0 END) as invalid,
                    SUM(CASE WHEN validation_status = 'needs_review' THEN 1 ELSE 0 END) as needs_review
                FROM emails
            """
            cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            logger.error(f"Error getting validation statistics: {e}")
            return None
    
    # ===================== TEMPLATE METHODS =====================
    
    def create_template(self, name, subject, body, html_body=None, plain_text=None, tags=None):
        """Create a new email template"""
        try:
            cursor = self.connection.cursor()
            import json
            query = """
                INSERT INTO email_templates (name, subject, body, html_body, plain_text, tags)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            tags_json = json.dumps(tags) if tags else None
            cursor.execute(query, (name, subject, body, html_body or body, plain_text or body, tags_json))
            self.connection.commit()
            template_id = cursor.lastrowid
            cursor.close()
            logger.info(f"Template created: {name} (ID: {template_id})")
            return template_id
        except Error as e:
            logger.error(f"Error creating template: {e}")
            self.connection.rollback()
            return None
    
    def get_all_templates(self):
        """Get all email templates"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT id, name, subject, created_at, updated_at, is_default 
                FROM email_templates 
                ORDER BY updated_at DESC
            """
            cursor.execute(query)
            templates = cursor.fetchall()
            cursor.close()
            return templates
        except Error as e:
            logger.error(f"Error getting templates: {e}")
            return []
    
    def get_template(self, template_id):
        """Get a specific template by ID"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM email_templates WHERE id = %s
            """
            cursor.execute(query, (template_id,))
            template = cursor.fetchone()
            cursor.close()
            return template
        except Error as e:
            logger.error(f"Error getting template: {e}")
            return None
    
    def update_template(self, template_id, name=None, subject=None, body=None, html_body=None, plain_text=None, tags=None):
        """Update an email template"""
        try:
            cursor = self.connection.cursor()
            import json
            
            updates = []
            params = []
            
            if name is not None:
                updates.append("name = %s")
                params.append(name)
            if subject is not None:
                updates.append("subject = %s")
                params.append(subject)
            if body is not None:
                updates.append("body = %s")
                params.append(body)
            if html_body is not None:
                updates.append("html_body = %s")
                params.append(html_body)
            if plain_text is not None:
                updates.append("plain_text = %s")
                params.append(plain_text)
            if tags is not None:
                updates.append("tags = %s")
                params.append(json.dumps(tags))
            
            if not updates:
                return False
            
            params.append(template_id)
            query = f"UPDATE email_templates SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            logger.info(f"Template {template_id} updated")
            return True
        except Error as e:
            logger.error(f"Error updating template: {e}")
            self.connection.rollback()
            return False
    
    def delete_template(self, template_id):
        """Delete an email template"""
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM email_templates WHERE id = %s"
            cursor.execute(query, (template_id,))
            self.connection.commit()
            cursor.close()
            logger.info(f"Template {template_id} deleted")
            return True
        except Error as e:
            logger.error(f"Error deleting template: {e}")
            self.connection.rollback()
            return False
    
    # ===================== SCHEDULER METHODS =====================
    
    def create_schedule(self, name, template_id, recipient_list, schedule_type, 
                       schedule_time=None, schedule_day=None, start_date=None, 
                       end_date=None, created_by=None, notes=None):
        """Create a new email schedule"""
        try:
            cursor = self.connection.cursor()
            import json
            
            recipient_json = json.dumps(recipient_list) if isinstance(recipient_list, list) else recipient_list
            total_recipients = len(recipient_list) if isinstance(recipient_list, list) else 0
            
            query = """
                INSERT INTO email_schedules 
                (name, template_id, recipient_list, schedule_type, schedule_time, schedule_day, 
                 start_date, end_date, created_by, notes, total_recipients)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (name, template_id, recipient_json, schedule_type, 
                                  schedule_time, schedule_day, start_date, end_date, created_by, notes, total_recipients))
            self.connection.commit()
            schedule_id = cursor.lastrowid
            cursor.close()
            logger.info(f"Schedule created: {name} (ID: {schedule_id})")
            return schedule_id
        except Error as e:
            logger.error(f"Error creating schedule: {e}")
            self.connection.rollback()
            return None
    
    def get_all_schedules(self):
        """Get all email schedules"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT id, name, template_id, schedule_type, status, total_recipients, 
                       sent_count, failed_count, created_at, next_run, is_active
                FROM email_schedules 
                ORDER BY created_at DESC
            """
            cursor.execute(query)
            schedules = cursor.fetchall()
            cursor.close()
            return schedules
        except Error as e:
            logger.error(f"Error getting schedules: {e}")
            return []
    
    def get_schedule(self, schedule_id):
        """Get a specific schedule by ID"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM email_schedules WHERE id = %s
            """
            cursor.execute(query, (schedule_id,))
            schedule = cursor.fetchone()
            cursor.close()
            return schedule
        except Error as e:
            logger.error(f"Error getting schedule: {e}")
            return None
    
    def update_schedule(self, schedule_id, **kwargs):
        """Update a schedule"""
        try:
            cursor = self.connection.cursor()
            import json
            
            updates = []
            params = []
            
            allowed_fields = ['name', 'template_id', 'schedule_type', 'schedule_time', 
                            'schedule_day', 'start_date', 'end_date', 'is_active', 
                            'status', 'notes', 'next_run']
            
            for key, value in kwargs.items():
                if key in allowed_fields:
                    updates.append(f"{key} = %s")
                    params.append(value)
            
            if not updates:
                return False
            
            params.append(schedule_id)
            query = f"UPDATE email_schedules SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            self.connection.commit()
            cursor.close()
            logger.info(f"Schedule {schedule_id} updated")
            return True
        except Error as e:
            logger.error(f"Error updating schedule: {e}")
            self.connection.rollback()
            return False
    
    def delete_schedule(self, schedule_id):
        """Delete a schedule"""
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM email_schedules WHERE id = %s"
            cursor.execute(query, (schedule_id,))
            self.connection.commit()
            cursor.close()
            logger.info(f"Schedule {schedule_id} deleted")
            return True
        except Error as e:
            logger.error(f"Error deleting schedule: {e}")
            self.connection.rollback()
            return False
    
    def get_active_schedules(self):
        """Get all active schedules"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT * FROM email_schedules 
                WHERE is_active = TRUE AND status != 'completed'
                ORDER BY next_run ASC
            """
            cursor.execute(query)
            schedules = cursor.fetchall()
            cursor.close()
            return schedules
        except Error as e:
            logger.error(f"Error getting active schedules: {e}")
            return []
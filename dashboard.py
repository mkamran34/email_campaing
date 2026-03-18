"""
Flask web dashboard for email system management
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

app = Flask(__name__)
# ...existing code...

# --- Group endpoints (move below app initialization) ---
@app.route('/api/scheduler/group-members', methods=['GET'])
def api_scheduler_group_members():
    import db_helper
    group_id = request.args.get('group_id')
    if not group_id:
        return { 'success': False, 'error': 'Missing group_id' }
    try:
        db = db_helper.get_db()
        cursor = db.cursor()
        cursor.execute("""
            SELECT emails.email
            FROM group_members
            JOIN emails ON group_members.email_id = emails.id
            WHERE group_members.group_id = %s
        """, (group_id,))
        members = [ row[0] for row in cursor.fetchall() ]
        return { 'success': True, 'members': members }
    except Exception as e:
        return { 'success': False, 'error': str(e) }

@app.route('/api/scheduler/groups', methods=['GET'])
def api_scheduler_groups():
    import db_helper
    try:
        db = db_helper.get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name FROM recipient_groups ORDER BY name")
        groups = [ {'id': row[0], 'name': row[1]} for row in cursor.fetchall() ]
        return { 'success': True, 'groups': groups }
    except Exception as e:
        return { 'success': False, 'error': str(e) }
"""
Flask web dashboard for email system management
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
import logging
from datetime import datetime
import os
from email_validator import validate_email

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7  # 7 days

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# User class for Flask-Login
class User(UserMixin):
    """User model for authentication"""
    
    def __init__(self, user_id, username, email, full_name=None, role='user'):
        self.id = user_id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.role = role


# Load user from database
@login_manager.user_loader
def load_user(user_id):
    """Load user from database by ID"""
    db = DashboardDB()
    if db.connect():
        user = db.get_user_by_id(user_id)
        db.disconnect()
        return user
    return None


class DashboardDB:
    """Database operations for dashboard"""
    
    def __init__(self):
        self.connection = None
    
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            return self.connection
        except Error as e:
            logger.error(f"Database connection error: {e}")
            return None
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def get_stats(self):
        """Get overall statistics"""
        try:
            if not self.connection or not self.connection.is_connected():
                logger.error("Database connection not available in get_stats")
                return None
            
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    SUM(CASE WHEN status = 'bounced' THEN 1 ELSE 0 END) as bounced
                FROM emails
            """
            cursor.execute(query)
            stats = cursor.fetchone()
            cursor.close()
            return stats
        except Error as e:
            logger.error(f"Error getting stats: {e}")
            return None
    
    def get_daily_stats(self):
        """Get today's statistics"""
        try:
            if not self.connection or not self.connection.is_connected():
                logger.error("Database connection not available in get_daily_stats")
                return None
            
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'sent' THEN 1 ELSE 0 END) as sent,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed,
                    SUM(CASE WHEN status = 'bounced' THEN 1 ELSE 0 END) as bounced,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending
                FROM emails
                WHERE DATE(created_at) = CURDATE()
                GROUP BY DATE(created_at)
            """
            cursor.execute(query)
            stats = cursor.fetchone()
            cursor.close()
            return stats if stats else {
                'date': datetime.now().date(),
                'total': 0, 'sent': 0, 'failed': 0, 'bounced': 0, 'pending': 0
            }
        except Error as e:
            logger.error(f"Error getting daily stats: {e}")
            return None
    
    def get_emails(self, status=None, limit=50, offset=0):
        """Get emails with optional status filter"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            if status:
                query = """
                    SELECT * FROM emails 
                    WHERE status = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (status, limit, offset))
            else:
                query = """
                    SELECT * FROM emails 
                    ORDER BY created_at DESC 
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (limit, offset))
            
            emails = cursor.fetchall()
            cursor.close()
            
            # Convert datetime objects to strings
            for email in emails:
                if email['created_at']:
                    email['created_at'] = email['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if email['sent_at']:
                    email['sent_at'] = email['sent_at'].strftime('%Y-%m-%d %H:%M:%S')
                if email['updated_at']:
                    email['updated_at'] = email['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return emails
        except Error as e:
            logger.error(f"Error getting emails: {e}")
            return []
    
    def get_email_count(self, status=None):
        """Get total count of emails"""
        try:
            cursor = self.connection.cursor()
            
            if status:
                query = "SELECT COUNT(*) FROM emails WHERE status = %s"
                cursor.execute(query, (status,))
            else:
                query = "SELECT COUNT(*) FROM emails"
                cursor.execute(query)
            
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except Error as e:
            logger.error(f"Error getting email count: {e}")
            return 0

    def get_scheduler_recipients(self, limit=1000, validation_status=None):
        """Get distinct recipient emails from database for scheduler"""
        try:
            cursor = self.connection.cursor(dictionary=True)

            params = []
            query = """
                SELECT DISTINCT recipient
                FROM emails
                WHERE recipient IS NOT NULL
                AND TRIM(recipient) != ''
            """

            if validation_status:
                query += " AND validation_status = %s"
                params.append(validation_status)

            query += " ORDER BY recipient ASC LIMIT %s"
            params.append(limit)

            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            cursor.close()

            recipients = [row['recipient'].strip() for row in rows if row.get('recipient')]
            return recipients
        except Error as e:
            logger.error(f"Error getting scheduler recipients: {e}")
            return []
    
    def update_email_status(self, email_id, status, error_message=None):
        """Update email status"""
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
            logger.info(f"Email {email_id} status updated to {status}")
            return True
        except Error as e:
            logger.error(f"Error updating email: {e}")
            self.connection.rollback()
            return False
    
    def delete_email(self, email_id):
        """Delete an email"""
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM emails WHERE id = %s"
            cursor.execute(query, (email_id,))
            self.connection.commit()
            cursor.close()
            logger.info(f"Email {email_id} deleted")
            return True
        except Error as e:
            logger.error(f"Error deleting email: {e}")
            self.connection.rollback()
            return False
    
    def bulk_update_status(self, email_ids, status):
        """Update multiple emails status"""
        try:
            cursor = self.connection.cursor()
            placeholders = ','.join(['%s'] * len(email_ids))
            query = f"""
                UPDATE emails 
                SET status = %s, updated_at = NOW()
                WHERE id IN ({placeholders})
            """
            cursor.execute(query, [status] + email_ids)
            self.connection.commit()
            rows = cursor.rowcount
            cursor.close()
            logger.info(f"Updated {rows} emails to {status}")
            return True
        except Error as e:
            logger.error(f"Error bulk updating emails: {e}")
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
    
    def get_emails_for_validation(self, validation_status='unchecked', limit=100, offset=0):
        """Get emails that need validation"""
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
        """Save email validation result to database"""
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
    
    # ==================== TEMPLATE METHODS ====================
    
    def create_template(self, name, subject, body, html_body=None, plain_text=None, tags=None):
        """Create a new email template"""
        try:
            cursor = self.connection.cursor()
            
            query = """
                INSERT INTO email_templates 
                (name, subject, body, html_body, plain_text, tags, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW(), NOW())
            """
            cursor.execute(query, (name, subject, body, html_body, plain_text, tags))
            
            self.connection.commit()
            template_id = cursor.lastrowid
            cursor.close()
            logger.info(f"Template '{name}' created with ID {template_id}")
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
                SELECT id, name, subject, body, html_body, plain_text, tags, 
                       created_at, updated_at
                FROM email_templates
                ORDER BY updated_at DESC
            """
            cursor.execute(query)
            templates = cursor.fetchall()
            cursor.close()
            
            # Convert datetime objects to strings
            for template in templates:
                if template.get('created_at'):
                    template['created_at'] = template['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if template.get('updated_at'):
                    template['updated_at'] = template['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return templates
        except Error as e:
            logger.error(f"Error getting templates: {e}")
            return []
    
    def get_template(self, template_id):
        """Get a specific template by ID"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT id, name, subject, body, html_body, plain_text, tags, 
                       created_at, updated_at
                FROM email_templates
                WHERE id = %s
            """
            cursor.execute(query, (template_id,))
            template = cursor.fetchone()
            cursor.close()
            
            if template:
                if template.get('created_at'):
                    template['created_at'] = template['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                if template.get('updated_at'):
                    template['updated_at'] = template['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
            
            return template
        except Error as e:
            logger.error(f"Error getting template {template_id}: {e}")
            return None
    
    def update_template(self, template_id, name=None, subject=None, body=None, 
                       html_body=None, plain_text=None, tags=None):
        """Update an existing template"""
        try:
            cursor = self.connection.cursor()
            
            # Build dynamic update query based on provided fields
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
                params.append(tags)
            
            if not updates:
                return False
            
            updates.append("updated_at = NOW()")
            params.append(template_id)
            
            query = f"""
                UPDATE email_templates 
                SET {', '.join(updates)}
                WHERE id = %s
            """
            cursor.execute(query, params)
            
            self.connection.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            logger.info(f"Template {template_id} updated")
            return rows_affected > 0
        except Error as e:
            logger.error(f"Error updating template: {e}")
            self.connection.rollback()
            return False
    
    def delete_template(self, template_id):
        """Delete a template"""
        try:
            cursor = self.connection.cursor()
            query = "DELETE FROM email_templates WHERE id = %s"
            cursor.execute(query, (template_id,))
            self.connection.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            logger.info(f"Template {template_id} deleted")
            return rows_affected > 0
        except Error as e:
            logger.error(f"Error deleting template: {e}")
            self.connection.rollback()
            return False
    
    # ==================== SCHEDULE METHODS ====================
    
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
        """Get all email schedules with template names"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT s.id, s.name, s.template_id, t.name as template_name, 
                       s.schedule_type, s.schedule_time, s.schedule_day, s.recipient_list,
                       s.start_date, s.end_date, s.is_active, s.total_recipients,
                       s.sent_count, s.failed_count, s.status, s.last_run, s.next_run, 
                       s.created_at, s.updated_at, s.created_by, s.notes
                FROM email_schedules s
                LEFT JOIN email_templates t ON s.template_id = t.id
                ORDER BY s.updated_at DESC
            """
            cursor.execute(query)
            schedules = cursor.fetchall()
            cursor.close()
            
            # Convert datetime objects to strings
            for schedule in schedules:
                for field in ['start_date', 'end_date', 'last_run', 'next_run', 'created_at', 'updated_at']:
                    if schedule.get(field):
                        schedule[field] = schedule[field].strftime('%Y-%m-%d %H:%M:%S')
                # Convert timedelta (TIME field) to string
                if schedule.get('schedule_time') and hasattr(schedule['schedule_time'], 'total_seconds'):
                    # Convert timedelta to HH:MM:SS format
                    total_seconds = int(schedule['schedule_time'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    schedule['schedule_time'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                # Parse recipient_list from JSON if it's a string
                if schedule.get('recipient_list') and isinstance(schedule['recipient_list'], str):
                    import json
                    try:
                        schedule['recipient_list'] = json.loads(schedule['recipient_list'])
                    except:
                        schedule['recipient_list'] = []
            
            return schedules
        except Error as e:
            logger.error(f"Error getting schedules: {e}")
            return []
    
    def get_schedule(self, schedule_id):
        """Get a specific schedule by ID"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT s.*, t.name as template_name
                FROM email_schedules s
                LEFT JOIN email_templates t ON s.template_id = t.id
                WHERE s.id = %s
            """
            cursor.execute(query, (schedule_id,))
            schedule = cursor.fetchone()
            cursor.close()
            
            if schedule:
                for field in ['start_date', 'end_date', 'last_run', 'next_run', 'created_at', 'updated_at']:
                    if schedule.get(field):
                        schedule[field] = schedule[field].strftime('%Y-%m-%d %H:%M:%S')
                # Convert timedelta (TIME field) to string
                if schedule.get('schedule_time') and hasattr(schedule['schedule_time'], 'total_seconds'):
                    total_seconds = int(schedule['schedule_time'].total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    seconds = total_seconds % 60
                    schedule['schedule_time'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                # Parse recipient_list from JSON if it's a string
                if schedule.get('recipient_list') and isinstance(schedule['recipient_list'], str):
                    import json
                    try:
                        schedule['recipient_list'] = json.loads(schedule['recipient_list'])
                    except:
                        schedule['recipient_list'] = []
            
            return schedule
        except Error as e:
            logger.error(f"Error getting schedule {schedule_id}: {e}")
            return None
    
    def update_schedule(self, schedule_id, **kwargs):
        """Update an existing schedule"""
        try:
            cursor = self.connection.cursor()
            
            # Build dynamic update query based on provided fields
            allowed_fields = ['name', 'template_id', 'recipient_list', 'schedule_type', 'schedule_time', 
                            'schedule_day', 'start_date', 'end_date', 'is_active', 'total_recipients',
                            'sent_count', 'failed_count', 'status', 'last_run', 'next_run', 
                            'created_by', 'notes']
            updates = []
            params = []
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    # Convert recipient_list to JSON if it's a list
                    if field == 'recipient_list' and isinstance(value, list):
                        import json
                        value = json.dumps(value)
                    updates.append(f"{field} = %s")
                    params.append(value)
            
            if not updates:
                return False
            
            updates.append("updated_at = NOW()")
            params.append(schedule_id)
            
            query = f"""
                UPDATE email_schedules 
                SET {', '.join(updates)}
                WHERE id = %s
            """
            cursor.execute(query, params)
            
            self.connection.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            logger.info(f"Schedule {schedule_id} updated")
            return rows_affected > 0
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
            rows_affected = cursor.rowcount
            cursor.close()
            logger.info(f"Schedule {schedule_id} deleted")
            return rows_affected > 0
        except Error as e:
            logger.error(f"Error deleting schedule: {e}")
            self.connection.rollback()
            return False
    
    # ==================== USER AUTHENTICATION METHODS ====================
    
    def create_user(self, username, email, password, full_name=None):
        """Create a new user account"""
        try:
            cursor = self.connection.cursor()
            
            # Hash the password
            password_hash = generate_password_hash(password)
            
            query = """
                INSERT INTO users 
                (username, email, password_hash, full_name, is_active, role, created_at, updated_at)
                VALUES (%s, %s, %s, %s, TRUE, 'user', NOW(), NOW())
            """
            cursor.execute(query, (username, email, password_hash, full_name))
            
            self.connection.commit()
            user_id = cursor.lastrowid
            cursor.close()
            logger.info(f"User '{username}' created with ID {user_id}")
            return user_id
        except Error as e:
            logger.error(f"Error creating user: {e}")
            self.connection.rollback()
            return None
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT id, username, email, full_name, role FROM users WHERE id = %s AND is_active = TRUE"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return User(result['id'], result['username'], result['email'], 
                          result['full_name'], result['role'])
            return None
        except Error as e:
            logger.error(f"Error getting user by ID: {e}")
            return None
    
    def get_user_by_username(self, username):
        """Get user by username or email"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT id, username, email, password_hash, full_name, role, is_active
                FROM users 
                WHERE (username = %s OR email = %s) AND is_active = TRUE
                LIMIT 1
            """
            cursor.execute(query, (username, username))
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    def verify_user_password(self, username, password):
        """Verify user password and return user object if valid"""
        user_data = self.get_user_by_username(username)
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            # Update last login
            try:
                cursor = self.connection.cursor()
                query = "UPDATE users SET last_login = NOW() WHERE id = %s"
                cursor.execute(query, (user_data['id'],))
                self.connection.commit()
                cursor.close()
            except Error as e:
                logger.error(f"Error updating last_login: {e}")
            
            return User(user_data['id'], user_data['username'], user_data['email'], 
                       user_data['full_name'], user_data['role'])
        
        return None
    
    def user_exists(self, username, email):
        """Check if username or email already exists"""
        try:
            cursor = self.connection.cursor()
            query = "SELECT id FROM users WHERE username = %s OR email = %s LIMIT 1"
            cursor.execute(query, (username, email))
            result = cursor.fetchone()
            cursor.close()
            return result is not None
        except Error as e:
            logger.error(f"Error checking user existence: {e}")
            return False


# Initialize database helper - but don't use globally
# db = DashboardDB()


# Routes


# ==================== AUTHENTICATION ROUTES ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and handler"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        return api_login()
    
    return render_template('login.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint for user login"""
    db = None
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        remember_me = data.get('remember_me', False)
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password required'}), 400
        
        db = DashboardDB()
        db.connect()
        
        user = db.verify_user_password(username, password)
        
        if user:
            login_user(user, remember=remember_me)
            logger.info(f"User '{username}' logged in successfully")
            return jsonify({'success': True, 'message': 'Login successful', 'user_id': user.id})
        else:
            logger.warning(f"Failed login attempt for '{username}'")
            return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
    
    except Exception as e:
        logger.error(f"Error in login: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/register', methods=['POST'])
def api_register():
    """API endpoint for user registration"""
    db = None
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        # Validation
        if not username or len(username) < 3:
            return jsonify({'success': False, 'error': 'Username must be at least 3 characters'}), 400
        
        if not email or '@' not in email:
            return jsonify({'success': False, 'error': 'Valid email is required'}), 400
        
        if not password or len(password) < 8:
            return jsonify({'success': False, 'error': 'Password must be at least 8 characters'}), 400
        
        db = DashboardDB()
        db.connect()
        
        # Check if user already exists
        if db.user_exists(username, email):
            return jsonify({'success': False, 'error': 'Username or email already exists'}), 409
        
        # Create user
        user_id = db.create_user(username, email, password, full_name)
        
        if user_id:
            # Auto-login after registration
            user = db.get_user_by_id(user_id)
            if user:
                login_user(user, remember=True)
                logger.info(f"New user '{username}' registered and logged in")
                return jsonify({'success': True, 'message': 'Registration successful', 'user_id': user_id})
        
        return jsonify({'success': False, 'error': 'Failed to create user account'}), 500
    
    except Exception as e:
        logger.error(f"Error in registration: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/current-user', methods=['GET'])
@login_required
def api_current_user():
    """API endpoint to get current user information"""
    return jsonify({
        'success': True,
        'user_id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'full_name': current_user.full_name or current_user.username
    })


@app.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    """API endpoint for user logout"""
    username = current_user.username
    logout_user()
    logger.info(f"User '{username}' logged out")
    return jsonify({'success': True, 'message': 'Logged out successfully'})


@app.route('/logout')
@login_required
def logout():
    """Logout page"""
    username = current_user.username
    logout_user()
    logger.info(f"User '{username}' logged out")
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """Main dashboard page"""
    return render_template('index.html')



@app.route('/api/stats')
def get_stats():
    """API endpoint for statistics"""
    db = None
    try:
        db = DashboardDB()
        db.connect()
        stats = db.get_stats()
        daily_stats = db.get_daily_stats()
        
        # Provide defaults if stats are None
        if stats is None:
            stats = {
                'total': 0,
                'pending': 0,
                'sent': 0,
                'failed': 0,
                'bounced': 0
            }
        
        if daily_stats is None:
            daily_stats = {
                'date': datetime.now().date(),
                'total': 0,
                'sent': 0,
                'failed': 0,
                'bounced': 0,
                'pending': 0
            }
        
        return jsonify({
            'success': True,
            'overall': stats,
            'today': daily_stats
        })
    except Exception as e:
        logger.error(f"Error in /api/stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/emails')
def get_emails():
    """API endpoint for emails list"""
    db = None
    try:
        status = request.args.get('status', None)
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit
        
        db = DashboardDB()
        db.connect()
        emails = db.get_emails(status=status, limit=limit, offset=offset)
        total = db.get_email_count(status=status)
        
        return jsonify({
            'success': True,
            'emails': emails,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        })
    except Exception as e:
        logger.error(f"Error in /api/emails: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/email/<int:email_id>', methods=['GET', 'DELETE'])
def manage_email(email_id):
    """Get or delete specific email"""
    db = None
    try:
        db = DashboardDB()
        db.connect()
        
        if request.method == 'DELETE':
            result = db.delete_email(email_id)
            return jsonify({'success': result, 'message': 'Email deleted' if result else 'Failed to delete'})
        
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM emails WHERE id = %s", (email_id,))
        email = cursor.fetchone()
        cursor.close()
        
        if not email:
            return jsonify({'success': False, 'error': 'Email not found'}), 404
        
        return jsonify({'success': True, 'email': email})
    except Exception as e:
        logger.error(f"Error in /api/email/{email_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/email/<int:email_id>/status', methods=['PUT'])
def update_email_status(email_id):
    """Update email status"""
    db = None
    try:
        data = request.get_json()
        status = data.get('status')
        error_message = data.get('error_message')
        
        if not status:
            return jsonify({'success': False, 'error': 'Status required'}), 400
        
        db = DashboardDB()
        db.connect()
        result = db.update_email_status(email_id, status, error_message)
        
        return jsonify({'success': result, 'message': 'Status updated' if result else 'Failed to update'})
    except Exception as e:
        logger.error(f"Error updating status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/emails/bulk-update', methods=['POST'])
def bulk_update():
    """Bulk update email statuses"""
    db = None
    try:
        data = request.get_json()
        email_ids = data.get('email_ids', [])
        status = data.get('status')
        
        if not email_ids or not status:
            return jsonify({'success': False, 'error': 'email_ids and status required'}), 400
        
        db = DashboardDB()
        db.connect()
        result = db.bulk_update_status(email_ids, status)
        
        return jsonify({'success': result, 'message': f'Updated {len(email_ids)} emails' if result else 'Failed to update'})
    except Exception as e:
        logger.error(f"Error in bulk update: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/validate-email', methods=['POST'])
def validate_email_endpoint():
    """Validate email address(es)
    
    Request JSON:
    {
        "email": "user@example.com",  // single email
        OR
        "emails": ["email1@example.com", "email2@example.com"],  // multiple emails
        "level": "syntax"  // quick, syntax, or full (optional, default: syntax)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Handle single email or batch of emails
        emails_to_validate = []
        if 'email' in data:
            emails_to_validate = [data['email']]
        elif 'emails' in data:
            emails_to_validate = data['emails'] if isinstance(data['emails'], list) else [data['emails']]
        else:
            return jsonify({'success': False, 'error': 'No email or emails field provided'}), 400
        
        # Get validation level (quick, syntax, or full)
        validation_level = data.get('level', 'syntax')
        if validation_level not in ['quick', 'syntax', 'full']:
            validation_level = 'syntax'
        
        # Validate all emails
        results = []
        all_valid = True
        
        for email in emails_to_validate:
            result = validate_email(email.strip(), level=validation_level)
            results.append({
                'email': email.strip(),
                'valid': result['valid'],
                'syntax_valid': result['syntax_valid'],
                'syntax_message': result['syntax_message'],
                'warnings': result.get('warnings', []),
                'suggestions': result.get('suggestions', []),
                'overall_message': result['overall_message'],
                'mx_valid': result.get('mx_valid'),
                'is_disposable': result.get('is_disposable')
            })
            
            if not result['valid']:
                all_valid = False
        
        logger.info(f"Validated {len(results)} email(s): {sum(1 for r in results if r['valid'])}/{len(results)} valid")
        
        return jsonify({
            'success': True,
            'all_valid': all_valid,
            'results': results if len(results) > 1 else results[0],
            'count': len(results)
        })
        
    except Exception as e:
        logger.error(f"Error validating email: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health')
def health():
    """Health check endpoint"""
    db = None
    try:
        db = DashboardDB()
        db.connect()
        if db.connection:
            return jsonify({'status': 'healthy'})
        else:
            return jsonify({'status': 'unhealthy'}), 500
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/config')
def get_config():
    """Get current configuration"""
    try:
        from config import BATCH_SIZE, DAILY_LIMIT, BATCH_DELAY, SMTP_CONFIG
        
        return jsonify({
            'success': True,
            'config': {
                'batch_size': BATCH_SIZE,
                'daily_limit': DAILY_LIMIT,
                'batch_delay': BATCH_DELAY,
                'smtp_host': SMTP_CONFIG['host'],
                'smtp_port': SMTP_CONFIG['port'],
                'from_email': SMTP_CONFIG['from_email']
            }
        })
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/config', methods=['PUT'])
def update_config():
    """Update configuration in .env file"""
    try:
        data = request.get_json()
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        
        # Read current .env file
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Update values
        updates = {
            'BATCH_SIZE': data.get('batch_size'),
            'DAILY_LIMIT': data.get('daily_limit'),
            'BATCH_DELAY': data.get('batch_delay')
        }
        
        new_lines = []
        for line in lines:
            updated = False
            for key, value in updates.items():
                if value is not None and line.startswith(f'{key}='):
                    new_lines.append(f'{key}={value}\n')
                    updated = True
                    break
            if not updated:
                new_lines.append(line)
        
        # Write back to .env
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
        
        logger.info(f"Configuration updated: {updates}")
        return jsonify({
            'success': True,
            'message': 'Configuration updated. Restart email sender for changes to take effect.'
        })
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/send-now', methods=['POST'])
def send_now():
    """Trigger manual email sending"""
    try:
        data = request.get_json()
        limit = data.get('limit', 10) if data else 10
        
        # Optional: validate email if provided for manual sending
        recipients = data.get('recipients') if data else None
        if recipients:
            if isinstance(recipients, str):
                recipients = [recipients]
            
            invalid_emails = []
            for email in recipients:
                result = validate_email(email.strip(), level='syntax')
                if not result['valid']:
                    invalid_emails.append({
                        'email': email,
                        'error': result['syntax_message']
                    })
            
            if invalid_emails:
                logger.warning(f"Found {len(invalid_emails)} invalid email(s): {invalid_emails}")
                return jsonify({
                    'success': False,
                    'error': 'Some email addresses are invalid',
                    'invalid_emails': invalid_emails
                }), 400
        
        import subprocess
        import sys
        
        # Get the Python executable path
        python_path = sys.executable
        script_path = os.path.join(os.path.dirname(__file__), 'email_sender.py')
        
        # Run email sender with custom batch size
        logger.info(f"Manually triggering email send for {limit} emails")
        
        # Create a temporary config override
        env_override = os.environ.copy()
        env_override['BATCH_SIZE'] = str(limit)
        env_override['DAILY_LIMIT'] = str(limit)
        
        # Run the email sender
        result = subprocess.run(
            [python_path, script_path, '--once'],
            env=env_override,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            # Parse output for sent count
            output = result.stdout
            logger.info(f"Manual send output: {output}")
            
            return jsonify({
                'success': True,
                'message': f'Email sending triggered for up to {limit} emails',
                'output': output
            })
        else:
            logger.error(f"Manual send failed: {result.stderr}")
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Email sending timed out (>60s)'
        }), 500
    except Exception as e:
        logger.error(f"Error triggering manual send: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/test-smtp', methods=['POST'])
def test_smtp():
    """Test SMTP connection and send a test email"""
    try:
        data = request.get_json()
        test_email = data.get('test_email') if data else None
        
        from smtp_helper import SMTPConnection
        from config import SMTP_CONFIG
        
        smtp = SMTPConnection()
        
        # Test 1: Connect to SMTP server
        logger.info("Testing SMTP connection...")
        try:
            smtp.connect()
            connection_status = "✓ Successfully connected to SMTP server"
            logger.info(connection_status)
        except Exception as e:
            error_msg = f"✗ Failed to connect to SMTP server: {str(e)}"
            logger.error(error_msg)
            return jsonify({
                'success': False,
                'error': error_msg,
                'details': {
                    'connection': False,
                    'send': False
                }
            })
        
        # Test 2: Send test email if email address provided
        send_status = None
        if test_email:
            logger.info(f"Sending test email to {test_email}...")
            try:
                subject = "Test Email from Email System Dashboard"
                body = f"""
This is a test email from your Email System Dashboard.

If you received this email, your SMTP configuration is working correctly!

Configuration Details:
- SMTP Host: {SMTP_CONFIG['host']}
- SMTP Port: {SMTP_CONFIG['port']}
- From Email: {SMTP_CONFIG['from_email']}
- Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is an automated test message.
                """.strip()
                
                success, error = smtp.send_email(test_email, subject, body)
                
                if success:
                    send_status = f"✓ Test email successfully sent to {test_email}"
                    logger.info(send_status)
                else:
                    send_status = f"✗ Failed to send test email: {error}"
                    logger.error(send_status)
                    smtp.disconnect()
                    return jsonify({
                        'success': False,
                        'error': send_status,
                        'details': {
                            'connection': True,
                            'send': False
                        }
                    })
            except Exception as e:
                send_status = f"✗ Error sending test email: {str(e)}"
                logger.error(send_status)
                smtp.disconnect()
                return jsonify({
                    'success': False,
                    'error': send_status,
                    'details': {
                        'connection': True,
                        'send': False
                    }
                })
        
        smtp.disconnect()
        
        result_message = connection_status
        if send_status:
            result_message += "\n" + send_status
        
        return jsonify({
            'success': True,
            'message': result_message,
            'details': {
                'connection': True,
                'send': bool(send_status and '✓' in send_status),
                'smtp_host': SMTP_CONFIG['host'],
                'smtp_port': SMTP_CONFIG['port'],
                'from_email': SMTP_CONFIG['from_email']
            }
        })
        
    except Exception as e:
        logger.error(f"Error testing SMTP: {e}")
        return jsonify({
            'success': False,
            'error': f"Error testing SMTP: {str(e)}",
            'details': {
                'connection': False,
                'send': False
            }
        }), 500


@app.route('/api/validation/stats', methods=['GET'])
def get_validation_stats():
    """Get email validation statistics"""
    db = None
    try:
        db = DashboardDB()
        db.connect()
        stats = db.get_validation_statistics()
        
        if not stats:
            stats = {
                'total': 0,
                'unchecked': 0,
                'valid': 0,
                'invalid': 0,
                'needs_review': 0
            }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f"Error getting validation stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/validation/emails', methods=['GET'])
def get_validation_emails():
    """Get emails by validation status"""
    db = None
    try:
        status = request.args.get('status', 'unchecked')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        offset = (page - 1) * limit
        
        db = DashboardDB()
        db.connect()
        emails = db.get_emails_for_validation(status, limit, offset)
        total = db.get_validation_count(status)
        
        # If json strings, parse them
        for email in emails:
            if email.get('validation_notes'):
                try:
                    import json
                    email['validation_notes'] = json.loads(email['validation_notes']) if isinstance(email['validation_notes'], str) else email['validation_notes']
                except:
                    pass
        
        return jsonify({
            'success': True,
            'emails': emails,
            'total': total,
            'page': page,
            'pages': (total + limit - 1) // limit
        })
    except Exception as e:
        logger.error(f"Error in /api/validation/emails: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/validation/validate-batch', methods=['POST'])
def validate_batch():
    """Run batch email validation on database emails"""
    db = None
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        validation_status = data.get('validation_status', 'unchecked')
        limit = data.get('limit', 100)
        level = data.get('level', 'syntax')
        
        from email_validator import validate_email as validator_func
        
        db = DashboardDB()
        db.connect()
        
        # Fetch emails to validate
        emails = db.get_emails_for_validation(validation_status, limit=limit)
        
        if not emails:
            return jsonify({
                'success': True,
                'message': f'No emails found with status: {validation_status}',
                'validated': 0,
                'errors': 0
            })
        
        logger.info(f"Starting batch validation of {len(emails)} emails (level: {level})")
        
        validated_count = 0
        error_count = 0
        results = []
        
        for email in emails:
            try:
                email_address = email['recipient']
                
                # Validate email
                result = validator_func(email_address, level=level)
                
                # Determine validation status
                if result['valid']:
                    val_status = 'valid'
                    if result.get('warnings'):
                        val_status = 'needs_review'
                else:
                    val_status = 'invalid'
                
                # Prepare validation notes
                validation_notes = {
                    'syntax_valid': result['syntax_valid'],
                    'syntax_message': result['syntax_message'],
                    'warnings': result.get('warnings', []),
                    'suggestions': result.get('suggestions', []),
                    'is_disposable': result.get('is_disposable'),
                    'mx_valid': result.get('mx_valid'),
                    'overall_message': result['overall_message']
                }
                
                # Save validation result
                db.save_validation_result(email['id'], val_status, validation_notes)
                
                results.append({
                    'id': email['id'],
                    'recipient': email_address,
                    'status': val_status,
                    'warnings': result.get('warnings', [])
                })
                
                validated_count += 1
                
            except Exception as e:
                logger.error(f"Error validating email {email['id']}: {e}")
                error_count += 1
        
        logger.info(f"Batch validation complete: {validated_count} validated, {error_count} errors")
        
        return jsonify({
            'success': True,
            'message': f'Validated {validated_count} emails',
            'validated': validated_count,
            'errors': error_count,
            'total': len(emails),
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in batch validation: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


# ===================== TEMPLATE MANAGEMENT ENDPOINTS =====================

@app.route('/api/templates', methods=['GET', 'POST'])
def manage_templates():
    """Get all templates or create a new template"""
    db = None
    try:
        db = DashboardDB()
        db.connect()
        
        if request.method == 'POST':
            data = request.get_json()
            
            if not data or 'name' not in data or 'subject' not in data or 'body' not in data:
                return jsonify({'success': False, 'error': 'name, subject, and body required'}), 400
            
            template_id = db.create_template(
                name=data['name'],
                subject=data['subject'],
                body=data['body'],
                html_body=data.get('html_body'),
                plain_text=data.get('plain_text'),
                tags=data.get('tags')
            )
            
            if template_id:
                return jsonify({
                    'success': True,
                    'template_id': template_id,
                    'message': f'Template "{data["name"]}" created successfully'
                }), 201
            else:
                return jsonify({'success': False, 'error': 'Failed to create template'}), 500
        
        else:  # GET
            templates = db.get_all_templates()
            return jsonify({
                'success': True,
                'templates': templates,
                'count': len(templates)
            })
    
    except Exception as e:
        logger.error(f"Error managing templates: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/templates/<int:template_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_template(template_id):
    """Get, update, or delete a specific template"""
    db = None
    try:
        db = DashboardDB()
        db.connect()
        
        if request.method == 'GET':
            template = db.get_template(template_id)
            if not template:
                return jsonify({'success': False, 'error': 'Template not found'}), 404
            return jsonify({'success': True, 'template': template})
        
        elif request.method == 'PUT':
            data = request.get_json()
            success = db.update_template(template_id, **data)
            
            if success:
                return jsonify({'success': True, 'message': 'Template updated'})
            else:
                return jsonify({'success': False, 'error': 'Failed to update template'}), 500
        
        elif request.method == 'DELETE':
            success = db.delete_template(template_id)
            if success:
                return jsonify({'success': True, 'message': 'Template deleted'})
            else:
                return jsonify({'success': False, 'error': 'Failed to delete template'}), 500
    
    except Exception as e:
        logger.error(f"Error managing template {template_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/templates/<int:template_id>/preview', methods=['GET'])
def preview_template(template_id):
    """Get template preview"""
    db = None
    try:
        db = DashboardDB()
        db.connect()
        
        template = db.get_template(template_id)
        if not template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        return jsonify({
            'success': True,
            'template': {
                'name': template['name'],
                'subject': template['subject'],
                'body': template['body'],
                'html_body': template.get('html_body'),
                'plain_text': template.get('plain_text')
            }
        })
    
    except Exception as e:
        logger.error(f"Error previewing template: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


# ===================== SCHEDULER MANAGEMENT ENDPOINTS =====================

import csv
from io import StringIO
from flask import request

@app.route('/api/scheduler/upload-csv', methods=['POST'])
@login_required
def upload_scheduler_csv():
    """Upload CSV file and insert emails into database"""
    db = None
    try:
        if 'csv' not in request.files:
            return jsonify({'success': False, 'error': 'No CSV file uploaded'}), 400

        file = request.files['csv']
        if not file or not file.filename.lower().endswith('.csv'):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400

        content = file.read().decode('utf-8', errors='ignore')
        reader = csv.DictReader(StringIO(content))
        emails = set()
        for row in reader:
            if 'recipient' in row and row['recipient']:
                emails.add(row['recipient'].strip())
            else:
                # fallback: if only one column, treat as email
                for v in row.values():
                    if v and '@' in v:
                        emails.add(v.strip())

        # If no header, try simple line split
        if not emails and content:
            for line in content.splitlines():
                line = line.strip()
                if '@' in line:
                    emails.add(line)

        if not emails:
            return jsonify({'success': False, 'error': 'No valid email addresses found in CSV'}), 400

        db = DashboardDB()
        db.connect()
        cursor = db.connection.cursor()
        inserted = 0
        for email in emails:
            try:
                cursor.execute("INSERT INTO emails (recipient, status, created_at, updated_at) VALUES (%s, 'pending', NOW(), NOW())", (email,))
                inserted += 1
            except Exception as e:
                db.connection.rollback()
                continue
        db.connection.commit()
        cursor.close()
        db.disconnect()

        return jsonify({'success': True, 'inserted': inserted, 'emails': list(emails)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/scheduler/recipients', methods=['GET'])
def get_scheduler_recipients():
    """Get unique recipients from emails table for scheduler selection"""
    db = None
    try:
        limit = int(request.args.get('limit', 1000))
        validation_status = request.args.get('validation_status', '').strip() or None

        if limit <= 0:
            limit = 1000
        if limit > 5000:
            limit = 5000

        db = DashboardDB()
        db.connect()
        recipients = db.get_scheduler_recipients(limit=limit, validation_status=validation_status)

        return jsonify({
            'success': True,
            'recipients': recipients,
            'count': len(recipients),
            'validation_status': validation_status
        })
    except Exception as e:
        logger.error(f"Error getting scheduler recipients: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()

@app.route('/api/schedules', methods=['GET', 'POST'])
def manage_schedules():
    """Get all schedules or create a new schedule"""
    db = None
    try:
        db = DashboardDB()
        db.connect()
        
        if request.method == 'POST':
            data = request.get_json()
            
            required_fields = ['name', 'recipient_list', 'schedule_type']
            if not data or not all(f in data for f in required_fields):
                return jsonify({'success': False, 'error': f'{", ".join(required_fields)} required'}), 400
            
            schedule_id = db.create_schedule(
                name=data['name'],
                template_id=data.get('template_id'),
                recipient_list=data['recipient_list'],
                schedule_type=data['schedule_type'],
                schedule_time=data.get('schedule_time'),
                schedule_day=data.get('schedule_day'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                created_by=data.get('created_by', 'admin'),
                notes=data.get('notes')
            )
            
            if schedule_id:
                return jsonify({
                    'success': True,
                    'schedule_id': schedule_id,
                    'message': f'Schedule "{data["name"]}" created successfully'
                }), 201
            else:
                return jsonify({'success': False, 'error': 'Failed to create schedule'}), 500
        
        else:  # GET
            schedules = db.get_all_schedules()
            return jsonify({
                'success': True,
                'schedules': schedules,
                'count': len(schedules)
            })
    
    except Exception as e:
        logger.error(f"Error managing schedules: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/schedules/<int:schedule_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_schedule(schedule_id):
    """Get, update, or delete a specific schedule"""
    db = None
    try:
        db = DashboardDB()
        db.connect()
        
        if request.method == 'GET':
            schedule = db.get_schedule(schedule_id)
            if not schedule:
                return jsonify({'success': False, 'error': 'Schedule not found'}), 404
            return jsonify({'success': True, 'schedule': schedule})
        
        elif request.method == 'PUT':
            data = request.get_json()
            success = db.update_schedule(schedule_id, **data)
            
            if success:
                return jsonify({'success': True, 'message': 'Schedule updated'})
            else:
                return jsonify({'success': False, 'error': 'Failed to update schedule'}), 500
        
        elif request.method == 'DELETE':
            success = db.delete_schedule(schedule_id)
            if success:
                return jsonify({'success': True, 'message': 'Schedule deleted'})
            else:
                return jsonify({'success': False, 'error': 'Failed to delete schedule'}), 500
    
    except Exception as e:
        logger.error(f"Error managing schedule {schedule_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/schedules/<int:schedule_id>/activate', methods=['POST'])
def activate_schedule(schedule_id):
    """Activate a schedule"""
    db = None
    try:
        db = DashboardDB()
        db.connect()
        
        success = db.update_schedule(schedule_id, is_active=True, status='scheduled')
        
        if success:
            return jsonify({'success': True, 'message': 'Schedule activated'})
        else:
            return jsonify({'success': False, 'error': 'Failed to activate schedule'}), 500
    
    except Exception as e:
        logger.error(f"Error activating schedule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


@app.route('/api/schedules/<int:schedule_id>/deactivate', methods=['POST'])
def deactivate_schedule(schedule_id):
    """Deactivate a schedule"""
    db = None
    try:
        db = DashboardDB()
        db.connect()
        
        success = db.update_schedule(schedule_id, is_active=False, status='paused')
        
        if success:
            return jsonify({'success': True, 'message': 'Schedule deactivated'})
        else:
            return jsonify({'success': False, 'error': 'Failed to deactivate schedule'}), 500
    
    except Exception as e:
        logger.error(f"Error deactivating schedule: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            db.disconnect()


if __name__ == '__main__':
    logger.info("Starting Email Dashboard...")
    # Use environment to determine debug mode
    debug_mode = os.getenv('FLASK_ENV', 'production') != 'production'
    port = int(os.getenv('PORT', 5001))
    app.run(debug=debug_mode, host='0.0.0.0', port=port)

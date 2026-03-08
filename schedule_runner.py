"""
Email Schedule Runner
Continuously checks and executes scheduled email campaigns
"""
import time
import logging
from datetime import datetime, timedelta
import json
from db_helper import DatabaseConnection
from smtp_helper import SMTPConnection
from config import LOG_LEVEL, LOG_FILE

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ScheduleRunner:
    """Manages and executes scheduled email campaigns"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.smtp = SMTPConnection()
    
    def get_due_schedules(self):
        """Get schedules that are due to run"""
        try:
            self.db.connect()
            cursor = self.db.connection.cursor(dictionary=True)
            
            now = datetime.now()
            current_time = now.strftime('%H:%M:%S')
            current_date = now.date()
            
            # Get active schedules that are due to run
            query = """
                SELECT s.*, t.subject, t.body, t.html_body, t.name as template_name
                FROM email_schedules s
                LEFT JOIN email_templates t ON s.template_id = t.id
                WHERE s.is_active = TRUE
                AND s.status IN ('draft', 'scheduled')
                AND (s.start_date IS NULL OR s.start_date <= %s)
                AND (s.end_date IS NULL OR s.end_date >= %s)
                AND (
                    (s.schedule_type = 'once' AND s.next_run IS NULL)
                    OR (s.schedule_type IN ('daily', 'recurring') AND (s.next_run IS NULL OR s.next_run <= NOW()))
                )
            """
            
            cursor.execute(query, (current_date, current_date))
            schedules = cursor.fetchall()
            cursor.close()
            
            # Filter schedules based on time
            due_schedules = []
            for schedule in schedules:
                schedule_time = schedule.get('schedule_time')
                if schedule_time:
                    # Convert timedelta to string if needed
                    if hasattr(schedule_time, 'total_seconds'):
                        total_seconds = int(schedule_time.total_seconds())
                        hours = total_seconds // 3600
                        minutes = (total_seconds % 3600) // 60
                        schedule_time_str = f"{hours:02d}:{minutes:02d}"
                    else:
                        schedule_time_str = str(schedule_time)[:5]  # Get HH:MM
                    
                    # Check if current time matches schedule time (within 2 minute window)
                    current_hour_min = current_time[:5]  # Get HH:MM
                    
                    if schedule_time_str == current_hour_min or schedule.get('next_run') and schedule['next_run'] <= now:
                        due_schedules.append(schedule)
                else:
                    due_schedules.append(schedule)
            
            return due_schedules
        except Exception as e:
            logger.error(f"Error getting due schedules: {e}")
            return []
        finally:
            if self.db.connection:
                self.db.disconnect()
    
    def execute_schedule(self, schedule):
        """Execute a schedule by sending emails to all recipients"""
        schedule_id = schedule['id']
        schedule_name = schedule['name']
        
        try:
            logger.info(f"Executing schedule: {schedule_name} (ID: {schedule_id})")
            
            # Update status to running
            self.db.connect()
            cursor = self.db.connection.cursor()
            cursor.execute("UPDATE email_schedules SET status = 'running', last_run = NOW() WHERE id = %s", (schedule_id,))
            self.db.connection.commit()
            cursor.close()
            
            # Parse recipient list
            recipient_list = schedule.get('recipient_list', [])
            if isinstance(recipient_list, str):
                try:
                    recipient_list = json.loads(recipient_list)
                except:
                    recipient_list = []
            
            if not recipient_list:
                logger.warning(f"No recipients found for schedule {schedule_id}")
                cursor = self.db.connection.cursor()
                cursor.execute("UPDATE email_schedules SET status = 'failed' WHERE id = %s", (schedule_id,))
                self.db.connection.commit()
                cursor.close()
                return
            
            # Get email template details
            subject = schedule.get('subject', 'Scheduled Email')
            body = schedule.get('html_body') or schedule.get('body', '')
            
            if not body:
                logger.warning(f"No email content found for schedule {schedule_id}")
                cursor = self.db.connection.cursor()
                cursor.execute("UPDATE email_schedules SET status = 'failed' WHERE id = %s", (schedule_id,))
                self.db.connection.commit()
                cursor.close()
                return
            
            # Send emails
            self.smtp.connect()
            sent_count = 0
            failed_count = 0
            
            for recipient in recipient_list:
                try:
                    logger.info(f"Sending email to {recipient}")
                    success, error_msg = self.smtp.send_email(recipient, subject, body)
                    
                    if success:
                        sent_count += 1
                        # Log to schedule_logs
                        self.log_schedule_execution(schedule_id, recipient, 'success')
                    else:
                        failed_count += 1
                        self.log_schedule_execution(schedule_id, recipient, 'failed', error_msg)
                    
                    # Small delay between emails
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"Error sending to {recipient}: {e}")
                    failed_count += 1
                    self.log_schedule_execution(schedule_id, recipient, 'failed', str(e))
            
            self.smtp.disconnect()
            
            # Update schedule with results
            cursor = self.db.connection.cursor()
            
            # Calculate next run time
            next_run = self.calculate_next_run(schedule)
            
            # Update schedule status
            if schedule['schedule_type'] == 'once':
                status = 'completed'
                cursor.execute("""
                    UPDATE email_schedules 
                    SET status = %s, sent_count = sent_count + %s, 
                        failed_count = failed_count + %s, is_active = FALSE
                    WHERE id = %s
                """, (status, sent_count, failed_count, schedule_id))
            else:
                status = 'scheduled'
                cursor.execute("""
                    UPDATE email_schedules 
                    SET status = %s, sent_count = sent_count + %s, 
                        failed_count = failed_count + %s, next_run = %s
                    WHERE id = %s
                """, (status, sent_count, failed_count, next_run, schedule_id))
            
            self.db.connection.commit()
            cursor.close()
            
            logger.info(f"Schedule {schedule_id} executed: {sent_count} sent, {failed_count} failed")
            
        except Exception as e:
            logger.error(f"Error executing schedule {schedule_id}: {e}")
            # Mark schedule as failed
            try:
                cursor = self.db.connection.cursor()
                cursor.execute("UPDATE email_schedules SET status = 'failed' WHERE id = %s", (schedule_id,))
                self.db.connection.commit()
                cursor.close()
            except:
                pass
        finally:
            if self.db.connection:
                self.db.disconnect()
    
    def calculate_next_run(self, schedule):
        """Calculate next run time based on schedule type"""
        schedule_type = schedule['schedule_type']
        
        if schedule_type == 'once':
            return None
        
        now = datetime.now()
        
        if schedule_type == 'daily':
            # Run next day at the same time
            schedule_time = schedule.get('schedule_time')
            if schedule_time:
                if hasattr(schedule_time, 'total_seconds'):
                    total_seconds = int(schedule_time.total_seconds())
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    next_run = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                    next_run += timedelta(days=1)
                else:
                    # Parse time string
                    time_parts = str(schedule_time).split(':')
                    hours = int(time_parts[0])
                    minutes = int(time_parts[1]) if len(time_parts) > 1 else 0
                    next_run = now.replace(hour=hours, minute=minutes, second=0, microsecond=0)
                    next_run += timedelta(days=1)
                
                return next_run
        
        elif schedule_type == 'weekly':
            # Run next week on the same day
            return now + timedelta(days=7)
        
        elif schedule_type == 'monthly':
            # Run next month on the same day
            return now + timedelta(days=30)
        
        return None
    
    def log_schedule_execution(self, schedule_id, recipient_email, status, error_message=None):
        """Log schedule execution to schedule_logs table"""
        try:
            cursor = self.db.connection.cursor()
            query = """
                INSERT INTO schedule_logs 
                (schedule_id, recipient_email, status, error_message, executed_at)
                VALUES (%s, %s, %s, %s, NOW())
            """
            cursor.execute(query, (schedule_id, recipient_email, status, error_message))
            self.db.connection.commit()
            cursor.close()
        except Exception as e:
            logger.error(f"Error logging schedule execution: {e}")
    
    def run(self, check_interval=60):
        """
        Main loop - continuously check and execute due schedules
        
        Args:
            check_interval: seconds between checks (default: 60)
        """
        logger.info("Schedule runner started")
        logger.info(f"Checking for due schedules every {check_interval} seconds")
        
        try:
            while True:
                try:
                    # Get schedules that are due
                    due_schedules = self.get_due_schedules()
                    
                    if due_schedules:
                        logger.info(f"Found {len(due_schedules)} schedule(s) to execute")
                        for schedule in due_schedules:
                            self.execute_schedule(schedule)
                    
                    # Wait before next check
                    time.sleep(check_interval)
                    
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    time.sleep(check_interval)
                    
        except KeyboardInterrupt:
            logger.info("Schedule runner stopped by user")


if __name__ == '__main__':
    import sys
    
    runner = ScheduleRunner()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--once':
            # Run once and exit (for testing)
            schedules = runner.get_due_schedules()
            logger.info(f"Found {len(schedules)} due schedule(s)")
            for schedule in schedules:
                runner.execute_schedule(schedule)
        else:
            # Custom check interval
            interval = int(sys.argv[1])
            runner.run(check_interval=interval)
    else:
        # Default: check every 60 seconds
        runner.run()

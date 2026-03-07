"""
Main email sending scheduler
Sends emails in batches with status tracking
"""
import time
import logging
import schedule
from datetime import datetime
from config import BATCH_SIZE, DAILY_LIMIT, BATCH_DELAY, LOG_LEVEL, LOG_FILE
from db_helper import DatabaseConnection
from smtp_helper import SMTPConnection

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EmailSender:
    """Main email sending orchestrator"""
    
    def __init__(self):
        self.db = DatabaseConnection()
        self.smtp = SMTPConnection()
        self.daily_sent = 0
        self.daily_failed = 0
    
    def send_batch(self):
        """Send one batch of emails"""
        try:
            # Check daily limit
            if self.daily_sent >= DAILY_LIMIT:
                logger.info(f"Daily limit of {DAILY_LIMIT} emails reached")
                return
            
            logger.info("=" * 60)
            logger.info(f"Starting batch send at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Calculate remaining emails for today
            remaining = DAILY_LIMIT - self.daily_sent
            batch_limit = min(BATCH_SIZE, remaining)
            
            # Fetch pending emails
            emails = self.db.get_pending_emails(batch_limit)
            if not emails:
                logger.info("No pending emails found")
                return
            
            logger.info(f"Processing {len(emails)} emails in this batch")
            
            # Send emails
            sent_count = 0
            failed_count = 0
            
            for email in emails:
                email_id = email['id']
                recipient = email['recipient']
                subject = email['subject']
                body = email['body']
                
                logger.info(f"Sending email {email_id} to {recipient}")
                
                # Send email
                success, error_msg = self.smtp.send_email(recipient, subject, body)
                
                if success:
                    self.db.update_email_status(email_id, 'sent')
                    sent_count += 1
                    self.daily_sent += 1
                else:
                    # Determine failure reason
                    status = 'bounced' if 'refused' in error_msg.lower() else 'failed'
                    self.db.update_email_status(email_id, status, error_msg)
                    failed_count += 1
                    self.daily_failed += 1
            
            logger.info(f"Batch complete: {sent_count} sent, {failed_count} failed")
            logger.info(f"Daily total: {self.daily_sent} sent, {self.daily_failed} failed")
            logger.info("=" * 60)
        
        except Exception as e:
            logger.error(f"Error in send_batch: {e}")
    
    def daily_job(self):
        """Scheduled daily job - runs at specified time"""
        logger.info("Starting daily email sending job")
        self.daily_sent = 0
        self.daily_failed = 0
        
        try:
            # Connect to database and SMTP
            self.db.connect()
            self.smtp.connect()
            
            # Send batches with delays
            while self.daily_sent < DAILY_LIMIT:
                self.send_batch()
                
                # Check if more emails to send
                pending_count = len(self.db.get_pending_emails(1))
                if pending_count == 0:
                    logger.info("No more pending emails for today")
                    break
                
                # Wait before next batch
                logger.info(f"Waiting {BATCH_DELAY} seconds before next batch...")
                time.sleep(BATCH_DELAY)
            
            logger.info(f"Daily job complete. Total sent: {self.daily_sent}, Failed: {self.daily_failed}")
        
        except Exception as e:
            logger.error(f"Error in daily_job: {e}")
        
        finally:
            # Cleanup connections
            self.smtp.disconnect()
            self.db.disconnect()
    
    def start_scheduler(self, run_time='09:00'):
        """
        Start the scheduler to run daily job
        
        Args:
            run_time: time to run daily job in HH:MM format (default: 09:00)
        """
        logger.info(f"Scheduler initialized to run daily job at {run_time}")
        schedule.every().day.at(run_time).do(self.daily_job)
        
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
    
    def run_once(self):
        """Run email sending job once (for testing)"""
        logger.info("Running email sending job once")
        self.daily_job()


if __name__ == '__main__':
    import sys
    
    sender = EmailSender()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--once':
            sender.run_once()
        elif sys.argv[1] == '--schedule':
            run_time = sys.argv[2] if len(sys.argv) > 2 else '09:00'
            sender.start_scheduler(run_time)
    else:
        # Default: start scheduler at 09:00
        sender.start_scheduler()

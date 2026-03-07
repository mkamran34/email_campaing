"""
SMTP helper functions for sending emails
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from config import SMTP_CONFIG
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class SMTPConnection:
    """Manages SMTP connection for sending emails"""
    
    def __init__(self):
        self.server = None
    
    def connect(self):
        """Establish SMTP connection"""
        try:
            self.server = smtplib.SMTP(SMTP_CONFIG['host'], SMTP_CONFIG['port'])
            
            if SMTP_CONFIG['use_tls']:
                self.server.starttls()
            
            self.server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
            logger.info("SMTP connection established")
            return self.server
        except smtplib.SMTPException as e:
            logger.error(f"Error connecting to SMTP server: {e}")
            raise
    
    def disconnect(self):
        """Close SMTP connection"""
        if self.server:
            try:
                self.server.quit()
                logger.info("SMTP connection closed")
            except:
                pass
    
    def send_email(self, recipient, subject, body, is_html=False):
        """
        Send an email
        
        Args:
            recipient: recipient email address
            subject: email subject
            body: email body
            is_html: whether body is HTML (default: False)
            
        Returns:
            Tuple of (success: bool, error_message: str or None)
        """
        try:
            msg = MIMEMultipart('alternative')
            
            # Required email headers for better deliverability
            msg['From'] = SMTP_CONFIG['from_email']
            msg['To'] = recipient
            msg['Subject'] = subject
            msg['Message-ID'] = f"<{uuid.uuid4()}@{SMTP_CONFIG['from_email'].split('@')[1]}>"
            msg['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
            msg['X-Mailer'] = 'Email System v1.0'
            msg['X-Priority'] = '3'
            msg['Precedence'] = 'bulk'  # Prevent auto-replies
            
            # Attach body with proper encoding
            mime_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(body, mime_type, 'utf-8'))
            
            # Send email using sendmail for better error handling
            logger.info(f"Attempting to send email: From={SMTP_CONFIG['from_email']}, To={recipient}, Subject={subject}")
            response = self.server.sendmail(
                SMTP_CONFIG['from_email'], 
                recipient, 
                msg.as_string()
            )
            
            # sendmail returns a dict of failed recipients {email: (code, message)}
            if response:
                error_details = '; '.join([f"{email}: {message}" for email, (code, message) in response.items()])
                error_msg = f"SMTP delivery rejected: {error_details}"
                logger.warning(f"Email to {recipient} rejected: {error_msg}")
                return False, error_msg
            
            logger.info(f"Email accepted by SMTP server for {recipient} (Note: does not guarantee delivery to inbox)")
            return True, None
        
        except smtplib.SMTPRecipientsRefused as e:
            error_msg = f"Recipient refused: {str(e)}"
            logger.warning(f"Email to {recipient} rejected by server: {e}")
            return False, error_msg
        
        except smtplib.SMTPSenderRefused as e:
            error_msg = f"Sender refused: {str(e)}"
            logger.warning(f"Sender refused for {recipient}: {e}")
            return False, error_msg
        
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP authentication failed: {str(e)}"
            logger.error(f"SMTP authentication error: {e}")
            return False, error_msg
        
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {str(e)}"
            logger.error(f"SMTP error for {recipient}: {e}")
            return False, error_msg
        
        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            logger.error(f"Error sending email to {recipient}: {e}")
            return False, error_msg

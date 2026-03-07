# Email System - Daily Batch Email Sender

A production-ready Python system to send up to 5,000 emails daily in batches from a MySQL database with automatic delivery status tracking and web dashboard.

## Features

- ✅ Send up to 5,000 emails per day (configurable)
- ✅ Process emails in batches (configurable batch size)
- ✅ Automatic delivery status tracking (sent, failed, bounced)
- ✅ **Web Dashboard** for managing emails and monitoring
- ✅ SMTP support with TLS
- ✅ Daily scheduler with configurable run time
- ✅ Comprehensive logging
- ✅ Error handling and retry logic
- ✅ MySQL database integration

## Project Structure

```
email-system/
├── config.py              # Configuration file (uses .env)
├── .env.example           # Example environment variables
├── requirements.txt       # Python dependencies
├── email_sender.py        # Main scheduler and sending logic
├── db_helper.py          # Database helper functions
├── smtp_helper.py        # SMTP helper functions
├── db_setup.py           # Database schema initialization
├── insert_samples.py     # Insert sample test emails
└── email_system.log      # Log file (generated)
```

## Installation

### 1. Clone/Create the Project

```bash
cd /Users/muhammadkamran/email-system
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and update with your settings:

```bash
cp .env.example .env
```

Edit `.env` with your database and SMTP credentials:

```env
# MySQL
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=email_system

# SMTP (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourdomain.com

# Batch settings
BATCH_SIZE=100          # emails per batch
DAILY_LIMIT=5000        # max emails per day
BATCH_DELAY=60          # seconds between batches
```

### 4. Setup Database

Run the database setup script:

```bash
python db_setup.py
```

This creates two tables:
- `emails`: stores email data and delivery status
- `daily_statistics`: tracks daily sending metrics

### 5. Insert Sample Data (Optional)

For testing, insert sample emails:

```bash
# Insert 100 sample emails
python insert_samples.py 100

# Insert 5000 sample emails
python insert_samples.py 5000
```

## Usage

### Run Once (Testing)

Send emails immediately without scheduling:

```bash
python email_sender.py --once
```

### Run as Daily Scheduler

Start the scheduler (runs at 09:00 by default):

```bash
python email_sender.py --schedule
```

Run at a specific time:

```bash
python email_sender.py --schedule 14:30
```

### Web Dashboard

Start the dashboard web interface:

```bash
python dashboard.py
```

Then open http://localhost:5000 in your browser.

**Dashboard Features:**
- 📊 Real-time statistics (total, pending, sent, failed, bounced emails)
- 📋 Email browser with filtering by status
- 🔍 Search and view email details
- ✏️ Update individual email statuses
- 📦 Bulk operations (mark as sent, delete)
- 📄 Pagination and sorting
- 🔄 Auto-refresh stats every 5 seconds
- 📱 Responsive mobile design

### Database Email Schema

Insert emails into the database:

```sql
INSERT INTO emails (recipient, subject, body, status) VALUES
('user@example.com', 'Welcome!', 'Hello user, welcome to our service!', 'pending');
```

Email fields:
- `id`: Auto-incremented ID
- `recipient`: Email address
- `subject`: Email subject
- `body`: Email body (supports HTML)
- `status`: pending, sent, failed, or bounced
- `error_message`: Error details if failed
- `sent_at`: Timestamp when email was sent
- `created_at`: When email was created
- `updated_at`: Last update time

## Configuration Details

### Batch Settings

- **BATCH_SIZE**: Number of emails to send per batch (default: 100)
- **DAILY_LIMIT**: Maximum emails to send per day (default: 5000)
- **BATCH_DELAY**: Seconds to wait between batches (default: 60)

With defaults: 5000 ÷ 100 = 50 batches, sending 50 batches × 60 seconds = ~50 minutes total

### SMTP Configuration

Supports any SMTP server. Gmail example:

1. Create an [App Password](https://support.google.com/accounts/answer/185833)
2. Add to `.env`:
   ```
   SMTP_USERNAME=your-email@gmail.com
   SMTP_PASSWORD=your-app-password
   ```

## Logging

Logs are written to `email_system.log` and displayed in console:

```
2026-02-27 09:00:01 - email_sender - INFO - Starting daily email sending job
2026-02-27 09:00:02 - email_sender - INFO - Fetched 100 pending emails
2026-02-27 09:00:05 - smtp_helper - DEBUG - Email sent successfully to user@example.com
```

## API Reference

### EmailSender

```python
from email_sender import EmailSender

sender = EmailSender()

# Send emails once
sender.run_once()

# Start scheduler (runs daily at 09:00)
sender.start_scheduler()

# Start scheduler at custom time
sender.start_scheduler('14:30')
```

### DatabaseConnection

```python
from db_helper import DatabaseConnection

db = DatabaseConnection()
db.connect()

# Get pending emails
emails = db.get_pending_emails(limit=100)

# Update status
db.update_email_status(email_id=1, status='sent')
db.update_email_status(email_id=2, status='failed', error_message='Connection timeout')

# Get daily stats
count = db.get_daily_sent_count()

db.disconnect()
```

### SMTPConnection

```python
from smtp_helper import SMTPConnection

smtp = SMTPConnection()
smtp.connect()

# Send email
success, error = smtp.send_email(
    recipient='user@example.com',
    subject='Hello',
    body='Hi there!',
    is_html=False
)

smtp.disconnect()
```

## Dashboard API

The dashboard uses RESTful APIs for data management:

### Statistics Endpoint
```
GET /api/stats
Returns overall and daily statistics
```

### Emails Endpoints
```
GET /api/emails?status=pending&page=1&limit=50
List emails with optional filtering

GET /api/email/<id>
Get specific email details

PUT /api/email/<id>/status
Update email status
{
  "status": "sent",
  "error_message": "optional error"
}

DELETE /api/email/<id>
Delete an email

POST /api/emails/bulk-update
Bulk update multiple emails
{
  "email_ids": [1, 2, 3],
  "status": "sent"
}
```

### Health Check
```
GET /api/health
Check system health
```

## Systemd Service (Linux/Mac)

Create `/etc/systemd/system/email-sender.service`:

```ini
[Unit]
Description=Email Sender Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/Users/muhammadkamran/email-system
ExecStart=/usr/bin/python3 /Users/muhammadkamran/email-system/email_sender.py --schedule
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then run:

```bash
sudo systemctl enable email-sender
sudo systemctl start email-sender
sudo systemctl status email-sender
```

## Troubleshooting

### Connection Error
Ensure MySQL and SMTP servers are running and credentials are correct in `.env`

### SMTP Authentication Failed
Check your SMTP username/password and ensure TLS/SSL settings are correct

### Emails Not Sending
1. Check `email_system.log` for errors
2. Verify pending emails exist: `SELECT COUNT(*) FROM emails WHERE status='pending';`
3. Test with `--once` flag to debug immediately

### Database Errors
Ensure the database user has privileges:

```sql
GRANT ALL PRIVILEGES ON email_system.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

## Performance Notes

- Default: 100 emails/batch, 60 sec delay = ~5,000 emails in 50 minutes
- Adjust `BATCH_SIZE` and `BATCH_DELAY` for your needs
- Monitor error rates in `email_system.log`
- Use daily_statistics table to track performance

## License

Internal Use Only

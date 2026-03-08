# Email Scheduler Service

## Overview

The email scheduler service automatically executes scheduled email campaigns at their designated times. It runs continuously in the background, checking every 60 seconds for schedules that need to be executed.

## Quick Start

### Start the Scheduler
```bash
./start_scheduler.sh
```

### Stop the Scheduler
```bash
./stop_scheduler.sh
```

### Monitor Scheduler Logs
```bash
tail -f scheduler.log
```

## How It Works

1. The scheduler checks the database every 60 seconds for active schedules
2. Schedules are selected based on:
   - `is_active = TRUE`
   - `status IN ('draft', 'scheduled')`
   - Current date is within `start_date` and `end_date`
   - Schedule time matches current time
3. When a schedule is due, it:
   - Updates status to 'running'
   - Sends emails to all recipients in the recipient_list
   - Logs each email send attempt to schedule_logs table
   - Updates sent_count and failed_count
   - For 'once' schedules: marks as 'completed' and deactivates
   - For recurring schedules: calculates next_run time

## Creating Schedules

### Via Dashboard UI

1. Go to **Scheduler** tab
2. Click **Create New Schedule**
3. Fill in:
   - **Name**: Schedule name
   - **Template**: Select email template
   - **Recipients**: Enter email addresses (one per line or comma-separated)
   - **Schedule Type**: 
     - `once`: Run one time only
     - `daily`: Run every day at specified time
     - `weekly`: Run every week
     - `monthly`: Run every month
   - **Schedule Time**: Time to run (HH:MM format)
   - **Start Date**: When to start
   - **End Date**: When to stop
4. Click **Save**
5. **Activate** the schedule (click the play button)

### Via API

```bash
curl -X POST http://localhost:5001/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Weekly Newsletter",
    "template_id": 1,
    "recipient_list": ["user1@example.com", "user2@example.com"],
    "schedule_type": "daily",
    "schedule_time": "09:00:00",
    "start_date": "2026-03-08",
    "end_date": "2026-12-31",
    "created_by": "admin",
    "notes": "Weekly newsletter campaign"
  }'
```

### Activate Schedule

```bash
curl -X POST http://localhost:5001/api/schedules/1/activate
```

## Schedule Types

- **once**: Runs one time at specified time, then marks as completed
- **daily**: Runs every day at specified time
- **recurring**: Runs based on schedule_type configuration
- **weekly**: Runs once per week
- **monthly**: Runs once per month

## Checking Schedule Status

### View All Schedules
```bash
curl http://localhost:5001/api/schedules
```

### View Specific Schedule
```bash
curl http://localhost:5001/api/schedules/1
```

### Check Execution Logs
Schedule execution details are logged in the `schedule_logs` table:

```sql
SELECT * FROM email_system.schedule_logs 
WHERE schedule_id = 1 
ORDER BY executed_at DESC;
```

## Troubleshooting

### Scheduler Not Running
```bash
# Check if scheduler is running
ps aux | grep schedule_runner.py

# If not running, start it
./start_scheduler.sh
```

### Schedule Not Executing

1. **Check schedule is activated**:
   - Status should be 'scheduled' (not 'draft')
   - is_active should be TRUE

2. **Check dates**:
   - Current date should be >= start_date
   - Current date should be <= end_date

3. **Check time**:
   - schedule_time should be in HH:MM:SS format
   - Time should match current time (scheduler checks every minute)

4. **Check template**:
   - Template must exist and have content
   - template_id must be valid

5. **Check recipients**:
   - recipient_list should be a valid JSON array
   - At least one recipient should be present

### View Scheduler Logs
```bash
# View recent logs
tail -50 scheduler.log

# Monitor in real-time
tail -f scheduler.log

# Search for errors
grep ERROR scheduler.log
```

### Manual Test Run
Run scheduler once without keeping it running:
```bash
source .venv/bin/activate
python schedule_runner.py --once
```

## Integration with Dashboard

The dashboard must be running for API operations:
```bash
python dashboard.py
```

Both services can run simultaneously:
- **Dashboard**: Port 5001 (web interface + API)
- **Scheduler**: Background process (reads from database)

## Production Deployment

### Using systemd (Linux)

Create `/etc/systemd/system/email-scheduler.service`:
```ini
[Unit]
Description=Email Schedule Runner
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/emailsystem
ExecStart=/path/to/emailsystem/.venv/bin/python schedule_runner.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable email-scheduler
sudo systemctl start email-scheduler
sudo systemctl status email-scheduler
```

### Using Docker

The scheduler is included in the Docker setup. Make sure to run both services:
```bash
docker-compose up -d
```

## Configuration

Edit `config.py` to change:
- Database connection settings
- SMTP settings
- Logging configuration

## Files

- `schedule_runner.py` - Main scheduler service
- `start_scheduler.sh` - Start script
- `stop_scheduler.sh` - Stop script
- `scheduler.log` - Execution logs
- `db_template_migrate.py` - Database setup (creates email_schedules table)

## Database Schema

### email_schedules table
- `id`: Schedule ID
- `name`: Schedule name
- `template_id`: Reference to email_templates
- `recipient_list`: JSON array of email addresses
- `schedule_type`: once/daily/weekly/monthly
- `schedule_time`: Time to run (TIME field)
- `schedule_day`: Day of week/month (for weekly/monthly)
- `start_date`: Start date
- `end_date`: End date
- `is_active`: Is schedule active
- `status`: draft/scheduled/running/completed/failed/paused
- `sent_count`: Number of emails sent
- `failed_count`: Number of emails failed
- `last_run`: Last execution time
- `next_run`: Next scheduled run time
- `created_by`: Creator username
- `notes`: Additional notes

### schedule_logs table
- `id`: Log ID
- `schedule_id`: Reference to email_schedules
- `recipient_email`: Recipient email
- `status`: success/failed
- `error_message`: Error message if failed
- `executed_at`: Execution timestamp

## Support

For issues or questions:
1. Check scheduler logs: `tail -f scheduler.log`
2. Check dashboard logs: `tail -f dashboard.log`
3. Verify database tables exist
4. Ensure SMTP settings are correct in `.env`

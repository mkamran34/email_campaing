# Web Dashboard Guide

## Starting the Dashboard

Run the dashboard with:

```bash
python dashboard.py
```

Or use the helper script:

```bash
bash run_dashboard.sh
```

The dashboard will be available at: **http://localhost:5000**

## Dashboard Features

### 📊 Statistics Panel

The top of the dashboard shows real-time metrics:

- **Total Emails**: Total number of emails in the system
- **Pending**: Emails waiting to be sent
- **Sent Today**: Emails successfully sent today
- **Failed**: Emails that failed to send
- **Bounced**: Emails that were rejected by recipient server

Stats auto-refresh every 5 seconds.

### 📋 Email Browser

Browse all emails with advanced filtering:

**Tabs:**
- **All Emails**: View all emails regardless of status
- **Pending**: View only emails waiting to be sent
- **Sent**: View successfully sent emails
- **Failed**: View emails that failed
- **Bounced**: View rejected emails

**Search & Filter:**
- Type in the search box to filter by recipient or subject
- Click "Refresh" to reload the current view

**Columns:**
- ID: Email unique identifier
- Recipient: Email address
- Subject: Email subject
- Status: Current delivery status
- Sent: When the email was sent (if applicable)
- Created: When the email was added to the system
- Action: View or manage the email

### 🔍 Email Details

Click the "View" button on any email to see full details:

- Complete email information
- Full email body
- Error message (if any)
- Quick actions to update status

**Actions available:**
- Mark as Sent
- Mark as Failed
- Close modal

### ✏️ Email Management

**Individual Email Management:**
1. Click "View" on any email
2. Click "Mark as Sent" or "Mark as Failed"
3. The email status updates immediately

**Bulk Operations:**
1. Check the boxes next to emails you want to manage
2. Check "Select All" to select all visible emails
3. Click "Mark Selected as Sent" or "Delete Selected"
4. Confirm the action

**Note:** Bulk actions work on the currently visible emails in the active tab.

### 📱 Responsive Design

The dashboard works on all devices:
- Desktop: Full feature set
- Tablet: Optimized layout
- Mobile: Simplified view with essential features

## Dashboard API

The web dashboard uses REST APIs that you can also call directly:

### Get Statistics
```bash
curl http://localhost:5000/api/stats
```

Response:
```json
{
  "success": true,
  "overall": {
    "total": 200,
    "pending": 50,
    "sent": 140,
    "failed": 8,
    "bounced": 2
  },
  "today": {
    "date": "2026-02-27",
    "total": 100,
    "sent": 95,
    "failed": 3,
    "bounced": 2,
    "pending": 0
  }
}
```

### Get Emails List
```bash
curl http://localhost:5000/api/emails?page=1&limit=50&status=pending
```

### Get Email Details
```bash
curl http://localhost:5000/api/email/1
```

### Update Email Status
```bash
curl -X PUT http://localhost:5000/api/email/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "sent"}'
```

### Bulk Update Emails
```bash
curl -X POST http://localhost:5000/api/emails/bulk-update \
  -H "Content-Type: application/json" \
  -d '{"email_ids": [1, 2, 3], "status": "sent"}'
```

### Delete Email
```bash
curl -X DELETE http://localhost:5000/api/email/1
```

### Health Check
```bash
curl http://localhost:5000/api/health
```

## Troubleshooting

### Dashboard won't start
- Check if port 5000 is already in use
- Try: `python dashboard.py` and look for error messages
- Check dashboard.log for detailed logs

### Can't connect to database
- Verify MySQL is running
- Check .env file for correct database credentials
- Run `python db_setup.py` to ensure tables exist

### Stats not updating
- Refresh the page
- Check if database connection is working (green dot in top right)
- Check dashboard.log for errors

### Emails not showing up
- Insert test emails: `python insert_samples.py 50`
- Verify emails table has records: `SELECT COUNT(*) FROM emails;`
- Check database connection status

## Performance Tips

- For large number of emails (>10,000), use pagination to browse
- Use status filters to narrow down results
- Run dashboard on same server as MySQL for best performance
- Consider using a reverse proxy (nginx) in production

## Running Multiple Instances

You can run dashboard and email sender simultaneously:

**Terminal 1 - Email Sender:**
```bash
python email_sender.py --schedule 09:00
```

**Terminal 2 - Dashboard:**
```bash
python dashboard.py
```

The dashboard will show real-time updates as emails are sent.

## Production Deployment

For production, consider:

1. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn dashboard:app -w 4 -b 0.0.0.0:5000
   ```

2. **Add a reverse proxy (nginx):**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
       }
   }
   ```

3. **Enable HTTPS** with Let's Encrypt
4. **Add authentication** to dashboard.py
5. **Configure database backups**
6. **Use environment variables** for security

## Security Notes

- The dashboard currently has no authentication
- Deploy on a secure, private network
- Use HTTPS in production
- Restrict database user permissions
- Keep your `.env` file secure
- Consider adding API authentication tokens

For production security, add Flask authentication:
```python
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username, password):
    # Add your authentication logic
    pass

@app.route('/api/stats')
@auth.login_required
def get_stats():
    # Your code
    pass
```

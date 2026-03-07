# Email Delivery Troubleshooting Guide

## 🚨 Critical Issue: Emails Show "Sent" But Don't Arrive

When SMTP accepts emails without errors but they don't reach the recipient, it's **NOT an SMTP problem** - it's a **mail server delivery problem**.

### Root Causes (In Order of Likelihood)

1. **Sender Not Authorized** ⚠️ MOST COMMON
   - The `FROM_EMAIL` is not authorized to send from this mail server
   - Solution: FROM_EMAIL must match the domain of SMTP_USERNAME
   
2. **SPF/DKIM/DMARC Verification Failure**
   - Recipient server checks domain authentication records
   - Email gets rejected at delivery stage (not SMTP)
   - Solution: Contact mail provider or add proper DNS records

3. **Mail Server Filtering**
   - Recipient server silently filters the email
   - Email is deleted before reaching inbox
   - Solution: Check with mail provider's support

---

## 🔧 IMMEDIATE ACTION PLAN

### Step 1: Verify Sender Authorization (CRITICAL)

Your FROM_EMAIL must match the authorized domain:

```bash
# Check your current config
cat .env | grep -E "^SMTP_USERNAME|^FROM_EMAIL"
```

**Rule**: If `SMTP_USERNAME` is `marketing@perinaljournalsubmissions.com`, then:
- ✅ CORRECT: `FROM_EMAIL=marketing@perinaljournalsubmissions.com`
- ✅ CORRECT: `FROM_EMAIL=noreply@perinaljournalsubmissions.com` (same domain)
- ❌ WRONG: `FROM_EMAIL=noreply@anotherdomain.com` (different domain)

**Fix**: Update `.env`
```env
# Change this line to match SMTP domain
FROM_EMAIL=marketing@perinaljournalsubmissions.com
```

Then restart the email sender.

### Step 2: Check Mail Server Logs Directly

Contact your mail server provider (**perinaljournalsubmissions.com**) and ask them:

> "I'm sending emails through SMTP (mail.perinaljournalsubmissions.com:587) 
> from marketing@perinaljournalsubmissions.com. 
> The SMTP server accepts them but they're not reaching recipients.
> Can you check the mail server logs for delivery failures?"

Provide them:
- Time of test (e.g., Feb 27, 2026 3:00 PM UTC)
- Recipient email address used for test
- Sender email (FROM_EMAIL)
- SMTP username

### Step 3: Check SPF/DKIM/DMARC Records

Ask your mail provider if these DNS records are configured:

```bash
# Check SPF record (should list your mail server)
dig perinaljournalsubmissions.com TXT | grep v=spf1

# Check DKIM (usually mail._domainkey.perinaljournalsubmissions.com)
dig TXT mail._domainkey.perinaljournalsubmissions.com

# Check DMARC
dig _dmarc.perinaljournalsubmissions.com TXT
```

If these are missing, ask your provider to set them up.

### Step 4: Test with Different Recipients

Test sending to different domains to identify pattern:

```bash
# Send one email to different domains
/Users/muhammadkamran/email-system/.venv/bin/python email_sender.py --once
```

Does it work for:
- Gmail accounts? (Gmail is strict with SPF/DKIM)
- Outlook accounts? (Outlook is strict with SPF/DKIM)
- Your domain? (Might accept without verification)
- Different recipients at same domain?

---

## 📋 Detailed Diagnostic Steps

### 1. Test SMTP Connection First
Use the dashboard **Settings** tab → **Test SMTP Connection**:
- Leave "Test Email Address" empty to test connection only
- Contact your mail server provider if connection fails

### 2. Send a Test Email to Yourself
1. Go to dashboard **Settings** tab
2. Enter your email in "Test Email Address"
3. Click "Test SMTP Connection"
4. Check:
   - Inbox (not just spam folder)
   - Spam/Junk folder
   - Blocked messages

If you don't receive it:
- It's a mail server delivery issue, NOT SMTP
- Contact your mail provider with time/details

### 3. Check Email Logs

Look for diagnostic messages in `email_system.log`:

```bash
tail -f email_system.log | grep -E "Attempting to send|Email accepted|rejected"
```

You'll see messages like:
- **"Email accepted by SMTP server for recipient@example.com (Note: does not guarantee delivery to inbox)"**
  - This means SMTP accepted it, but recipient server may reject it
- **"Sender refused" or "Recipient refused"**
  - Delivery was rejected during SMTP transaction
- **"SMTP authentication failed"**
  - Credentials are wrong

### 4. Verify SMTP Configuration

Check your `.env` file:

```bash
cat .env
```

Verify:
| Setting | Example | Notes |
|---------|---------|-------|
| **SMTP_HOST** | mail.perinaljournalsubmissions.com | Should be your mail server |
| **SMTP_PORT** | 587 | 587=TLS, 465=SSL |
| **SMTP_USERNAME** | marketing@perinaljournalsubmissions.com | Your email account |
| **SMTP_PASSWORD** | (hidden) | Should be correct |
| **FROM_EMAIL** | marketing@perinaljournalsubmissions.com | **MUST match SMTP_USERNAME domain** ⚠️ |
| **SMTP_USE_TLS** | True | Should be True for port 587 |

### 5. Common Issues & Solutions

| Issue | Root Cause | Solution |
|-------|-----------|----------|
| Emails "sent" but not delivered | Sender not authorized | Ensure FROM_EMAIL domain matches SMTP username domain |
| Emails "sent" but not delivered | SPF/DKIM failure | Contact mail provider to add/verify DNS records |
| "Sender refused" error | FROM_EMAIL not on mail server | Change FROM_EMAIL to authorized address |
| "Authentication failed" | Wrong credentials | Verify SMTP_USERNAME and SMTP_PASSWORD |
| "Connection refused" | Wrong host/port | Check SMTP_HOST and SMTP_PORT are correct |
| Emails going to spam | Domain not verified | Ask mail provider about SPF/DKIM setup |

### 6. Check Database for Details

```bash
mysql -u root -p12345678 email_system -e "
SELECT id, recipient, status, error_message, sent_at 
FROM emails 
ORDER BY id DESC 
LIMIT 10;
"
```

Look for patterns in recipient domains or error messages.

### 7. Manual SMTP Test

Test directly with Python:

```python
python3 << 'EOF'
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

HOST = 'mail.perinaljournalsubmissions.com'
PORT = 587
USERNAME = 'marketing@perinaljournalsubmissions.com'
PASSWORD = 'your-password-here'
FROM_EMAIL = 'marketing@perinaljournalsubmissions.com'
TO_EMAIL = 'test@example.com'

print(f"[*] Connecting to {HOST}:{PORT}")
smtp = smtplib.SMTP(HOST, PORT)
smtp.starttls()

print(f"[*] Logging in as {USERNAME}")
smtp.login(USERNAME, PASSWORD)

msg = MIMEMultipart('alternative')
msg['From'] = FROM_EMAIL
msg['To'] = TO_EMAIL
msg['Subject'] = 'Test Email'
msg['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')

body = "This is a test email to diagnose delivery issues."
msg.attach(MIMEText(body, 'plain', 'utf-8'))

print(f"[*] Sending email from {FROM_EMAIL} to {TO_EMAIL}")
result = smtp.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())

if result:
    print(f"[ERROR] Delivery rejected: {result}")
else:
    print(f"[SUCCESS] SMTP accepted email (check recipient mailbox)")

smtp.quit()
EOF
```

### 8. Contact Mail Server Provider

Prepare this information:
- **Sender email**: marketing@perinaljournalsubmissions.com
- **SMTP host**: mail.perinaljournalsubmissions.com
- **SMTP port**: 587
- **Issue**: Emails accepted by SMTP but not delivered
- **Test time**: (your local time)
- **Test recipient**: (email you tested)

Ask them to:
1. Check mail server logs for delivery attempts
2. Check if SPF/DKIM/DMARC records are configured
3. Verify sender authorization for FROM_EMAIL

---

## 📞 Next Steps

1. **Verify sender authorization first** (most common issue)
2. **Contact your mail provider** with diagnostic info
3. **Check SPF/DKIM/DMARC** records exist
4. **Test with multiple recipients** to identify pattern

## ✅ What We've Improved

The system now:
- ✅ Adds proper email headers (Message-ID, Date, etc.)
- ✅ Logs detailed SMTP transaction info
- ✅ Checks SMTP rejection at send time
- ✅ Clarifies that SMTP acceptance ≠ delivery guarantee
- ✅ Provides diagnostic logging for debugging

### 1. Test SMTP Connection First
Use the dashboard **Settings** tab → **Test SMTP Connection**:
- Leave "Test Email Address" empty to test connection only
- Contact your mail server provider if connection fails

### 2. Send a Test Email to Yourself
1. Go to dashboard **Settings** tab
2. Enter your email in "Test Email Address"
3. Click "Test SMTP Connection"
4. Check:
   - Inbox (not just spam folder)
   - Spam/Junk folder
   - Blocked messages

If you don't receive it:
- Check mail server logs (requires server access)
- Verify "From Email" is authorized to send from the mail server
- Check for SPF/DKIM/DMARC issues

### 3. Check Email Logs

Look for the actual error messages in `email_system.log`:

```bash
tail -f email_system.log | grep -E "Error|failed|refused|rejected"
```

Common messages:
- **"Sender refused"** - The from_email is not authorized to send
- **"Recipient refused"** - The recipient address is blocked/invalid
- **"Authentication failed"** - SMTP credentials are wrong
- **"Connection refused"** - Mail server is down or wrong host/port

### 4. Verify SMTP Configuration

Check your `.env` file:

```bash
cat .env
```

Verify:
- **SMTP_HOST**: Correct mail server address (no typos)
- **SMTP_PORT**: Usually 587 (TLS) or 465 (SSL)
- **SMTP_USERNAME**: Correct username
- **SMTP_PASSWORD**: Correct password/app password
- **FROM_EMAIL**: Must be authorized on the mail server (usually matches SMTP_USERNAME domain)
- **SMTP_USE_TLS**: Should be True for port 587

### 5. Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Emails marked sent but not delivered | Check mail server logs; verify sender authorization |
| "Sender refused" error | Make sure FROM_EMAIL matches domain authorized for SMTP account |
| "Authentication failed" | Verify SMTP_USERNAME and SMTP_PASSWORD in .env |
| "Connection refused" | Check SMTP_HOST and SMTP_PORT are correct |
| Emails going to spam | Check SPF/DKIM/DMARC records; add verification headers |
| Bounced emails in dashboard | Check error_message column in emails table |

### 6. Check Database for Errors

```bash
mysql -u root -p email_system -e "SELECT id, recipient, status, error_message FROM emails WHERE status='bounced' OR status='failed' LIMIT 10;"
```

### 7. Manual Test from Command Line

```bash
# Connect to mail server directly
telnet mail.perinaljournalsubmissions.com 587

# Or use Python:
python3 -c "
import smtplib
from email.mime.text import MIMEText

smtp = smtplib.SMTP('mail.perinaljournalsubmissions.com', 587)
smtp.starttls()
smtp.login('your-username', 'your-password')

msg = MIMEText('Test message')
msg['From'] = 'marketing@perinaljournalsubmissions.com'
msg['To'] = 'test@example.com'
msg['Subject'] = 'Test'

try:
    result = smtp.sendmail('marketing@perinaljournalsubmissions.com', 'test@example.com', msg.as_string())
    print('Delivery status:', result)
except Exception as e:
    print('Error:', e)

smtp.quit()
"
```

### 8. Check Mail Server Logs (If You Have Access)

Contact your mail server provider to check:
- SMTP server logs for your account
- Mail delivery logs for the recipient
- Any blocks/filters on outgoing mail

### 9. Verify SPF/DKIM/DMARC Records

If using a custom domain, ensure your DNS records are set up:
- **SPF Record**: Authorizes your mail server
- **DKIM Record**: Signs emails with your domain
- **DMARC Record**: Instructs recipient servers how to handle emails

Ask your mail provider about these.

## When to Contact Your Mail Server Provider

Provide them with:
1. SMTP host, port, and credentials
2. The "From Email" address
3. The recipient email that's not receiving
4. Date/time of the test
5. Log messages showing any errors

## Improved Error Detection

The updated `smtp_helper.py` now:
- Uses `sendmail()` for better error detection
- Catches and logs specific SMTP errors
- Reports delivery failures immediately
- Updates database with error details

Check `email_system.log` for detailed error messages after running emails again.

## Quick Test Command

```bash
# Test 5 emails to see if there are delivery errors
cd /Users/muhammadkamran/email-system
.venv/bin/python -c "
from smtp_helper import SMTPConnection

smtp = SMTPConnection()
smtp.connect()
success, error = smtp.send_email('your-test@example.com', 'Test Subject', 'Test Body')
print(f'Send result - Success: {success}, Error: {error}')
smtp.disconnect()
"
```

## Next Steps

1. Run the SMTP test in dashboard with your email
2. Check the test result and mail folder
3. Look at `email_system.log` for any error messages
4. If still failing, contact your mail server provider with the error details

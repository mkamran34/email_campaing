# Email Template Designer & Scheduler Guide

## Overview

The Email Template Designer and Scheduler module allows you to:
- **Design and manage reusable email templates** with support for HTML and plain text
- **Create automated email schedules** for batch sending or manual triggers
- **Organize templates with tags** for easy classification
- **Schedule emails with flexible timing** (once, daily, weekly, monthly)
- **Track schedule execution** with sent/failed counts and status monitoring

---

## Template Designer

### Creating a Template

1. **Navigate to Templates Tab**
   - Click the "Templates" button in the dashboard navigation
   - Click "Create Template" button

2. **Fill Template Details**
   - **Template Name** (Required): Unique identifier for this template
     - Example: "Welcome Email", "Newsletter", "Password Reset"
   - **Email Subject** (Required): Subject line for emails using this template
     - Example: "Welcome to {{company_name}}!"
   - **Email Body - Plain Text** (Required): Plain text version of email
     - Supports variables like {{name}}, {{email}}, {{company_name}}
   - **Email Body - HTML** (Optional): HTML formatted version
     - Will be used if recipient supports HTML emails
   - **Tags** (Optional): Comma-separated keywords for organization
     - Example: "welcome, promotional, transactional"

3. **Save Template**
   - Click "Save Template" button
   - Template is now available for use in schedules

### Template Variables

Use template variables in subject and body to personalize emails:
- `{{name}}` - Recipient's name
- `{{email}}` - Recipient's email address
- `{{company_name}}` - Your company name
- `{{date}}` - Current date
- `{{time}}` - Current time

Variables are replaced when emails are sent.

### Managing Templates

**View Templates**
- All templates appear as cards in the Templates tab
- Each card shows:
  - Template name
  - Subject line preview
  - Created and updated timestamps
  - Action buttons

**Edit Template**
- Click the pencil icon on any template card
- Make changes in the form
- Click "Save Template" to update

**Delete Template**
- Click the trash icon on template card
- Confirm deletion
- Template is permanently removed (but existing schedules using it are unaffected)

### Template Best Practices

1. **Keep it concise**: Limit to 2000 characters for better deliverability
2. **Use variables**: Make templates dynamic with {{variable}} placeholders
3. **Test before use**: Preview templates before adding to schedules
4. **Organize with tags**: Use consistent tag naming for easy filtering
5. **Include unsubscribe**: Add unsubscribe link in footer for compliance
6. **Mobile-friendly**: If using HTML, ensure responsive design

---

## Email Scheduler

### Creating a Schedule

1. **Navigate to Scheduler Tab**
   - Click the "Scheduler" button in dashboard navigation
   - Click "Create Schedule" button

2. **Configure Schedule Settings**

   **Basic Information**
   - **Schedule Name**: Unique name for this schedule
     - Example: "Daily Newsletter", "Welcome Series - Day 1"
   - **Email Template**: Select template to use for emails
     - Must select a template from dropdown

   **Schedule Type**
   - **Once**: Send immediately or at specific date/time
   - **Daily**: Send every day at specified time
   - **Weekly**: Send every week on specified day
   - **Monthly**: Send monthly on specified date

   **Timing**
   - **Time**: Hour and minute to send (HH:MM format)
   - **Start Date**: When schedule should begin
   - **End Date**: (Optional) When schedule should stop

3. **Add Recipients**
   - **Recipients field**: Enter email addresses, one per line
   - System validates format before sending
   - Example:
     ```
     john@example.com
     jane@example.com
     bob@example.com
     ```

4. **Optional Details**
   - **Notes**: Add context or instructions about this schedule
   - Gets recorded for future reference

5. **Save and Activate**
   - Click "Save Schedule" button
   - Schedule is created in DRAFT status
   - Click the play icon to ACTIVATE schedule

### Schedule Status Information

**Status Codes**
- **Draft**: Schedule created but not activated
- **Scheduled**: Active and waiting for next send time
- **Running**: Currently sending emails
- **Completed**: All emails sent (limited schedules only)
- **Failed**: Error during sending
- **Paused**: Manually paused

**Status Indicators**
- Each schedule card shows:
  - Current status badge (color-coded)
  - Schedule type (once, daily, weekly, monthly)
  - Total recipients count
  - Sent/failed email counts
  - Next scheduled run time

### Managing Schedules

**View Schedules**
- All schedules appear in Scheduler tab
- Each card shows full schedule information
- Color-coded status badges

**Edit Schedule**
- Click pencil icon on schedule card
- Modify any setting
- Click "Save Schedule" to apply changes

**Activate/Pause Schedule**
- Click play icon (green) to ACTIVATE paused schedule
- Click pause icon (yellow) to PAUSE active schedule
- Schedule won't send while paused

**Delete Schedule**
- Click trash icon
- Confirm deletion
- Schedule is permanently removed (already sent emails are not affected)

### Schedule Examples

**Example 1: Daily Newsletter**
```
Name: Daily Newsletter
Template: Newsletter Template
Type: Daily
Time: 09:00 AM
Start Date: 2026-03-01
End Date: (ongoing)
Recipients: 100+ email addresses
```

**Example 2: One-Time Announcement**
```
Name: Product Launch Announcement
Template: Announcement
Type: Once
Start Date: 2026-03-15
Recipient: Limited to specific group
```

**Example 3: Weekly Campaign**
```
Name: Weekly Promotions
Template: Weekly Promo
Type: Weekly
Time: 10:00 AM
Start Date: 2026-03-01
Recipients: Active customers
```

### Scheduler Features

**Recipient Management**
- Enter one email per line
- System validates all emails before sending
- Duplicate emails are automatically removed
- Failed recipients are logged with error details

**Execution Tracking**
- **Sent Count**: Number of emails successfully sent
- **Failed Count**: Number of emails that failed
- **Last Run**: Timestamp of most recent send
- **Next Run**: Scheduled time for next send

**Error Handling**
- Failed emails are marked with error message
- Schedule can retry or skip failed addresses
- Error logs help troubleshoot delivery issues

---

## Template + Scheduler Integration

### Using Templates in Schedules

1. **Best Practice Workflow**
   - Create and test template first
   - Create schedule using template
   - Schedule handles sending via template

2. **Template Updates**
   - Editing template affects ALL future sends
   - Already-sent emails keep original template content
   - Schedule continues using updated template

3. **Variable Substitution**
   - Recipient data replaces template variables
   - Each email personalized before sending
   - Falls back to placeholder if data missing

---

## API Reference

### Template Endpoints

**Create Template**
```
POST /api/templates
Content-Type: application/json

{
  "name": "Welcome Email",
  "subject": "Welcome {{name}}!",
  "body": "Hello {{name}}...",
  "html_body": "<h1>Welcome</h1>...",
  "tags": ["welcome", "transactional"]
}
```

**Get All Templates**
```
GET /api/templates
```

**Get Specific Template**
```
GET /api/templates/{template_id}
```

**Update Template**
```
PUT /api/templates/{template_id}
Content-Type: application/json

{
  "subject": "Updated Subject",
  "body": "Updated body content..."
}
```

**Delete Template**
```
DELETE /api/templates/{template_id}
```

### Schedule Endpoints

**Create Schedule**
```
POST /api/schedules
Content-Type: application/json

{
  "name": "Daily Newsletter",
  "template_id": 1,
  "schedule_type": "daily",
  "schedule_time": "09:00",
  "start_date": "2026-03-01",
  "recipient_list": ["email1@example.com", "email2@example.com"]
}
```

**Get All Schedules**
```
GET /api/schedules
```

**Get Specific Schedule**
```
GET /api/schedules/{schedule_id}
```

**Update Schedule**
```
PUT /api/schedules/{schedule_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "is_active": false
}
```

**Activate Schedule**
```
POST /api/schedules/{schedule_id}/activate
```

**Pause Schedule**
```
POST /api/schedules/{schedule_id}/deactivate
```

**Delete Schedule**
```
DELETE /api/schedules/{schedule_id}
```

---

## Database Schema

### email_templates Table
```sql
- id: Primary key
- name: Unique template name
- subject: Email subject line
- body: Plain text body
- html_body: HTML body (optional)
- plain_text: Alternative plain text
- tags: JSON array of tags
- variables: JSON array of template variables
- created_at: Creation timestamp
- updated_at: Last update timestamp
- is_default: Boolean flag
```

### email_schedules Table
```sql
- id: Primary key
- name: Schedule name
- template_id: Foreign key to templates
- recipient_list: JSON array of emails
- schedule_type: once, recurring, daily, weekly, monthly
- schedule_time: Time (HH:MM)
- schedule_day: Day (0-6 for week, 1-31 for month)
- start_date: Schedule start date
- end_date: Schedule end date
- is_active: Active/inactive flag
- status: draft, scheduled, running, completed, failed, paused
- sent_count: Number of emails sent
- failed_count: Number of failed emails
- created_at: Creation timestamp
- last_run: Last run timestamp
- next_run: Next scheduled run
```

### schedule_logs Table
```sql
- id: Primary key
- schedule_id: Foreign key to schedules
- run_id: Unique run identifier
- started_at: Execution start time
- completed_at: Execution end time
- total_sent: Emails sent in this run
- total_failed: Emails failed in this run
- status: running, completed, failed
- error_message: Error details if failed
```

---

## Troubleshooting

### Template Issues

**Problem: Template won't save**
- Check that name is unique
- Ensure subject and body are not empty
- Verify JSON format if using tags

**Problem: Variables not replacing**
- Verify variable syntax: {{variable_name}}
- Check spelling of variable names
- Ensure recipient data includes required fields

### Scheduler Issues

**Problem: Schedule not sending**
- Check if schedule is activated (not just created)
- Verify start date is not in future
- Confirm template is selected
- Check system time matches schedule time

**Problem: Emails going to spam**
- Review template content (avoid spam keywords)
- Check sender reputation
- Verify SMTP configuration in Settings
- Add unsubscribe link to template

**Problem: Recipients not receiving**
- Verify email list format (one per line)
- Check email validation settings
- Confirm SMTP server is working
- Review dashboard logs for error messages

---

## Performance Tips

1. **Batch Sending**: Use moderate recipient counts (100-1000) per schedule
2. **Timing**: Stagger multiple schedules to avoid server overload
3. **Template Size**: Keep HTML templates under 100KB
4. **Variables**: Minimize number of variables for faster processing
5. **Testing**: Always test schedule with small recipient list first

---

## Security Considerations

1. **Recipient Privacy**: Never share recipient lists between different schedules
2. **Template Content**: Don't include sensitive data in templates (passwords, tokens)
3. **SMTP Credentials**: Keep SMTP login secure in Settings tab
4. **Access Control**: Limit dashboard access to authorized users only
5. **Data Retention**: Regularly archive old schedules and logs

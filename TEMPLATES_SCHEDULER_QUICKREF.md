# Quick Reference: Templates & Scheduler

## Dashboard Navigation

```
Email System Dashboard
│
├── All Emails
├── Pending
├── Sent
├── Failed
├── Bounced
├── Send Now
├── Settings
├── Validation
├── ⭐ Templates (NEW)
└── ⭐ Scheduler (NEW)
```

---

## Templates Tab

### What You Can Do
- Create new email templates
- Edit existing templates  
- Delete templates
- Organize with tags
- Support HTML and plain text

### Button Functions
| Button | Action |
|--------|--------|
| **Create Template** | Open form to create new template |
| **Save** | Save or update template |
| **Cancel** | Close form without saving |
| **✏️ (Edit icon)** | Load template for editing |
| **🗑️ (Delete icon)** | Remove template (with confirmation) |

### Form Fields

| Field | Required | Example |
|-------|----------|---------|
| Template Name | Yes | "Welcome Email" |
| Email Subject | Yes | "Welcome {{name}}!" |
| Email Body (Text) | Yes | "Hello {{name}}, welcome..." |
| Email Body (HTML) | No | "<h1>Welcome</h1>..." |
| Tags | No | "welcome, welcome-series" |

### Template Card Info
```
[Template Name]
✏️ 🗑️

Subject: Your email subject line here
Created: Feb 27, 2026 10:30 AM
Updated: Feb 27, 2026 10:30 AM
```

---

## Scheduler Tab

### What You Can Do
- Create email sending schedules
- Define schedule frequency (once, daily, weekly, monthly)
- Add recipient lists
- Activate/pause schedules
- Monitor sending progress
- Delete schedules

### Button Functions
| Button | Action |
|--------|--------|
| **Create Schedule** | Open form to create new schedule |
| **Save** | Save or update schedule |
| **Cancel** | Close form without saving |
| **✏️ (Edit icon)** | Load schedule for editing |
| **▶️ (Play icon)** | Activate/resume paused schedule |
| **⏸️ (Pause icon)** | Pause active schedule |
| **🗑️ (Delete icon)** | Remove schedule (with confirmation) |

### Form Fields

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| Schedule Name | Text | "Daily Newsletter" | Must be unique |
| Email Template | Dropdown | Newsletter | Select from created templates |
| Schedule Type | Dropdown | Daily | Once, Daily, Weekly, Monthly |
| Time | Time | 09:00 | HH:MM format |
| Start Date | Date | 2026-03-01 | When schedule begins |
| End Date | Date | 2026-12-31 | Optional, when schedule ends |
| Recipients | Textarea | email@ex.com (one per line) | Validates before sending |
| Notes | Textarea | Any notes | For your reference |

### Schedule Card Info
```
[Schedule Name]                [Status Badge]
│
├─ Type: Daily
├─ Recipients: 150
├─ Sent: 450 / Failed: 2
├─ Next Run: 2026-03-01 09:00
│
└─ [✏️] [▶️] [🗑️]
```

### Status Badges

| Status | Color | Meaning |
|--------|-------|---------|
| draft | Grey | Not yet activated |
| scheduled | Blue | Active & waiting to send |
| running | Yellow | Currently sending emails |
| completed | Green | All emails sent |
| failed | Red | Error during sending |
| paused | Grey | Temporarily stopped |

---

## Common Workflows

### Workflow 1: One-Time Announcement
```
1. Templates Tab
   ├─ Create "Announcement" template
   └─ Set subject and body
   
2. Scheduler Tab
   ├─ Create "New Feature Announcement"
   ├─ Select "Announcement" template
   ├─ Type: Once
   ├─ Start Date: Today
   ├─ Add all recipients
   └─ Click Activate (▶️)
```

### Workflow 2: Daily Newsletter
```
1. Templates Tab
   ├─ Create "Daily Newsletter" template
   ├─ Use {{date}} variable
   └─ Make HTML-friendly
   
2. Scheduler Tab
   ├─ Create "Daily Newsletter Send"
   ├─ Select "Daily Newsletter"
   ├─ Type: Daily
   ├─ Time: 09:00 AM
   ├─ Start Date: Tomorrow
   ├─ Add newsletter subscribers
   └─ Activate
   
3. Management
   ├─ Monitor daily from dashboard
   ├─ Check sent/failed counts
   └─ Pause if needed (⏸️)
```

### Workflow 3: Welcome Series
```
1. Templates Tab
   ├─ Create "Welcome - Day 1"
   ├─ Create "Welcome - Day 7"
   └─ Create "Welcome - Day 30"
   
2. Scheduler Tab
   ├─ Schedule 1: "Welcome Day 1"
   │  ├─ Run: Once
   │  └─ Recipients: New signups
   │
   ├─ Schedule 2: "Welcome Day 7"
   │  └─ Run: Weekly
   │
   └─ Schedule 3: "Welcome Day 30"
      └─ Run: Monthly
```

---

## Tips & Tricks

### Template Tips
- Use `{{name}}` to personalize
- Provide both HTML and plain text
- Test with small recipient list first
- Use meaningful template names
- Organize with tags: `promotional, transactional, welcome`

### Scheduler Tips
- Start small: test with 10 recipients
- Schedule during low-traffic hours
- Always select a template
- Enter recipients one per line
- Monitor first run to verify delivery
- Use "Pause" before editing to avoid conflicts
- Delete old completed schedules to keep list manageable

### Optimization Tips
- Reuse templates across schedules
- Set end dates for time-limited campaigns
- Batch recipients by segment or preference
- Review failed email logs regularly
- Archive old schedules after completion

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Create Template | Tab1 → Create → Enter name |
| Create Schedule | Tab2 → Create → Enter details |
| Save | Click Save or Ctrl+S (if form focused) |
| Cancel | ESC or Click Cancel |

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Template Name Already Exists" | Use unique name, add suffix like `_v2` |
| Schedule won't send | Check: activated? template selected? time set? |
| Emails not received | SMTP test, check recipient emails, review logs |
| Form won't save | Verify all required fields filled, check browser console |
| Templates dropdown empty | Create a template first in Templates tab |
| Can't pause schedule | Only active schedules can be paused |

---

## Status Transitions

```
Draft (Created)
    ↓
↓─→ Scheduled (Activated with future start date)
│   ↓
│   ↓─→ Running (Currently sending)
│   │   ↓
│   │   ↓─→ Completed (All emails sent)
│   │   ↓
│   │   └─→ Failed (Error occurred)
│
└─→ Paused (Manually paused)
    ↓
    └─→ Scheduled (Resumed from pause)
```

---

## Data Flow

```
Template Creation
       ↓
    Template
    (Stored in DB)
       ↓
Schedule References Template
       ↓
Recipients + Template → Email Task
       ↓
Email Execution
       ↓
[Success] → Mark as Sent
[Failure] → Log Error
```

---

## API Quick Reference

### Get All Templates
```
curl http://localhost:5001/api/templates
```

### Create Schedule
```
curl -X POST http://localhost:5001/api/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Newsletter",
    "template_id": 1,
    "schedule_type": "daily",
    "schedule_time": "09:00",
    "start_date": "2026-03-01",
    "recipient_list": ["user@example.com"]
  }'
```

### Activate Schedule
```
curl -X POST http://localhost:5001/api/schedules/1/activate
```

### Get Schedule Info
```
curl http://localhost:5001/api/schedules/1
```

---

## File Locations

| File | Purpose |
|------|---------|
| `TEMPLATES_SCHEDULER_GUIDE.md` | Full user documentation |
| `TEMPLATES_SCHEDULER_SUMMARY.md` | Feature overview |
| `templates/index.html` | Frontend UI |
| `static/js/dashboard.js` | JavaScript functions |
| `static/css/style.css` | Styling |
| `dashboard.py` | API endpoints |
| `db_helper.py` | Database methods |
| `db_template_migrate.py` | Migration script |

---

## Support Resources

- 📖 **Guide**: TEMPLATES_SCHEDULER_GUIDE.md
- 🔍 **Summary**: TEMPLATES_SCHEDULER_SUMMARY.md  
- 💾 **Logs**: dashboard.log
- 🗄️ **Database**: Check email_templates and email_schedules tables

---

**Last Updated**: February 27, 2026
**Status**: ✅ Production Ready

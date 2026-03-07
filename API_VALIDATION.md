# Email Validation API Documentation

## Overview

The email system now includes comprehensive email validation integrated into the dashboard API. Validation is performed at multiple levels:

- **Syntax validation** - RFC 5322 compliant email format checking
- **Domain validation** - DNS MX record verification (optional)
- **Typo detection** - Common domain spelling mistakes
- **Disposable email detection** - Identifies temporary/throwaway email providers

## Validation Endpoints

### 1. Validate Email(s) Endpoint

**Endpoint:** `POST /api/validate-email`

**Purpose:** Validate one or more email addresses

#### Request JSON (Single Email)
```json
{
  "email": "user@example.com",
  "level": "syntax"
}
```

#### Request JSON (Batch Emails)
```json
{
  "emails": [
    "user@example.com",
    "test@example.com",
    "user@gmial.com"
  ],
  "level": "syntax"
}
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `email` | string | - | Single email to validate |
| `emails` | array | - | Multiple emails to validate |
| `level` | string | "syntax" | Validation level: `quick`, `syntax`, or `full` |

#### Validation Levels

- **quick**: Syntax validation only (fastest)
- **syntax**: Syntax + typo detection + disposable check (recommended)
- **full**: Syntax + MX records + typo detection + disposable check (slowest)

#### Response (Single Email)
```json
{
  "success": true,
  "all_valid": true,
  "count": 1,
  "results": {
    "email": "user@example.com",
    "valid": true,
    "syntax_valid": true,
    "syntax_message": "Valid email syntax",
    "warnings": [],
    "suggestions": [],
    "overall_message": "Email is valid and ready to use",
    "is_disposable": false,
    "mx_valid": null
  }
}
```

#### Response (Batch Emails)
```json
{
  "success": true,
  "all_valid": false,
  "count": 4,
  "results": [
    {
      "email": "user@example.com",
      "valid": true,
      "syntax_valid": true,
      "syntax_message": "Valid email syntax",
      "warnings": [],
      "suggestions": [],
      "overall_message": "Email is valid and ready to use",
      "is_disposable": false
    },
    {
      "email": "invalid.email",
      "valid": false,
      "syntax_valid": false,
      "syntax_message": "Email must contain exactly one @ symbol",
      "warnings": [],
      "suggestions": [],
      "overall_message": "Invalid email syntax: Email must contain exactly one @ symbol",
      "is_disposable": null
    },
    {
      "email": "user@gmial.com",
      "valid": true,
      "syntax_valid": true,
      "syntax_message": "Valid email syntax",
      "warnings": [
        "Possible typo detected: 'gmial.com' → 'gmail.com'. Did you mean 'user@gmail.com'?"
      ],
      "suggestions": [
        "Possible typo detected: 'gmial.com' → 'gmail.com'. Did you mean 'user@gmail.com'?"
      ],
      "overall_message": "Email syntax is valid but has issues: Possible typo detected...",
      "is_disposable": false
    }
  ]
}
```

#### Example Usage

**Single Email:**
```bash
curl -X POST http://localhost:5001/api/validate-email \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "level": "syntax"}'
```

**Batch Emails:**
```bash
curl -X POST http://localhost:5001/api/validate-email \
  -H "Content-Type: application/json" \
  -d '{
    "emails": [
      "user@example.com",
      "invalid.email",
      "test@tempmail.com"
    ],
    "level": "syntax"
  }'
```

**Full Validation with MX Check:**
```bash
curl -X POST http://localhost:5001/api/validate-email \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "level": "full"}'
```

---

### 2. Send Now Endpoint (Enhanced)

**Endpoint:** `POST /api/send-now`

**Purpose:** Manually send emails with optional validation

#### Request JSON
```json
{
  "limit": 10,
  "recipients": [
    "user@example.com",
    "test@example.com"
  ]
}
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 10 | Max emails to send in this batch |
| `recipients` | array | - | Optional: Specific recipients to validate |

#### Behavior

- If `recipients` is provided, all emails are validated before sending
- Invalid emails are rejected with detailed error messages
- Valid emails proceed to the email sender
- If any email is invalid, the entire request is rejected (400 error)

#### Response (Invalid Recipients)
```json
{
  "success": false,
  "error": "Some email addresses are invalid",
  "invalid_emails": [
    {
      "email": "invalid.email",
      "error": "Email must contain exactly one @ symbol"
    },
    {
      "email": "user@gmial.com",
      "error": "Possible typo detected: 'gmial.com' → 'gmail.com'"
    }
  ]
}
```

#### Response (Valid Recipients - Success)
```json
{
  "success": true,
  "message": "Email sending triggered for up to 10 emails",
  "output": "..."
}
```

#### Example Usage

**Send with Recipient Validation:**
```bash
curl -X POST http://localhost:5001/api/send-now \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 5,
    "recipients": [
      "user@example.com",
      "test@example.com"
    ]
  }'
```

**Send Without Validation (Use Pending Queue):**
```bash
curl -X POST http://localhost:5001/api/send-now \
  -H "Content-Type: application/json" \
  -d '{"limit": 10}'
```

---

## Response Fields

### Email Validation Result Object

| Field | Type | Description |
|-------|------|-------------|
| `email` | string | The email address being validated |
| `valid` | boolean | Overall validity (syntax + warnings check) |
| `syntax_valid` | boolean | Whether email syntax is valid per RFC 5322 |
| `syntax_message` | string | Detailed syntax validation message |
| `warnings` | array | List of warnings (typos, disposable provider, etc.) |
| `suggestions` | array | Suggested corrections (typo fixes) |
| `overall_message` | string | Human-readable validation summary |
| `is_disposable` | boolean\|null | Whether email uses a disposable provider |
| `mx_valid` | boolean\|null | Whether domain has valid MX records (only with "full" level) |

---

## Validation Rules

### Syntax Validation

- Email must contain exactly one `@` symbol
- Local part (before @) must be 1-64 characters
- Domain part (after @) must be 1-255 characters
- Local part cannot start/end with dot or have consecutive dots
- Domain must have at least one dot
- Top-level domain must be 2+ letters only

### Typo Detection

Common misspellings detected:
- `gmial.com` → `gmail.com`
- `yahooo.com` → `yahoo.com`
- `hotmial.com` → `hotmail.com`
- `outlok.com` → `outlook.com`
- And 10+ more common typos

### Disposable Email Providers

Identified providers include:
- tempmail.com, temp-mail.org, 10minutemail.com
- sharklasers.com, throwaway.email, mailinator.com
- yopmail.com and 10+ others

### MX Record Validation

- Checks DNS for Mail Exchange records
- Verifies domain has mail servers configured
- Takes longer but most reliable for domain validity

---

## Error Handling

### Common Error Responses

**Missing Required Field:**
```json
{
  "success": false,
  "error": "No email or emails field provided"
}
```

**Invalid JSON:**
```json
{
  "success": false,
  "error": "No data provided"
}
```

**Server Error:**
```json
{
  "success": false,
  "error": "Error validating email: [error message]"
}
```

---

## Integration with Dashboard

### Browser Console (DevTools)

```javascript
// Validate single email
async function validateEmail(email) {
  const response = await fetch('/api/validate-email', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, level: 'syntax' })
  });
  return await response.json();
}

// Example usage
validateEmail('user@example.com').then(result => {
  console.log(result);
});
```

### Python Client

```python
import requests

# Validate single email
response = requests.post('http://localhost:5001/api/validate-email', json={
    'email': 'user@example.com',
    'level': 'syntax'
})
print(response.json())

# Batch validation
response = requests.post('http://localhost:5001/api/validate-email', json={
    'emails': ['user@example.com', 'test@test.com'],
    'level': 'syntax'
})
print(response.json())
```

---

## Performance Notes

| Validation Level | Speed | Checks |
|------------------|-------|--------|
| quick | Fastest | Syntax only |
| syntax | Fast | Syntax + typo + disposable |
| full | Slower | Syntax + MX + typo + disposable |

**Recommendations:**
- Use `quick` for rapid MVP validation
- Use `syntax` for user input on web forms
- Use `full` for batch import validation (can run async)
- Use `syntax` on send-now endpoint for balance

---

## Logging

All validation activities are logged:

```
2026-02-27 22:44:09,707 - __main__ - INFO - Validated 1 email(s): 1/1 valid
2026-02-27 22:44:34,583 - __main__ - WARNING - Found 1 invalid email(s): [...]
```

Check `dashboard.log` for validation history.

---

## Future Enhancements

Possible additions:
- SMTP validation (verify email exists on server)
- Bounce rate checking
- Whale detection (common corporate emails)
- Custom blacklist support
- Async batch validation endpoint
- Validation rate limiting


#!/usr/bin/env python3
"""
Quick Start: Email Validation Examples
Demonstrates usage of the email_validator module
"""

from email_validator import validate_email, EmailValidator

print("=" * 80)
print("EMAIL VALIDATION - QUICK START GUIDE")
print("=" * 80)
print()

# Example 1: Quick Single Email Validation
print("1. QUICK VALIDATION (Syntax Only)")
print("-" * 80)
result = validate_email("john@example.com", level="quick")
print(f"Email: {result['email']}")
print(f"Valid: {result['valid']}")
print(f"Message: {result['overall_message']}")
print()

# Example 2: Full Syntax Validation with Typo Detection
print("2. SYNTAX VALIDATION (Typo Detection)")
print("-" * 80)
result = validate_email("user@gmial.com", level="syntax")
print(f"Email: {result['email']}")
print(f"Valid: {result['valid']}")
print(f"Warnings: {result['warnings']}")
print(f"Suggestions: {result['suggestions']}")
print()

# Example 3: Disposable Email Detection
print("3. DISPOSABLE EMAIL DETECTION")
print("-" * 80)
result = validate_email("temp@tempmail.com", level="syntax")
print(f"Email: {result['email']}")
print(f"Is Disposable: {result.get('is_disposable')}")
if result.get('is_disposable'):
    print(f"Warning: {result['warnings'][0]}")
print()

# Example 4: Invalid Email Detection
print("4. INVALID EMAIL DETECTION")
print("-" * 80)
result = validate_email("invalid@@example.com", level="quick")
print(f"Email: {result['email']}")
print(f"Valid: {result['valid']}")
print(f"Error: {result['syntax_message']}")
print()

# Example 5: Batch Validation
print("5. BATCH VALIDATION")
print("-" * 80)
emails = [
    "valid@example.com",
    "user@gmial.com",
    "invalid.email",
    "test@tempmail.com",
    "john.doe@company.co.uk"
]

for email in emails:
    result = validate_email(email, level="syntax")
    status = "✓" if result['valid'] else "✗"
    issues = f" ({', '.join(result['warnings']) if result['warnings'] else 'no issues'})"
    print(f"{status} {email:30} {issues if result.get('warnings') else ''}")
print()

# Example 6: Accessing Detailed Information
print("6. DETAILED VALIDATION RESULT")
print("-" * 80)
result = validate_email("user@example.com", level="syntax")
print(f"Email: {result['email']}")
print(f"Overall Valid: {result['valid']}")
print(f"Syntax Valid: {result['syntax_valid']}")
print(f"Is Disposable: {result.get('is_disposable')}")
print(f"Warnings: {result['warnings']}")
print(f"Suggestions: {result['suggestions']}")
print(f"Message: {result['overall_message']}")
print()

# Example 7: Using EmailValidator Class Directly
print("7. DIRECT CLASS USAGE (Advanced)")
print("-" * 80)
syntax_ok, msg = EmailValidator.is_valid_syntax("test@example.com")
print(f"Syntax Check: {msg}")

has_typo, typo_msg = EmailValidator.detect_typos("test@gmial.com")
if has_typo:
    print(f"Typo Detection: {typo_msg}")

is_disp, disp_msg = EmailValidator.is_disposable("temp@tempmail.com")
if is_disp:
    print(f"Disposable Check: {disp_msg}")
print()

# Example 8: API Usage (HTTP)
print("8. API ENDPOINT USAGE")
print("-" * 80)
print("# Single email validation:")
print('curl -X POST http://localhost:5001/api/validate-email \\')
print('  -H "Content-Type: application/json" \\')
print('  -d \'{"email": "user@example.com", "level": "syntax"}\'')
print()

print("# Batch validation:")
print('curl -X POST http://localhost:5001/api/validate-email \\')
print('  -H "Content-Type: application/json" \\')
print('  -d \'{')
print('    "emails": ["user@example.com", "test@tempmail.com"],')
print('    "level": "syntax"')
print('  }\'')
print()

print("# Send emails with validation:")
print('curl -X POST http://localhost:5001/api/send-now \\')
print('  -H "Content-Type: application/json" \\')
print('  -d \'{')
print('    "limit": 5,')
print('    "recipients": ["user@example.com"]')
print('  }\'')
print()

# Example 9: Validation Levels Comparison
print("9. VALIDATION LEVELS COMPARISON")
print("-" * 80)
email = "test@example.com"
print(f"Testing: {email}")
print()

for level in ["quick", "syntax", "full"]:
    result = validate_email(email, level=level)
    print(f"Level: {level}")
    print(f"  Valid: {result['valid']}")
    print(f"  Syntax: {result['syntax_valid']}")
    print(f"  MX Check: {result.get('mx_valid')}")
    print(f"  Message: {result['overall_message']}")
    print()

print("=" * 80)
print("For more details, see API_VALIDATION.md")
print("=" * 80)

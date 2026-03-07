#!/usr/bin/env python3
"""
Email Delivery Diagnostic Script
Identifies configuration issues preventing email delivery
"""

import os
import sys
import smtplib
from dotenv import load_dotenv
from datetime import datetime
import socket

# Load config
load_dotenv()

SMTP_HOST = os.getenv('SMTP_HOST', 'mail.perinaljournalsubmissions.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', '')
SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'True').lower() == 'true'

print("=" * 70)
print("EMAIL DELIVERY DIAGNOSTIC REPORT")
print("=" * 70)
print()

# 1. Check Configuration
print("1. CONFIGURATION CHECK")
print("-" * 70)

if not SMTP_HOST:
    print("❌ SMTP_HOST is not set")
    sys.exit(1)
else:
    print(f"✅ SMTP_HOST: {SMTP_HOST}:{SMTP_PORT}")

if not SMTP_USERNAME:
    print("❌ SMTP_USERNAME is not set")
    sys.exit(1)
else:
    print(f"✅ SMTP_USERNAME: {SMTP_USERNAME}")

if not SMTP_PASSWORD:
    print("❌ SMTP_PASSWORD is not set")
    sys.exit(1)
else:
    print(f"✅ SMTP_PASSWORD: (set, length={len(SMTP_PASSWORD)})")

if not FROM_EMAIL:
    print("❌ FROM_EMAIL is not set")
    sys.exit(1)
else:
    print(f"✅ FROM_EMAIL: {FROM_EMAIL}")

print()

# 2. Check Sender Authorization (CRITICAL)
print("2. SENDER AUTHORIZATION CHECK ⚠️  CRITICAL")
print("-" * 70)

smtp_domain = SMTP_USERNAME.split('@')[1] if '@' in SMTP_USERNAME else None
from_domain = FROM_EMAIL.split('@')[1] if '@' in FROM_EMAIL else None

if smtp_domain and from_domain:
    if smtp_domain == from_domain:
        print(f"✅ CORRECT: FROM_EMAIL domain ({from_domain}) matches SMTP domain ({smtp_domain})")
    else:
        print(f"❌ ERROR: FROM_EMAIL domain ({from_domain}) does NOT match SMTP domain ({smtp_domain})")
        print(f"   This is likely why emails are not being delivered!")
        print(f"   Solution: Change FROM_EMAIL to an address from {smtp_domain}")
        print(f"   Example: noreply@{smtp_domain} or {SMTP_USERNAME}")
else:
    print("❌ Could not parse email domains")

print()

# 3. Test DNS Resolution
print("3. DNS RESOLUTION CHECK")
print("-" * 70)

try:
    ip = socket.gethostbyname(SMTP_HOST)
    print(f"✅ SMTP host resolves: {SMTP_HOST} → {ip}")
except socket.gaierror:
    print(f"❌ Cannot resolve SMTP host: {SMTP_HOST}")
    print("   This means the SMTP server cannot be reached")
    sys.exit(1)

print()

# 4. Test SMTP Connection
print("4. SMTP CONNECTION CHECK")
print("-" * 70)

try:
    print(f"[*] Connecting to {SMTP_HOST}:{SMTP_PORT}")
    
    smtp = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10)
    print(f"✅ Connected")
    
    if SMTP_USE_TLS:
        print(f"[*] Starting TLS...")
        smtp.starttls()
        print(f"✅ TLS started")
    
    print(f"[*] Authenticating as {SMTP_USERNAME}")
    smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
    print(f"✅ Authentication successful")
    
    smtp.quit()
    print()
    
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ AUTHENTICATION FAILED: {e}")
    print("   Check your SMTP_USERNAME and SMTP_PASSWORD")
    sys.exit(1)
except smtplib.SMTPException as e:
    print(f"❌ SMTP ERROR: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ CONNECTION ERROR: {e}")
    sys.exit(1)

# 5. Recommendations
print("5. RECOMMENDATIONS")
print("-" * 70)

if smtp_domain != from_domain:
    print("⚠️  PRIORITY #1: Fix sender authorization")
    print(f"   Change FROM_EMAIL from '{FROM_EMAIL}' to '{SMTP_USERNAME}'")
    print()

print("NEXT STEPS:")
print("1. If sender authorization is correct, contact your mail provider")
print("2. Ask them to check mail server logs for delivery failures")
print("3. Verify SPF/DKIM/DMARC DNS records are configured")
print("4. See TROUBLESHOOTING.md for detailed diagnostic steps")
print()

print("=" * 70)
print("✅ Diagnostic complete!")
print("=" * 70)

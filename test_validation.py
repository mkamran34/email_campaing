#!/usr/bin/env python3
"""
Test script for email validation features in dashboard
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5001"

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_health_check():
    """Test that dashboard is running"""
    print_header("Test 1: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            print("✓ Dashboard is running")
            return True
        else:
            print("✗ Dashboard not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to dashboard (not running on port 5001)")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_validation_stats():
    """Test getting validation statistics"""
    print_header("Test 2: Get Validation Statistics")
    try:
        response = requests.get(f"{BASE_URL}/api/validation/stats", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('stats', {})
                print(f"✓ Validation Stats Retrieved:")
                print(f"  Total Emails: {stats.get('total', 0)}")
                print(f"  Unchecked: {stats.get('unchecked', 0)}")
                print(f"  Valid: {stats.get('valid', 0)}")
                print(f"  Invalid: {stats.get('invalid', 0)}")
                print(f"  Needs Review: {stats.get('needs_review', 0)}")
                return True
            else:
                print(f"✗ Error: {data.get('error')}")
                return False
        else:
            print(f"✗ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_get_emails():
    """Test getting emails by validation status"""
    print_header("Test 3: Get Emails by Validation Status")
    try:
        response = requests.get(
            f"{BASE_URL}/api/validation/emails?status=unchecked&page=1&limit=10",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                emails = data.get('emails', [])
                print(f"✓ Retrieved {len(emails)} unchecked emails:")
                for i, email in enumerate(emails[:3], 1):
                    print(f"  {i}. {email.get('recipient')}")
                if len(emails) > 3:
                    print(f"  ... and {len(emails) - 3} more")
                return True
            else:
                print(f"✗ Error: {data.get('error')}")
                return False
        else:
            print(f"✗ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_validate_batch_dry_run():
    """Test batch validation (dry run - no actual validation)"""
    print_header("Test 4: Batch Validation (Dry Run)")
    try:
        payload = {
            "validation_status": "unchecked",
            "limit": 5,
            "level": "quick"
        }
        print(f"Sending validation request:")
        print(f"  Status: {payload['validation_status']}")
        print(f"  Limit: {payload['limit']}")
        print(f"  Level: {payload['level']}")
        
        response = requests.post(
            f"{BASE_URL}/api/validation/validate-batch",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✓ Validation Request Successful:")
                print(f"  Validated: {data.get('validated', 0)} emails")
                print(f"  Errors: {data.get('errors', 0)}")
                print(f"  Total Processed: {data.get('total', 0)}")
                
                results = data.get('results', [])
                if results:
                    print(f"  Sample Results:")
                    for i, result in enumerate(results[:3], 1):
                        print(f"    {i}. {result['recipient']} - {result['status']}")
                        if result.get('warnings'):
                            for warning in result['warnings'][:1]:
                                print(f"       ⚠️  {warning}")
                
                return True
            else:
                print(f"✗ Error: {data.get('error')}")
                return False
        else:
            print(f"✗ HTTP Error: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print(f"✗ Request timed out (validation may be taking long)")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_email_validation_api():
    """Test the email validation API endpoint"""
    print_header("Test 5: Email Validation API (Direct)")
    try:
        test_emails = [
            "user@example.com",
            "invalid.email",
            "user@gmial.com"
        ]
        
        payload = {"emails": test_emails, "level": "syntax"}
        response = requests.post(
            f"{BASE_URL}/api/validate-email",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                results = data.get('results', [])
                print(f"✓ Validated {len(results)} emails:")
                for result in results:
                    status = "✓" if result['valid'] else "✗"
                    print(f"  {status} {result['email']}: {result['overall_message'][:50]}...")
                return True
            else:
                print(f"✗ Error: {data.get('error')}")
                return False
        else:
            print(f"✗ HTTP Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("\n")
    print(" " * 70)
    print("  EMAIL VALIDATION SYSTEM - FEATURE TESTS")
    print(" " * 70)
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Dashboard URL: {BASE_URL}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Validation Statistics", test_validation_stats),
        ("Get Emails", test_get_emails),
        ("Batch Validation", test_validate_batch_dry_run),
        ("Email Validation API", test_email_validation_api),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ Unexpected error in {name}: {e}")
            results.append((name, False))
        time.sleep(1)  # Pause between tests
    
    print_header("SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nTests Passed: {passed}/{total}\n")
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print("\n" + "=" * 70)
    
    if passed == total:
        print("  ✓ All tests passed! Validation system is working correctly.")
    elif passed > 0:
        print(f"  ⚠ {passed}/{total} tests passed. Check failed tests above.")
    else:
        print("  ✗ All tests failed. Check dashboard is running on port 5001.")
    
    print("=" * 70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)


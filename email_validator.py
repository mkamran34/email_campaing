"""
Email Validation Module
Provides comprehensive email validation with multiple levels of checking
"""

import re
import socket
import logging
from typing import Tuple, Dict, List
from urllib.request import urlopen
import json

logger = logging.getLogger(__name__)


class EmailValidator:
    """
    Comprehensive email validation with multiple levels of checking:
    - Syntax validation (RFC 5322 compliant)
    - Domain validation (DNS MX records)
    - Common typo detection
    - Disposable email detection
    """
    
    # Regex pattern for email syntax (RFC 5322 simplified)
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    )
    
    # Common email domain typos
    DOMAIN_TYPOS = {
        'gmial.com': 'gmail.com',
        'gmai.com': 'gmail.com',
        'gmal.com': 'gmail.com',
        'gmail.co': 'gmail.com',
        'gmai.co': 'gmail.com',
        'yahooo.com': 'yahoo.com',
        'yaho.com': 'yahoo.com',
        'yahoo.co': 'yahoo.com',
        'hotmial.com': 'hotmail.com',
        'hotmai.com': 'hotmail.com',
        'hotmail.co': 'hotmail.com',
        'outlok.com': 'outlook.com',
        'outloo.com': 'outlook.com',
        'outlook.co': 'outlook.com',
        'aol.co': 'aol.com',
        'protonmail.con': 'protonmail.com',
    }
    
    # Common disposable email providers
    DISPOSABLE_DOMAINS = {
        'tempmail.com',
        'temp-mail.org',
        '10minutemail.com',
        'sharklasers.com',
        'throwaway.email',
        'mailinator.com',
        'maildrop.cc',
        'yopmail.com',
        'spam4.me',
        'fakeinbox.com',
        'trashmail.com',
        'mintemail.com',
        'trycatchmail.com',
        'temp-mail.io',
        'tempmail.co.uk',
        'mytrashmail.com',
    }
    
    @staticmethod
    def is_valid_syntax(email: str) -> Tuple[bool, str]:
        """
        Check if email has valid syntax
        
        Args:
            email: Email address to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        email = email.strip().lower()
        
        # Basic length check
        if len(email) < 5 or len(email) > 254:
            return False, f"Email length must be between 5 and 254 characters (got {len(email)})"
        
        # Check for required @ symbol
        if email.count('@') != 1:
            return False, "Email must contain exactly one @ symbol"
        
        local, domain = email.split('@')
        
        # Check local part (before @)
        if not local or len(local) > 64:
            return False, f"Local part must be 1-64 characters (got {len(local)})"
        
        if local.startswith('.') or local.endswith('.'):
            return False, "Local part cannot start or end with a dot"
        
        if '..' in local:
            return False, "Local part cannot have consecutive dots"
        
        # Check domain part (after @)
        if not domain or len(domain) > 255:
            return False, f"Domain must be 1-255 characters (got {len(domain)})"
        
        if domain.startswith('.') or domain.endswith('.'):
            return False, "Domain cannot start or end with a dot"
        
        if domain.startswith('-') or domain.endswith('-'):
            return False, "Domain cannot start or end with a hyphen"
        
        if '..' in domain:
            return False, "Domain cannot have consecutive dots"
        
        # Regex validation
        if not EmailValidator.EMAIL_REGEX.match(email):
            return False, "Email does not match valid format"
        
        # Check for valid TLD
        domain_parts = domain.split('.')
        if len(domain_parts) < 2:
            return False, "Domain must have at least one dot"
        
        tld = domain_parts[-1]
        if len(tld) < 2:
            return False, "Top-level domain must be at least 2 characters"
        
        if not tld.isalpha():
            return False, "Top-level domain must contain only letters"
        
        return True, "Valid email syntax"
    
    @staticmethod
    def check_domain_mx_records(domain: str) -> Tuple[bool, str]:
        """
        Check if domain has valid MX records (mail servers)
        
        Args:
            domain: Domain to check
            
        Returns:
            Tuple of (has_mx_records, message)
        """
        try:
            # Try to get MX records
            mx_records = socket.getmxrrdata(domain)
            if mx_records:
                mx_hosts = [mx[1].to_text() for mx in mx_records]
                return True, f"Domain has MX records: {', '.join(mx_hosts[:3])}"
            else:
                return False, "Domain has no MX records"
        except (socket.error, AttributeError):
            # Fallback: try basic DNS lookup
            try:
                socket.gethostbyname(domain)
                return True, f"Domain resolves to IP address"
            except socket.gaierror:
                return False, f"Domain does not resolve (no DNS record found)"
        except Exception as e:
            return False, f"Error checking MX records: {str(e)}"
    
    @staticmethod
    def detect_typos(email: str) -> Tuple[bool, str]:
        """
        Detect common domain typos and suggest corrections
        
        Args:
            email: Email address to check
            
        Returns:
            Tuple of (has_typo, message_with_suggestion)
        """
        email = email.strip().lower()
        
        if '@' not in email:
            return False, ""
        
        domain = email.split('@')[1]
        
        if domain in EmailValidator.DOMAIN_TYPOS:
            suggestion = EmailValidator.DOMAIN_TYPOS[domain]
            corrected = email.split('@')[0] + '@' + suggestion
            return True, f"Possible typo detected: '{domain}' → '{suggestion}'. Did you mean '{corrected}'?"
        
        return False, ""
    
    @staticmethod
    def is_disposable(email: str) -> Tuple[bool, str]:
        """
        Check if email uses a disposable/temporary email provider
        
        Args:
            email: Email address to check
            
        Returns:
            Tuple of (is_disposable, message)
        """
        email = email.strip().lower()
        
        if '@' not in email:
            return False, ""
        
        domain = email.split('@')[1]
        
        if domain in EmailValidator.DISPOSABLE_DOMAINS:
            return True, f"Email uses disposable provider: {domain}"
        
        return False, ""
    
    @staticmethod
    def validate_full(
        email: str,
        check_mx: bool = True,
        check_typos: bool = True,
        check_disposable: bool = False
    ) -> Dict[str, any]:
        """
        Perform full email validation with multiple checks
        
        Args:
            email: Email address to validate
            check_mx: Check MX records (may be slow)
            check_typos: Check for common typos
            check_disposable: Check if disposable email provider
            
        Returns:
            Dictionary with validation results:
            {
                'valid': bool,
                'email': str,
                'syntax_valid': bool,
                'syntax_message': str,
                'mx_valid': bool (optional),
                'mx_message': str (optional),
                'typo_detected': bool (optional),
                'typo_message': str (optional),
                'is_disposable': bool (optional),
                'disposable_message': str (optional),
                'warnings': list,
                'suggestions': list,
                'overall_message': str
            }
        """
        result = {
            'valid': True,
            'email': email.strip().lower(),
            'syntax_valid': False,
            'syntax_message': '',
            'warnings': [],
            'suggestions': [],
        }
        
        # 1. Syntax validation (required)
        syntax_valid, syntax_msg = EmailValidator.is_valid_syntax(email)
        result['syntax_valid'] = syntax_valid
        result['syntax_message'] = syntax_msg
        
        if not syntax_valid:
            result['valid'] = False
            result['overall_message'] = f"Invalid email syntax: {syntax_msg}"
            return result
        
        # 2. Check typos (optional)
        if check_typos:
            has_typo, typo_msg = EmailValidator.detect_typos(email)
            result['typo_detected'] = has_typo
            if has_typo:
                result['typo_message'] = typo_msg
                result['warnings'].append(typo_msg)
                result['suggestions'].append(typo_msg)
        
        # 3. Check if disposable (optional)
        if check_disposable:
            is_disp, disp_msg = EmailValidator.is_disposable(email)
            result['is_disposable'] = is_disp
            if is_disp:
                result['disposable_message'] = disp_msg
                result['warnings'].append(disp_msg)
        
        # 4. Check MX records (optional, can be slow)
        if check_mx:
            domain = email.split('@')[1]
            mx_valid, mx_msg = EmailValidator.check_domain_mx_records(domain)
            result['mx_valid'] = mx_valid
            result['mx_message'] = mx_msg
            
            if not mx_valid:
                result['valid'] = False
                result['warnings'].append(f"Domain issue: {mx_msg}")
        
        # Overall message
        if result['warnings']:
            result['overall_message'] = "Email syntax is valid but has issues: " + "; ".join(result['warnings'])
        else:
            result['overall_message'] = "Email is valid and ready to use"
        
        return result


def validate_email(
    email: str,
    level: str = "syntax"
) -> Dict[str, any]:
    """
    Convenience function for email validation
    
    Args:
        email: Email address to validate
        level: Validation level
            - "quick": Syntax only (fastest)
            - "syntax": Syntax + typo detection + disposable check
            - "full": Syntax + MX + typo detection + disposable check (slowest)
            
    Returns:
        Validation result dictionary
    """
    if level == "quick":
        return EmailValidator.validate_full(
            email,
            check_mx=False,
            check_typos=False,
            check_disposable=False
        )
    elif level == "syntax":
        return EmailValidator.validate_full(
            email,
            check_mx=False,
            check_typos=True,
            check_disposable=True
        )
    elif level == "full":
        return EmailValidator.validate_full(
            email,
            check_mx=True,
            check_typos=True,
            check_disposable=True
        )
    else:
        raise ValueError(f"Unknown validation level: {level}")


if __name__ == "__main__":
    """Test the validator"""
    
    test_emails = [
        "test@example.com",
        "invalid.email",
        "user@gmial.com",  # typo
        "test@tempmail.com",  # disposable
        "user.name@company.co.uk",
        "user+tag@gmail.com",
        "invalid@@example.com",
        "user@.com",
        "user@domain",
    ]
    
    print("=" * 80)
    print("EMAIL VALIDATION TEST")
    print("=" * 80)
    print()
    
    for email in test_emails:
        print(f"Email: {email}")
        print("-" * 80)
        
        # Quick validation
        result = validate_email(email, level="syntax")
        
        print(f"Valid: {result['valid']}")
        print(f"Syntax: {result['syntax_message']}")
        
        if result.get('typo_detected'):
            print(f"⚠️  {result['typo_message']}")
        
        if result.get('is_disposable'):
            print(f"⚠️  {result['disposable_message']}")
        
        if result.get('warnings'):
            for warning in result['warnings']:
                print(f"⚠️  {warning}")
        
        print(f"Message: {result['overall_message']}")
        print()

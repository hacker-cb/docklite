"""
Domain validation
"""
import re
from typing import Tuple


# Simple domain regex (not RFC-compliant but practical)
DOMAIN_REGEX = re.compile(
    r'^(?:[a-zA-Z0-9]'  # First character of domain
    r'(?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)'  # Sub-domain + dot
    r'+[a-zA-Z]{2,}$'  # TLD
)


def validate_domain(domain: str) -> Tuple[bool, str]:
    """
    Validate domain name
    
    Args:
        domain: Domain name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not domain or not domain.strip():
        return False, "Domain cannot be empty"
    
    domain = domain.strip().lower()
    
    # Check length
    if len(domain) > 255:
        return False, "Domain is too long (max 255 characters)"
    
    # Check for localhost (allowed in development)
    if domain in ('localhost', '127.0.0.1', '0.0.0.0'):
        return True, ""
    
    # Check for IP address with port
    if ':' in domain:
        parts = domain.split(':')
        if len(parts) == 2 and parts[1].isdigit():
            domain = parts[0]
    
    # Allow IP addresses
    ip_parts = domain.split('.')
    if len(ip_parts) == 4 and all(p.isdigit() and 0 <= int(p) <= 255 for p in ip_parts):
        return True, ""
    
    # Validate domain name
    if not DOMAIN_REGEX.match(domain):
        return False, "Invalid domain format"
    
    return True, ""


def is_valid_domain(domain: str) -> bool:
    """
    Check if domain is valid
    
    Args:
        domain: Domain name
        
    Returns:
        bool: True if valid
    """
    is_valid, _ = validate_domain(domain)
    return is_valid


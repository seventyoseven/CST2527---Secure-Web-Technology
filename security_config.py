from flask import request, jsonify
from functools import wraps
import re
import time
from collections import defaultdict
from datetime import datetime, timedelta

# Rate limiting storage (in production, use Redis or similar)
rate_limit_storage = defaultdict(list)

# Security headers configuration
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; font-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data:; connect-src 'self'",
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
}

def add_security_headers(response):
    """Add security headers to all responses"""
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

def rate_limit(max_requests=100, window_minutes=15):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get client IP
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            if client_ip:
                client_ip = client_ip.split(',')[0].strip()
            
            current_time = time.time()
            window_start = current_time - (window_minutes * 60)
            
            # Clean old entries
            rate_limit_storage[client_ip] = [
                timestamp for timestamp in rate_limit_storage[client_ip]
                if timestamp > window_start
            ]
            
            # Check rate limit
            if len(rate_limit_storage[client_ip]) >= max_requests:
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': window_minutes * 60
                }), 429
            
            # Add current request
            rate_limit_storage[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_input(data, required_fields=None, email_fields=None, phone_fields=None):
    """Validate input data for security and format"""
    errors = []
    
    if required_fields:
        for field in required_fields:
            if field not in data or not data[field]:
                errors.append(f'{field} is required')
    
    if email_fields:
        email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        for field in email_fields:
            if field in data and data[field]:
                if not email_pattern.match(data[field]):
                    errors.append(f'{field} must be a valid email address')
    
    if phone_fields:
        phone_pattern = re.compile(r'^\+?[\d\s\-\(\)]{10,}$')
        for field in phone_fields:
            if field in data and data[field]:
                if not phone_pattern.match(data[field]):
                    errors.append(f'{field} must be a valid phone number')
    
    # Check for potential SQL injection patterns
    sql_injection_patterns = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\'\s*(OR|AND)\s*\'\w*\'\s*=\s*\'\w*\')"
    ]
    
    for field, value in data.items():
        if isinstance(value, str):
            for pattern in sql_injection_patterns:
                if re.search(pattern, value, re.IGNORECASE):
                    errors.append(f'Invalid characters detected in {field}')
                    break
    
    return errors

def validate_password_strength(password):
    """Validate password strength"""
    errors = []
    
    if len(password) < 8:
        errors.append('Password must be at least 8 characters long')
    
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        errors.append('Password must contain at least one number')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append('Password must contain at least one special character')
    
    # Check for common weak passwords
    weak_passwords = [
        'password', '123456', 'password123', 'admin', 'qwerty',
        'letmein', 'welcome', 'monkey', '1234567890'
    ]
    
    if password.lower() in weak_passwords:
        errors.append('Password is too common and weak')
    
    return errors

def sanitize_input(data):
    """Sanitize input data"""
    if isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, str):
        # Remove potentially dangerous characters
        data = re.sub(r'[<>"\']', '', data)
        # Limit length
        return data[:1000]
    else:
        return data

def log_security_event(event_type, details, user_id=None):
    """Log security events for monitoring"""
    timestamp = datetime.utcnow().isoformat()
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')
    
    log_entry = {
        'timestamp': timestamp,
        'event_type': event_type,
        'details': details,
        'user_id': user_id,
        'client_ip': client_ip,
        'user_agent': user_agent,
        'endpoint': request.endpoint,
        'method': request.method
    }
    
    # In production, send this to a proper logging system
    print(f"SECURITY EVENT: {log_entry}")

def check_suspicious_activity(user_id, activity_type):
    """Check for suspicious activity patterns"""
    # This is a simplified implementation
    # In production, you'd want more sophisticated detection
    
    current_time = datetime.utcnow()
    
    # Example: Check for too many failed login attempts
    if activity_type == 'failed_login':
        # In production, store this in a database or cache
        # For now, just log it
        log_security_event('failed_login_attempt', {
            'user_id': user_id,
            'consecutive_failures': 1  # Would track actual count
        })
    
    # Example: Check for unusual access patterns
    elif activity_type == 'data_access':
        log_security_event('data_access', {
            'user_id': user_id,
            'access_time': current_time.isoformat()
        })

def require_https(f):
    """Decorator to require HTTPS in production"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # In production, uncomment this check
        # if not request.is_secure and not app.debug:
        #     return jsonify({'error': 'HTTPS required'}), 400
        return f(*args, **kwargs)
    return decorated_function

# GDPR compliance helpers
def get_data_retention_policy():
    """Get data retention policies for different data types"""
    return {
        'medical_records': {
            'retention_period': '7 years',
            'legal_basis': 'Legal obligation and vital interests'
        },
        'appointment_data': {
            'retention_period': '2 years',
            'legal_basis': 'Contract performance'
        },
        'user_accounts': {
            'retention_period': 'Until account deletion requested',
            'legal_basis': 'Consent and contract performance'
        },
        'audit_logs': {
            'retention_period': '1 year',
            'legal_basis': 'Legitimate interests'
        }
    }

def anonymize_data(data, fields_to_anonymize):
    """Anonymize sensitive data fields"""
    anonymized_data = data.copy()
    
    for field in fields_to_anonymize:
        if field in anonymized_data:
            if field in ['email']:
                anonymized_data[field] = 'anonymized@example.com'
            elif field in ['first_name', 'last_name']:
                anonymized_data[field] = 'ANONYMIZED'
            elif field in ['phone']:
                anonymized_data[field] = 'XXX-XXX-XXXX'
            elif field in ['address']:
                anonymized_data[field] = 'ANONYMIZED ADDRESS'
            else:
                anonymized_data[field] = 'ANONYMIZED'
    
    return anonymized_data

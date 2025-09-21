#!/usr/bin/env python3
"""
Security Configuration and Utilities for Slack Intro Bot

Provides security-focused configuration, input validation, and secure logging utilities.
"""

import os
import re
import logging
import hashlib
import secrets
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class SecurityConfig:
    """Security-specific configuration settings"""
    enable_security_checks: bool = True
    sanitize_input: bool = True
    log_security_events: bool = True
    max_input_length: int = 10000
    allowed_file_extensions: List[str] = None
    max_filename_length: int = 255
    session_timeout_minutes: int = 30
    
    def __post_init__(self):
        if self.allowed_file_extensions is None:
            self.allowed_file_extensions = ['.md', '.txt', '.json']

class InputValidator:
    """Secure input validation utilities"""
    
    # Safe patterns for common data types
    SAFE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-\.\']{1,100}$')
    SAFE_USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]{1,50}$')
    SAFE_DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    SAFE_TIMESTAMP_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$')
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        re.compile(r'[<>"\']', re.IGNORECASE),  # HTML/XML injection
        re.compile(r'javascript:', re.IGNORECASE),  # JavaScript injection
        re.compile(r'data:', re.IGNORECASE),  # Data URI injection
        re.compile(r'vbscript:', re.IGNORECASE),  # VBScript injection
        re.compile(r'on\w+\s*=', re.IGNORECASE),  # Event handlers
        re.compile(r'<script', re.IGNORECASE),  # Script tags
        re.compile(r'<iframe', re.IGNORECASE),  # Iframe tags
        re.compile(r'<object', re.IGNORECASE),  # Object tags
        re.compile(r'<embed', re.IGNORECASE),  # Embed tags
        re.compile(r'<link', re.IGNORECASE),  # Link tags
        re.compile(r'<meta', re.IGNORECASE),  # Meta tags
        re.compile(r'\.\./', re.IGNORECASE),  # Directory traversal
        re.compile(r'\.\.\\', re.IGNORECASE),  # Windows directory traversal
        re.compile(r'[;&|`$]', re.IGNORECASE),  # Command injection
    ]
    
    @classmethod
    def validate_name(cls, name: str) -> bool:
        """Validate a name field"""
        if not name or not isinstance(name, str):
            return False
        return bool(cls.SAFE_NAME_PATTERN.match(name.strip()))
    
    @classmethod
    def validate_username(cls, username: str) -> bool:
        """Validate a username field"""
        if not username or not isinstance(username, str):
            return False
        return bool(cls.SAFE_USERNAME_PATTERN.match(username.strip()))
    
    @classmethod
    def validate_date(cls, date_str: str) -> bool:
        """Validate a date string"""
        if not date_str or not isinstance(date_str, str):
            return False
        return bool(cls.SAFE_DATE_PATTERN.match(date_str.strip()))
    
    @classmethod
    def validate_timestamp(cls, timestamp: str) -> bool:
        """Validate a timestamp string"""
        if not timestamp or not isinstance(timestamp, str):
            return False
        return bool(cls.SAFE_TIMESTAMP_PATTERN.match(timestamp.strip()))
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: int = 10000) -> str:
        """Sanitize text input by removing dangerous patterns"""
        if not text or not isinstance(text, str):
            return ""
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remove dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            text = pattern.sub('', text)
        
        # Remove control characters except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text.strip()
    
    @classmethod
    def validate_filename(cls, filename: str, allowed_extensions: List[str] = None) -> bool:
        """Validate a filename for security"""
        if not filename or not isinstance(filename, str):
            return False
        
        if len(filename) > 255:  # Standard filesystem limit
            return False
        
        # Check for dangerous characters
        if any(char in filename for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            return False
        
        # Check extension if provided
        if allowed_extensions:
            _, ext = os.path.splitext(filename.lower())
            if ext not in allowed_extensions:
                return False
        
        return True

class SecureLogger:
    """Secure logging utilities that avoid logging sensitive information"""
    
    SENSITIVE_PATTERNS = [
        re.compile(r'password["\']?\s*[:=]\s*["\']?[^"\'\s]+', re.IGNORECASE),
        re.compile(r'token["\']?\s*[:=]\s*["\']?[^"\'\s]+', re.IGNORECASE),
        re.compile(r'key["\']?\s*[:=]\s*["\']?[^"\'\s]+', re.IGNORECASE),
        re.compile(r'secret["\']?\s*[:=]\s*["\']?[^"\'\s]+', re.IGNORECASE),
        re.compile(r'api[_-]?key["\']?\s*[:=]\s*["\']?[^"\'\s]+', re.IGNORECASE),
    ]
    
    @classmethod
    def sanitize_log_message(cls, message: str) -> str:
        """Remove sensitive information from log messages"""
        if not message:
            return message
        
        sanitized = message
        for pattern in cls.SENSITIVE_PATTERNS:
            sanitized = pattern.sub(r'\g<0>[REDACTED]', sanitized)
        
        return sanitized
    
    @classmethod
    def log_security_event(cls, logger: logging.Logger, event_type: str, details: str, user_id: str = None):
        """Log security events with consistent formatting"""
        if not logger:
            return
        
        sanitized_details = cls.sanitize_log_message(details)
        user_info = f" user_id={user_id}" if user_id else ""
        
        logger.warning(f"SECURITY_EVENT: {event_type}{user_info} - {sanitized_details}")

class SecurityManager:
    """Main security manager for the application"""
    
    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self.validator = InputValidator()
        self.logger = self._setup_security_logger()
        self.session_tokens = {}  # Simple session management
    
    def _setup_security_logger(self) -> logging.Logger:
        """Setup dedicated security logger"""
        logger = logging.getLogger('security')
        logger.setLevel(logging.WARNING)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def validate_and_sanitize_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize input data"""
        sanitized = {}
        
        for key, value in input_data.items():
            if not isinstance(value, str):
                sanitized[key] = value
                continue
            
            # Apply specific validation based on field name
            if key in ['first_name', 'real_name']:
                if not self.validator.validate_name(value):
                    self.logger.warning(f"Invalid name field: {key}={value[:50]}")
                    sanitized[key] = self.validator.sanitize_text(value, 100)
                else:
                    sanitized[key] = value
            elif key in ['username', 'user_id']:
                if not self.validator.validate_username(value):
                    self.logger.warning(f"Invalid username field: {key}={value[:50]}")
                    sanitized[key] = self.validator.sanitize_text(value, 50)
                else:
                    sanitized[key] = value
            elif key in ['timestamp', 'ts_time']:
                if not self.validator.validate_timestamp(value):
                    self.logger.warning(f"Invalid timestamp field: {key}={value[:50]}")
                    sanitized[key] = ""
                else:
                    sanitized[key] = value
            else:
                # General sanitization for other text fields
                sanitized[key] = self.validator.sanitize_text(value, self.config.max_input_length)
        
        return sanitized
    
    def validate_file_operation(self, filepath: str, operation: str = "read") -> bool:
        """Validate file operations for security"""
        if not filepath or not isinstance(filepath, str):
            return False
        
        # Resolve path to prevent directory traversal
        try:
            abs_path = os.path.abspath(filepath)
            # Ensure the path is within allowed directories
            if not abs_path.startswith(os.path.abspath('.')):
                self.logger.warning(f"File operation blocked - path outside project: {filepath}")
                return False
        except Exception as e:
            self.logger.warning(f"File operation blocked - invalid path: {filepath} - {e}")
            return False
        
        # Check if this is a directory path or if it's a known directory
        is_directory = (
            filepath.endswith('/') or 
            filepath in ['.', './welcome_messages', 'welcome_messages'] or
            (os.path.exists(filepath) and os.path.isdir(filepath))
        )
        
        if is_directory:
            # This is a directory operation, validate directory name
            dirname = os.path.basename(filepath.rstrip('/'))
            if dirname and not self.validator.validate_filename(dirname, []):  # No extension required for directories
                self.logger.warning(f"File operation blocked - invalid directory name: {dirname}")
                return False
        else:
            # This is a file operation, validate filename with extensions
            filename = os.path.basename(filepath)
            if not self.validator.validate_filename(filename, self.config.allowed_file_extensions):
                self.logger.warning(f"File operation blocked - invalid filename: {filename}")
                return False
        
        return True
    
    def generate_session_token(self) -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    def validate_session_token(self, token: str) -> bool:
        """Validate a session token"""
        if not token or token not in self.session_tokens:
            return False
        
        # Check if token has expired
        expiry = self.session_tokens[token]
        if datetime.now() > expiry:
            del self.session_tokens[token]
            return False
        
        return True
    
    def create_session(self) -> str:
        """Create a new session"""
        token = self.generate_session_token()
        expiry = datetime.now() + timedelta(minutes=self.config.session_timeout_minutes)
        self.session_tokens[token] = expiry
        return token
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        now = datetime.now()
        expired_tokens = [
            token for token, expiry in self.session_tokens.items()
            if now > expiry
        ]
        for token in expired_tokens:
            del self.session_tokens[token]

# Global security manager instance
_security_manager = None

def get_security_manager() -> SecurityManager:
    """Get the global security manager instance"""
    global _security_manager
    if _security_manager is None:
        config = SecurityConfig()
        # Load from environment
        config.enable_security_checks = os.getenv('ENABLE_SECURITY_CHECKS', 'true').lower() == 'true'
        config.sanitize_input = os.getenv('SANITIZE_INPUT', 'true').lower() == 'true'
        config.log_security_events = os.getenv('LOG_SECURITY_EVENTS', 'true').lower() == 'true'
        
        _security_manager = SecurityManager(config)
    
    return _security_manager

# Example usage and testing
if __name__ == "__main__":
    # Test security utilities
    security = get_security_manager()
    
    print("🔒 Security Configuration:")
    print(f"   Security checks enabled: {security.config.enable_security_checks}")
    print(f"   Input sanitization enabled: {security.config.sanitize_input}")
    print(f"   Security logging enabled: {security.config.log_security_events}")
    
    # Test input validation
    test_input = {
        'first_name': 'John Doe',
        'username': 'johndoe123',
        'message_text': 'Hello <script>alert("xss")</script> world!',
        'timestamp': '2025-09-21T10:00:00.000Z'
    }
    
    print("\n🧪 Testing input validation:")
    sanitized = security.validate_and_sanitize_input(test_input)
    print(f"   Original: {test_input}")
    print(f"   Sanitized: {sanitized}")
    
    # Test file validation
    print("\n📁 Testing file validation:")
    valid_files = ['daily_intros_2025-09-21.md', 'config.json']
    invalid_files = ['../../../etc/passwd', 'script.js', 'file.exe']
    
    for filepath in valid_files + invalid_files:
        is_valid = security.validate_file_operation(filepath)
        print(f"   {filepath}: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    print("\n🔐 Security utilities initialized successfully!")

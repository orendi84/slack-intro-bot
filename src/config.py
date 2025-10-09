#!/usr/bin/env python3
"""
Configuration Management for Slack Intro Bot

Handles all configuration settings, environment variables, and defaults.
Provides a centralized configuration system with validation and type safety.
"""

import os
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class SlackConfig:
    """Slack-specific configuration settings"""
    channel_name: str = "intros"
    message_search_limit: int = 100
    user_profile_timeout: int = 30
    fallback_timeout: int = 45
    safe_wrapper_timeout: int = 60

@dataclass
class LinkedInConfig:
    """LinkedIn extraction configuration"""
    url_patterns: List[str] = field(default_factory=lambda: [
        r'<https?://(?:www\.)?linkedin\.com/in/[^>]+>',
        r'\(https?://(?:www\.)?linkedin\.com/in/[^)]+\)',
        r'https?://(?:www\.)?linkedin\.com/in/[\w\-\.]+/?(?=\s|$|>|LinkedIn|linkedin)',
        r'https?://(?:www\.)?linkedin\.com/pub/[\w\-\.]+/?(?=\s|$|>)',
        r'linkedin\.com/in/[\w\-\.]+/?(?=\s|$|>)',
        r'linkedin\.com/pub/[\w\-\.]+/?(?=\s|$|>)'
    ])
    profile_fields: List[str] = field(default_factory=lambda: [
        'status_text', 'title', 'phone', 'skype', 'real_name_normalized',
        'display_name', 'display_name_normalized', 'real_name', 'email'
    ])

@dataclass
class OutputConfig:
    """Output and reporting configuration"""
    output_directory: str = "welcome_messages"
    file_permissions: int = 0o600
    date_format: str = "%Y-%m-%d"
    filename_template: str = "daily_intros_{date}.md"

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    enable_emoji_logging: bool = True
    log_file: Optional[str] = None

@dataclass
class WelcomeMessageConfig:
    """Welcome message template configuration"""
    template: str = "Aloha {first_name}!\n\nWelcome to Lenny's podcast community!\n\nHave a wonderful day!"
    fallback_name: str = "there"
    max_name_length: int = 50

class Config:
    """Main configuration class that manages all settings"""

    def __init__(self):
        self.slack = SlackConfig()
        self.linkedin = LinkedInConfig()
        self.output = OutputConfig()
        self.logging = LoggingConfig()
        self.welcome = WelcomeMessageConfig()
        
        # Load from environment variables
        self._load_from_env()
        
        # Validate configuration
        self._validate_config()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Slack configuration
        self.slack.channel_name = os.getenv('SLACK_CHANNEL', self.slack.channel_name)
        self.slack.message_search_limit = int(os.getenv('SLACK_SEARCH_LIMIT', self.slack.message_search_limit))
        self.slack.user_profile_timeout = int(os.getenv('SLACK_PROFILE_TIMEOUT', self.slack.user_profile_timeout))
        self.slack.fallback_timeout = int(os.getenv('SLACK_FALLBACK_TIMEOUT', self.slack.fallback_timeout))
        self.slack.safe_wrapper_timeout = int(os.getenv('SLACK_SAFE_TIMEOUT', self.slack.safe_wrapper_timeout))
        
        # Output configuration
        self.output.output_directory = os.getenv('OUTPUT_DIRECTORY', self.output.output_directory)
        self.output.file_permissions = int(os.getenv('OUTPUT_PERMISSIONS', f"0o{self.output.file_permissions:o}"), 8)
        self.output.date_format = os.getenv('DATE_FORMAT', self.output.date_format)
        self.output.filename_template = os.getenv('FILENAME_TEMPLATE', self.output.filename_template)
        
        # Logging configuration
        self.logging.level = os.getenv('LOG_LEVEL', self.logging.level)
        self.logging.enable_emoji_logging = os.getenv('ENABLE_EMOJI_LOGGING', 'true').lower() == 'true'
        self.logging.log_file = os.getenv('LOG_FILE')
        
        # Welcome message configuration
        self.welcome.template = os.getenv('WELCOME_MESSAGE_TEMPLATE', self.welcome.template)
        self.welcome.fallback_name = os.getenv('FALLBACK_NAME', self.welcome.fallback_name)
        self.welcome.max_name_length = int(os.getenv('MAX_NAME_LENGTH', self.welcome.max_name_length))
    
    def _validate_config(self):
        """Validate configuration settings"""
        # Validate timeouts
        if not (1 <= self.slack.user_profile_timeout <= 300):
            raise ValueError("user_profile_timeout must be between 1 and 300 seconds")
        
        if not (1 <= self.slack.fallback_timeout <= 600):
            raise ValueError("fallback_timeout must be between 1 and 600 seconds")
        
        if not (1 <= self.slack.safe_wrapper_timeout <= 600):
            raise ValueError("safe_wrapper_timeout must be between 1 and 600 seconds")
        
        # Validate search limit
        if not (1 <= self.slack.message_search_limit <= 1000):
            raise ValueError("message_search_limit must be between 1 and 1000")
        
        # Validate output directory
        if not os.path.exists(self.output.output_directory):
            try:
                os.makedirs(self.output.output_directory, mode=0o755, exist_ok=True)
            except OSError as e:
                raise ValueError(f"Cannot create output directory: {e}")
        
        # Validate welcome message template
        if not self.welcome.template.strip():
            raise ValueError("Welcome message template cannot be empty")
        
        if '{first_name}' not in self.welcome.template:
            raise ValueError("Welcome message template must contain {first_name} placeholder")
    
    def get_output_filename(self, date: Optional[datetime] = None) -> str:
        """Generate output filename for given date"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime(self.output.date_format)
        return self.output.filename_template.format(date=date_str)
    
    def get_output_path(self, date: Optional[datetime] = None) -> str:
        """Get full output file path"""
        filename = self.get_output_filename(date)
        return os.path.join(self.output.output_directory, filename)
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.logging.level.upper(), logging.INFO)
        
        # Configure logging format
        if self.logging.enable_emoji_logging:
            format_string = "🔧 %(asctime)s - %(levelname)s - %(message)s"
        else:
            format_string = self.logging.format
        
        # Setup handlers
        handlers = [logging.StreamHandler()]
        
        if self.logging.log_file:
            handlers.append(logging.FileHandler(self.logging.log_file))
        
        # Configure logging
        logging.basicConfig(
            level=log_level,
            format=format_string,
            handlers=handlers
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'slack': {
                'channel_name': self.slack.channel_name,
                'message_search_limit': self.slack.message_search_limit,
                'user_profile_timeout': self.slack.user_profile_timeout,
                'fallback_timeout': self.slack.fallback_timeout,
                'safe_wrapper_timeout': self.slack.safe_wrapper_timeout
            },
            'linkedin': {
                'url_patterns_count': len(self.linkedin.url_patterns),
                'profile_fields': self.linkedin.profile_fields
            },
            'output': {
                'output_directory': self.output.output_directory,
                'file_permissions': f"0o{self.output.file_permissions:o}",
                'date_format': self.output.date_format,
                'filename_template': self.output.filename_template
            },
            'logging': {
                'level': self.logging.level,
                'enable_emoji_logging': self.logging.enable_emoji_logging,
                'log_file': self.logging.log_file
            },
            'welcome': {
                'template_preview': self.welcome.template[:100] + "..." if len(self.welcome.template) > 100 else self.welcome.template,
                'fallback_name': self.welcome.fallback_name,
                'max_name_length': self.welcome.max_name_length
            }
        }

# Global configuration instance
config = Config()

def get_config() -> Config:
    """Get the global configuration instance"""
    return config

def reload_config():
    """Reload configuration from environment variables"""
    global config
    config = Config()
    return config

# Example usage and testing
if __name__ == "__main__":
    # Test configuration loading
    cfg = get_config()
    print("🔧 Configuration loaded successfully!")
    print(f"📋 Config summary: {cfg.to_dict()}")
    
    # Test filename generation
    test_date = datetime.now()
    filename = cfg.get_output_filename(test_date)
    filepath = cfg.get_output_path(test_date)
    print(f"📄 Output filename: {filename}")
    print(f"📁 Full path: {filepath}")
    
    # Test logging setup
    cfg.setup_logging()
    logging.info("✅ Configuration system working correctly!")
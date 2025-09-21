#!/usr/bin/env python3
"""
Test suite for configuration management
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime
from unittest.mock import patch

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config, SlackConfig, LinkedInConfig, OutputConfig

class TestConfig(unittest.TestCase):
    """Test configuration management functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.original_env = os.environ.copy()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_default_config(self):
        """Test default configuration values"""
        config = Config()
        
        # Test Slack config defaults
        self.assertEqual(config.slack.channel_name, "intros")
        self.assertEqual(config.slack.message_search_limit, 100)
        self.assertEqual(config.slack.user_profile_timeout, 30)
        
        # Test LinkedIn config defaults
        self.assertGreater(len(config.linkedin.url_patterns), 0)
        self.assertIn('status_text', config.linkedin.profile_fields)
        
        # Test output config defaults
        self.assertEqual(config.output.output_directory, "welcome_messages")
        self.assertEqual(config.output.file_permissions, 0o600)
    
    def test_environment_override(self):
        """Test configuration override from environment variables"""
        os.environ['SLACK_CHANNEL'] = 'test-channel'
        os.environ['SLACK_SEARCH_LIMIT'] = '50'
        os.environ['SLACK_PROFILE_TIMEOUT'] = '60'
        
        config = Config()
        
        self.assertEqual(config.slack.channel_name, 'test-channel')
        self.assertEqual(config.slack.message_search_limit, 50)
        self.assertEqual(config.slack.user_profile_timeout, 60)
    
    def test_invalid_timeout_validation(self):
        """Test timeout validation"""
        os.environ['SLACK_PROFILE_TIMEOUT'] = '999'  # Too high
        
        with self.assertRaises(ValueError):
            Config()
    
    def test_invalid_search_limit_validation(self):
        """Test search limit validation"""
        os.environ['SLACK_SEARCH_LIMIT'] = '9999'  # Too high
        
        with self.assertRaises(ValueError):
            Config()
    
    def test_output_directory_creation(self):
        """Test automatic output directory creation"""
        test_output_dir = os.path.join(self.test_dir, "test_output")
        os.environ['OUTPUT_DIRECTORY'] = test_output_dir
        
        config = Config()
        
        self.assertTrue(os.path.exists(test_output_dir))
        self.assertEqual(config.output.output_directory, test_output_dir)
    
    def test_filename_generation(self):
        """Test output filename generation"""
        config = Config()
        
        # Test with current date
        filename = config.get_output_filename()
        self.assertTrue(filename.startswith("daily_intros_"))
        self.assertTrue(filename.endswith(".md"))
        
        # Test with specific date
        test_date = datetime(2025, 1, 21)
        filename = config.get_output_filename(test_date)
        self.assertEqual(filename, "daily_intros_2025-01-21.md")
    
    def test_output_path_generation(self):
        """Test full output path generation"""
        config = Config()
        
        path = config.get_output_path()
        self.assertTrue(path.startswith(config.output.output_directory))
        self.assertTrue(path.endswith(".md"))
    
    def test_welcome_message_validation(self):
        """Test welcome message template validation"""
        # Test empty template
        os.environ['WELCOME_MESSAGE_TEMPLATE'] = ''
        
        with self.assertRaises(ValueError):
            Config()
        
        # Test missing placeholder
        os.environ['WELCOME_MESSAGE_TEMPLATE'] = 'Hello!'
        
        with self.assertRaises(ValueError):
            Config()
        
        # Test valid template
        os.environ['WELCOME_MESSAGE_TEMPLATE'] = 'Hello {first_name}!'
        
        config = Config()
        self.assertEqual(config.welcome.template, 'Hello {first_name}!')
    
    def test_to_dict(self):
        """Test configuration serialization to dictionary"""
        config = Config()
        config_dict = config.to_dict()
        
        self.assertIn('slack', config_dict)
        self.assertIn('linkedin', config_dict)
        self.assertIn('output', config_dict)
        self.assertIn('logging', config_dict)
        self.assertIn('welcome', config_dict)
        
        # Test specific values
        self.assertEqual(config_dict['slack']['channel_name'], 'intros')
        self.assertIn('template_preview', config_dict['welcome'])

class TestSlackConfig(unittest.TestCase):
    """Test Slack-specific configuration"""
    
    def test_default_values(self):
        """Test SlackConfig default values"""
        slack_config = SlackConfig()
        
        self.assertEqual(slack_config.channel_name, "intros")
        self.assertEqual(slack_config.message_search_limit, 100)
        self.assertEqual(slack_config.user_profile_timeout, 30)
        self.assertEqual(slack_config.fallback_timeout, 45)
        self.assertEqual(slack_config.safe_wrapper_timeout, 60)

class TestLinkedInConfig(unittest.TestCase):
    """Test LinkedIn-specific configuration"""
    
    def test_url_patterns(self):
        """Test LinkedIn URL patterns"""
        linkedin_config = LinkedInConfig()
        
        self.assertGreater(len(linkedin_config.url_patterns), 0)
        
        # Test that patterns contain expected regex elements
        patterns_text = ' '.join(linkedin_config.url_patterns)
        self.assertIn('linkedin\\.com', patterns_text)  # Escaped for regex
        self.assertIn('linkedin\\.com/in', patterns_text)  # Escaped for regex
    
    def test_profile_fields(self):
        """Test profile fields configuration"""
        linkedin_config = LinkedInConfig()
        
        expected_fields = ['status_text', 'title', 'real_name']
        for field in expected_fields:
            self.assertIn(field, linkedin_config.profile_fields)

if __name__ == '__main__':
    unittest.main()

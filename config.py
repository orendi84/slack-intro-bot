#!/usr/bin/env python3
"""
Configuration management for Slack Intro Bot
Loads settings from environment variables with secure defaults
"""

import os
from typing import Optional
from dotenv import load_dotenv

class Config:
    """Configuration class that loads settings from environment variables"""

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

    @property
    def slack_channel_id(self) -> str:
        """Slack channel ID to monitor"""
        return os.getenv('SLACK_CHANNEL_ID', 'YOUR_CHANNEL_ID_HERE')

    @property
    def slack_bot_token(self) -> Optional[str]:
        """Slack bot token for API access"""
        return os.getenv('SLACK_BOT_TOKEN')

    @property
    def slack_app_token(self) -> Optional[str]:
        """Slack app token for API access"""
        return os.getenv('SLACK_APP_TOKEN')

    @property
    def check_time(self) -> str:
        """Time to run daily check (HH:MM format)"""
        return os.getenv('CHECK_TIME', '08:00')

    @property
    def timezone(self) -> str:
        """Timezone for scheduled runs"""
        return os.getenv('TIMEZONE', 'CET')

    @property
    def output_dir(self) -> str:
        """Directory for output files"""
        return os.getenv('OUTPUT_DIR', './welcome_messages')

    @property
    def log_level(self) -> str:
        """Logging level"""
        return os.getenv('LOG_LEVEL', 'INFO')

    @property
    def zapier_webhook_url(self) -> Optional[str]:
        """Zapier webhook URL for integration"""
        return os.getenv('ZAPIER_WEBHOOK_URL')

    @property
    def zapier_api_key(self) -> Optional[str]:
        """Zapier API key"""
        return os.getenv('ZAPIER_API_KEY')

    @property
    def welcome_message_template(self) -> str:
        """Welcome message template (secured in .env)"""
        template = os.getenv('WELCOME_MESSAGE_TEMPLATE', 'Aloha {first_name}, Welcome to our community!\n\nHave a wonderful day!')
        return template.replace('\\n', '\n')

    @property
    def notification_email(self) -> Optional[str]:
        """Email for notifications"""
        return os.getenv('NOTIFICATION_EMAIL')

    @property
    def smtp_server(self) -> str:
        """SMTP server for email notifications"""
        return os.getenv('SMTP_SERVER', 'smtp.gmail.com')

    @property
    def smtp_port(self) -> int:
        """SMTP port for email notifications"""
        return int(os.getenv('SMTP_PORT', '587'))

    @property
    def smtp_username(self) -> Optional[str]:
        """SMTP username"""
        return os.getenv('SMTP_USERNAME')

    @property
    def smtp_password(self) -> Optional[str]:
        """SMTP password"""
        return os.getenv('SMTP_PASSWORD')

    def validate_required_settings(self) -> bool:
        """Validate that required settings are present"""
        required_settings = [
            ('SLACK_CHANNEL_ID', self.slack_channel_id),
        ]

        missing = []
        for name, value in required_settings:
            if not value:
                missing.append(name)

        if missing:
            print(f"❌ Missing required configuration: {', '.join(missing)}")
            print("Please check your .env file or environment variables.")
            return False

        return True

    def print_config_summary(self):
        """Print configuration summary (without sensitive values)"""
        print("🔧 Configuration Summary:")
        print(f"   Channel ID: {self.slack_channel_id}")
        print(f"   Check Time: {self.check_time} {self.timezone}")
        print(f"   Output Dir: {self.output_dir}")
        print(f"   Log Level: {self.log_level}")
        print(f"   Slack Bot Token: {'✅ Set' if self.slack_bot_token else '❌ Not set'}")
        print(f"   Slack App Token: {'✅ Set' if self.slack_app_token else '❌ Not set'}")
        print(f"   Zapier Webhook: {'✅ Set' if self.zapier_webhook_url else '❌ Not set'}")
        print(f"   Email Notifications: {'✅ Set' if self.notification_email else '❌ Not set'}")

# Global config instance
config = Config()
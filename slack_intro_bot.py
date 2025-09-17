#!/usr/bin/env python3
"""
Slack Intro Bot - Daily check for new introductions in target community
Generates personalized welcome messages for new members
"""

import json
import re
import schedule
import time
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import requests
import os

class SlackIntroBot:
    def __init__(self, channel_id: str = "C0142RHUS4Q", check_time: str = "08:00", timezone_str: str = "CET"):
        self.channel_id = channel_id
        self.check_time = check_time
        self.timezone_str = timezone_str
        self.zapier_base_url = "https://hooks.zapier.com/hooks/catch/"  # You'll need to configure this
        self.last_check_file = "last_check.txt"

    def get_last_check_time(self) -> datetime:
        """Get the timestamp of the last check from file"""
        try:
            if os.path.exists(self.last_check_file):
                with open(self.last_check_file, 'r') as f:
                    timestamp = float(f.read().strip())
                    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except (FileNotFoundError, ValueError):
            pass

        # Default to 24 hours ago if no last check found
        return datetime.now(timezone.utc) - timedelta(days=1)

    def save_last_check_time(self, timestamp: datetime):
        """Save the timestamp of the current check to file"""
        with open(self.last_check_file, 'w') as f:
            f.write(str(timestamp.timestamp()))

    def extract_linkedin_link(self, text: str) -> Optional[str]:
        """Extract LinkedIn profile link from message text"""
        # Pattern for LinkedIn profile URLs
        linkedin_patterns = [
            r'https?://(?:www\.)?linkedin\.com/in/[^\s>]+',
            r'https?://(?:www\.)?linkedin\.com/posts/[^\s>]+',
        ]

        for pattern in linkedin_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Clean up any trailing characters or markdown
                url = match.group(0)
                url = re.sub(r'[>)\]]+$', '', url)
                return url

        return None

    def extract_first_name(self, real_name: str, username: str, text: str) -> str:
        """Extract first name from user data"""
        if real_name:
            # Try to get first name from real_name
            first_name = real_name.split()[0] if real_name.split() else real_name
            return first_name

        # Fallback to username
        return username if username else "there"

    def parse_intro_message(self, message: Dict) -> Optional[Dict]:
        """Parse a Slack message to extract intro information"""
        user = message.get('user', {})
        text = message.get('text', '') or message.get('raw_text', '')

        # Check if this looks like an intro message
        intro_keywords = ['hi everyone', 'hello everyone', 'hey everyone', 'i\'m ', 'my name is', 'introduction']
        text_lower = text.lower()

        if not any(keyword in text_lower for keyword in intro_keywords):
            return None

        real_name = user.get('real_name', '')
        username = user.get('name', '')
        first_name = self.extract_first_name(real_name, username, text)
        linkedin_link = self.extract_linkedin_link(text)

        return {
            'first_name': first_name,
            'real_name': real_name,
            'username': username,
            'linkedin_link': linkedin_link,
            'message_text': text,
            'timestamp': message.get('ts_time', ''),
            'user_id': user.get('id', '')
        }

    def get_new_messages_since_last_check(self) -> List[Dict]:
        """Get new messages from Slack channel since last check using MCP Zapier integration"""
        # This would use the Zapier MCP integration
        # For now, returning empty list as we'd need to implement the actual Zapier call
        print(f"Checking for new messages in channel {self.channel_id}")
        print("Note: This would use Zapier MCP integration to fetch messages")
        return []

    def generate_welcome_message(self, intro_data: Dict) -> str:
        """Generate personalized welcome message"""
        first_name = intro_data['first_name'].capitalize()
        return self.config.welcome_message_template.format(first_name=first_name)

    def process_new_intros(self):
        """Main function to process new introductions"""
        print(f"🤖 Running intro check at {datetime.now()}")

        last_check = self.get_last_check_time()
        print(f"📅 Last check was at: {last_check}")

        # Get new messages (this would use the actual Zapier integration)
        new_messages = self.get_new_messages_since_last_check()

        intro_count = 0
        for message in new_messages:
            intro_data = self.parse_intro_message(message)
            if intro_data:
                intro_count += 1
                welcome_msg = self.generate_welcome_message(intro_data)

                print(f"\n📝 New intro detected:")
                print(f"   Name: {intro_data['first_name']}")  # Only show first name
                print(f"   LinkedIn: {'✅ Provided' if intro_data['linkedin_link'] else '❌ Not provided'}")
                print(f"   Generated message:")
                print(f"   {welcome_msg}")

                # Here you could send the welcome message back to Slack
                # or save it to a file for manual review
                self.save_welcome_message(intro_data, welcome_msg)

        print(f"\n✅ Found {intro_count} new introductions")

        # Update last check time
        current_time = datetime.now(timezone.utc)
        self.save_last_check_time(current_time)
        print(f"💾 Updated last check time to: {current_time}")

    def save_welcome_message(self, intro_data: Dict, welcome_msg: str):
        """Save welcome message to file for review"""
        filename = f"welcome_messages_{datetime.now().strftime('%Y%m%d')}.txt"

        with open(filename, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Time: {datetime.now()}\n")
            f.write(f"User: {intro_data['real_name']} (@{intro_data['username']})\n")
            f.write(f"LinkedIn: {intro_data['linkedin_link'] or 'Not provided'}\n")
            f.write(f"Message:\n{welcome_msg}\n")
            f.write(f"Original intro:\n{intro_data['message_text'][:200]}...\n")

    def start_scheduler(self):
        """Start the daily scheduler"""
        print(f"🚀 Starting Slack Intro Bot")
        print(f"📅 Scheduled to run daily at {self.check_time} {self.timezone_str}")
        print(f"📢 Monitoring channel: {self.channel_id}")

        # Schedule the daily check
        schedule.every().day.at(self.check_time).do(self.process_new_intros)

        # Run once immediately for testing
        print("\n🧪 Running initial check...")
        self.process_new_intros()

        # Keep the scheduler running
        print("\n⏰ Scheduler started. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n👋 Scheduler stopped.")

def main():
    """Main entry point with configurable parameters"""
    # Configuration
    CHANNEL_ID = "YOUR_CHANNEL_ID_HERE"  # Target intro channel
    CHECK_TIME = "08:00"        # 8 AM
    TIMEZONE = "CET"            # Central European Time

    # Create and start the bot
    bot = SlackIntroBot(
        channel_id=CHANNEL_ID,
        check_time=CHECK_TIME,
        timezone_str=TIMEZONE
    )

    bot.start_scheduler()

if __name__ == "__main__":
    main()
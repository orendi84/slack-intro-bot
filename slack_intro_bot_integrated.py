#!/usr/bin/env python3
"""
Slack Intro Bot - Integrated with MCP Zapier
Daily check for new introductions in target community with actual Slack integration
"""

import json
import re
import schedule
import time
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from config import config

class SlackIntroBotIntegrated:
    def __init__(self, channel_id: str = None, check_time: str = None, timezone_str: str = None):
        self.channel_id = channel_id or config.slack_channel_id
        self.check_time = check_time or config.check_time
        self.timezone_str = timezone_str or config.timezone
        self.last_check_file = "last_check.txt"

    def get_last_check_time(self) -> datetime:
        """Get the timestamp of the last check from file"""
        try:
            with open(self.last_check_file, 'r') as f:
                timestamp = float(f.read().strip())
                return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except (FileNotFoundError, ValueError):
            # Default to 24 hours ago if no last check found
            return datetime.now(timezone.utc) - timedelta(days=1)

    def save_last_check_time(self, timestamp: datetime):
        """Save the timestamp of the current check to file"""
        with open(self.last_check_file, 'w') as f:
            f.write(str(timestamp.timestamp()))

    def extract_linkedin_link(self, text: str) -> Optional[str]:
        """Extract LinkedIn profile link from message text"""
        linkedin_patterns = [
            r'https?://(?:www\.)?linkedin\.com/in/[^\s>)\]]+',
            r'https?://(?:www\.)?linkedin\.com/posts/[^\s>)\]]+',
        ]

        for pattern in linkedin_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                url = match.group(0)
                # Clean up any trailing characters
                url = re.sub(r'[>)\]]+$', '', url)
                return url

        return None

    def extract_first_name(self, real_name: str, username: str) -> str:
        """Extract first name from user data"""
        if real_name:
            first_name = real_name.split()[0] if real_name.split() else real_name
            return first_name
        return username if username else "there"

    def is_intro_message(self, text: str) -> bool:
        """Check if message looks like an introduction"""
        intro_keywords = [
            'hi everyone', 'hello everyone', 'hey everyone', 'hey all',
            'i\'m ', 'my name is', 'introduction', 'nice to meet',
            'pleased to meet', 'excited to be here', 'happy to be here'
        ]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in intro_keywords)

    def validate_channel_id(self, channel_id: str) -> bool:
        """Validate Slack channel ID format for security"""
        import re
        # Slack channel IDs should start with C and be alphanumeric
        if not channel_id or not isinstance(channel_id, str):
            return False
        # Basic format validation: starts with C followed by alphanumeric characters
        pattern = r'^C[A-Z0-9]{8,}$'
        return bool(re.match(pattern, channel_id))

    def sanitize_command_arg(self, arg: str) -> str:
        """Sanitize command line arguments to prevent injection"""
        if not arg or not isinstance(arg, str):
            return ""
        # Remove potentially dangerous characters
        import re
        # Allow alphanumeric, spaces, hyphens, underscores, colons, and basic punctuation
        sanitized = re.sub(r'[^a-zA-Z0-9\s\-_:.,#]', '', arg)
        # Limit length to prevent buffer overflow
        return sanitized[:200]

    def get_new_slack_messages(self) -> List[Dict]:
        """Get new messages from Slack using Claude Code MCP integration"""
        try:
            # Validate channel ID before use
            if not self.validate_channel_id(self.channel_id):
                print(f"Error: Invalid channel ID format: {self.channel_id}")
                return []

            # Sanitize all inputs
            sanitized_channel_id = self.sanitize_command_arg(self.channel_id)
            sanitized_date = self.sanitize_command_arg(self.get_yesterday_date())
            
            # Use Claude Code to call the Zapier MCP integration
            # This simulates calling: mcp__zapier__slack_find_message
            cmd = [
                'claude', 'mcp', 'call', 'mcp__zapier__slack_find_message',
                '--instructions', f'Find messages in channel {sanitized_channel_id} from the last 24 hours, sorted by most recent',
                '--query', f'in:#intros after:{sanitized_date}',
                '--sort_by', 'timestamp',
                '--sort_dir', 'desc'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                # Parse the JSON response
                response = json.loads(result.stdout)
                return response.get('results', [])
            else:
                print(f"Error calling Slack API: {result.stderr}")
                return []

        except subprocess.TimeoutExpired:
            print("Error: Command timed out")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing API response: {e}")
            return []
        except Exception as e:
            print(f"Error getting Slack messages: {e}")
            return []

    def get_yesterday_date(self) -> str:
        """Get yesterday's date in YYYY-MM-DD format for Slack search"""
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime('%Y-%m-%d')

    def parse_intro_message(self, message: Dict) -> Optional[Dict]:
        """Parse a Slack message to extract intro information"""
        user = message.get('user', {})
        text = message.get('text', '') or message.get('raw_text', '')

        # Check if this looks like an intro message
        if not self.is_intro_message(text):
            return None

        real_name = user.get('real_name', '')
        username = user.get('name', '')
        first_name = self.extract_first_name(real_name, username)
        linkedin_link = self.extract_linkedin_link(text)

        return {
            'first_name': first_name,
            'real_name': real_name,
            'username': username,
            'linkedin_link': linkedin_link,
            'message_text': text,
            'timestamp': message.get('ts_time', ''),
            'user_id': user.get('id', ''),
            'permalink': message.get('permalink', '')
        }

    def generate_welcome_message(self, intro_data: Dict) -> str:
        """Generate personalized welcome message"""
        first_name = intro_data['first_name'].capitalize()
        return self.config.welcome_message_template.format(first_name=first_name)

    def process_new_intros(self):
        """Main function to process new introductions"""
        print(f"🤖 Running intro check at {datetime.now()}")

        # Get new messages from Slack
        messages = self.get_new_slack_messages()
        print(f"📨 Found {len(messages)} messages to check")

        intro_count = 0
        welcome_messages = []

        for message in messages:
            intro_data = self.parse_intro_message(message)
            if intro_data:
                intro_count += 1
                welcome_msg = self.generate_welcome_message(intro_data)
                welcome_messages.append((intro_data, welcome_msg))

                print(f"\n📝 New intro detected:")
                print(f"   Name: {intro_data['first_name']}")  # Only show first name
                print(f"   LinkedIn: {'✅ Provided' if intro_data['linkedin_link'] else '❌ Not provided'}")
                print(f"   Message: {welcome_msg}")

        # Save all welcome messages to file
        if welcome_messages:
            self.save_welcome_messages(welcome_messages)

        print(f"\n✅ Processed {intro_count} new introductions")

        # Update last check time
        current_time = datetime.now(timezone.utc)
        self.save_last_check_time(current_time)

    def save_welcome_messages(self, welcome_messages: List[tuple]):
        """Save welcome messages to file"""
        os.makedirs(config.output_dir, exist_ok=True)
        filename = os.path.join(config.output_dir, f"daily_intros_{datetime.now().strftime('%Y-%m-%d')}.md")

        with open(filename, 'w', encoding='utf-8') as f:
            date_str = datetime.now().strftime('%Y-%m-%d')
            f.write(f"# Daily Introductions - {date_str}\n\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if not welcome_messages:
                f.write("*No new introductions found today.*\n")
                return filename

            f.write(f"## Summary\n\n")
            f.write(f"Found **{len(welcome_messages)}** new introduction(s) today.\n\n")
            f.write("---\n\n")

            for i, (intro_data, welcome_msg) in enumerate(welcome_messages, 1):
                f.write(f"## {i}. {intro_data['real_name']}\n\n")

                # User info section
                f.write("### 👤 User Information\n")
                f.write(f"- **Name:** {intro_data['real_name']}\n")
                f.write(f"- **Username:** @{intro_data['username']}\n")

                if intro_data['linkedin_link']:
                    f.write(f"- **LinkedIn:** [{intro_data['linkedin_link']}]({intro_data['linkedin_link']})\n")
                else:
                    f.write("- **LinkedIn:** *Not provided*\n")

                if intro_data.get('permalink'):
                    f.write(f"- **Message Link:** [View in Slack]({intro_data['permalink']})\n")

                f.write(f"- **Posted:** {intro_data.get('timestamp', 'Unknown')}\n\n")

                # Welcome message section
                f.write("### 💬 Draft Welcome Message\n\n")
                f.write("```\n")
                f.write(welcome_msg)
                f.write("\n```\n\n")

                # Original intro section
                f.write("### 📝 Original Introduction\n\n")
                f.write("> ")
                formatted_intro = intro_data['message_text'].replace('\n', '\n> ')
                f.write(formatted_intro)
                f.write("\n\n")

                if i < len(welcome_messages):
                    f.write("---\n\n")

        print(f"💾 Welcome messages saved to: {filename}")

    def run_once(self):
        """Run the intro check once (for testing)"""
        print("🧪 Running one-time intro check...")
        self.process_new_intros()

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

        print("\n⏰ Scheduler started. Press Ctrl+C to stop.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n👋 Scheduler stopped.")

def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='Slack Intro Bot for Community Management')
    parser.add_argument('--channel', help='Slack channel ID (overrides .env)')
    parser.add_argument('--time', help='Daily check time (HH:MM format, overrides .env)')
    parser.add_argument('--timezone', help='Timezone for scheduled runs (overrides .env)')
    parser.add_argument('--run-once', action='store_true', help='Run once and exit (for testing)')
    parser.add_argument('--config', action='store_true', help='Show configuration and exit')

    args = parser.parse_args()

    if args.config:
        config.print_config_summary()
        return

    # Validate configuration
    if not config.validate_required_settings():
        sys.exit(1)

    bot = SlackIntroBotIntegrated(
        channel_id=args.channel,
        check_time=args.time,
        timezone_str=args.timezone
    )

    if args.run_once:
        bot.run_once()
    else:
        bot.start_scheduler()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Slack Intro Bot - Cron Version
Designed to be run as a daily cron job to check for new introductions
"""

import json
import re
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from config import config

def extract_linkedin_link(text: str) -> Optional[str]:
    """Extract LinkedIn profile link from message text"""
    linkedin_patterns = [
        r'https?://(?:www\.)?linkedin\.com/in/[^\s>)\]]+',
        r'https?://(?:www\.)?linkedin\.com/posts/[^\s>)\]]+',
    ]

    for pattern in linkedin_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            url = match.group(0)
            url = re.sub(r'[>)\]]+$', '', url)
            return url
    return None

def extract_first_name(real_name: str, username: str) -> str:
    """Extract first name from user data"""
    if real_name:
        first_name = real_name.split()[0] if real_name.split() else real_name
        return first_name
    return username if username else "there"

def is_intro_message(text: str) -> bool:
    """Check if message looks like an introduction"""
    intro_keywords = [
        'hi everyone', 'hello everyone', 'hey everyone', 'hey all',
        'i\'m ', 'my name is', 'introduction', 'nice to meet',
        'pleased to meet', 'excited to be here', 'happy to be here'
    ]
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in intro_keywords)

def parse_intro_message(message: Dict) -> Optional[Dict]:
    """Parse a Slack message to extract intro information"""
    user = message.get('user', {})
    text = message.get('text', '') or message.get('raw_text', '')

    if not is_intro_message(text):
        return None

    real_name = user.get('real_name', '')
    username = user.get('name', '')
    first_name = extract_first_name(real_name, username)
    linkedin_link = extract_linkedin_link(text)

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

def generate_welcome_message(intro_data: Dict) -> str:
    """Generate personalized welcome message"""
    config = Config()
    first_name = intro_data['first_name'].capitalize()
    return config.welcome_message_template.format(first_name=first_name)

def get_yesterday_date() -> str:
    """Get yesterday's date in YYYY-MM-DD format"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime('%Y-%m-%d')

def log_message(message: str):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def save_welcome_messages_markdown(welcome_messages: List[tuple], output_dir: str = "."):
    """Save welcome messages to markdown file"""
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = os.path.join(output_dir, f"daily_intros_{date_str}.md")

    with open(filename, 'w', encoding='utf-8') as f:
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
            # Format the intro text with proper line breaks for markdown
            formatted_intro = intro_data['message_text'].replace('\n', '\n> ')
            f.write(formatted_intro)
            f.write("\n\n")

            if i < len(welcome_messages):
                f.write("---\n\n")

    return filename

def main():
    """Main function for cron execution"""
    log_message("🤖 Starting Slack Intro Bot (Cron Mode)")

    # Validate configuration
    if not config.validate_required_settings():
        sys.exit(1)

    # Print configuration summary
    config.print_config_summary()

    log_message(f"📢 Monitoring channel: {config.slack_channel_id}")

    # Ensure output directory exists
    os.makedirs(config.output_dir, exist_ok=True)

    # For cron mode, we would need to implement actual Slack API integration
    # For now, this is a template that shows the structure
    log_message("⚠️  Note: This is a template. Actual Slack integration needs to be implemented.")
    log_message("    You would need to:")
    log_message("    1. Add Slack API token to environment variables")
    log_message("    2. Implement actual API calls to fetch messages")
    log_message("    3. Filter messages from the last 24 hours")

    # Simulate processing (in real implementation, this would fetch from Slack)
    welcome_messages = []

    # Always generate markdown file, even if no introductions found
    filename = save_welcome_messages_markdown(welcome_messages, config.output_dir)
    log_message(f"💾 Daily intro report saved to: {filename}")

    if welcome_messages:
        log_message(f"✅ Processed {len(welcome_messages)} new introductions")
    else:
        log_message("📭 No new introductions found today")

    log_message("🏁 Slack Intro Bot completed")

if __name__ == "__main__":
    main()
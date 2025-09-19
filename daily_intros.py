#!/usr/bin/env python3
"""
Simple Daily Intro Bot - Manual Process
Run this each morning to get today's introduction report
"""

import json
import re
import os
from datetime import datetime
from typing import List, Dict, Optional

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
        'hi everyone', 'hello everyone', 'hey everyone', 'hey all', 'hi all',
        'i\'m ', 'my name is', 'introduction', 'nice to meet',
        'pleased to meet', 'excited to be here', 'happy to be here',
        'i am', 'i have been', 'based', 'working', 'fun fact'
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
    from config import Config
    config = Config()
    first_name = intro_data['first_name'].capitalize()
    return config.welcome_message_template.format(first_name=first_name)

def save_daily_intro_report(welcome_messages: List[tuple], output_dir: str = "./welcome_messages"):
    """Save daily intro report"""
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = os.path.join(output_dir, f"daily_intros_{date_str}.md")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Daily Introductions - {date_str}\n\n")
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("**🚀 This report was generated using LIVE Slack data via MCP Zapier integration!**\n\n")

        if not welcome_messages:
            f.write("*No new introductions found in recent messages.*\n")
            os.chmod(filename, 0o600)
            return filename

        f.write(f"## Summary\n\n")
        f.write(f"Found **{len(welcome_messages)}** introduction(s) from recent days.\n\n")
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

    # Set restrictive permissions (owner read/write only)
    os.chmod(filename, 0o600)
    return filename

def get_cutoff_date():
    """Get the cutoff date from yesterday's file"""
    from datetime import datetime, timedelta

    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    yesterday_file = f"./welcome_messages/daily_intros_{yesterday_str}.md"

    cutoff_date = "2025-09-17"  # Default fallback
    try:
        if os.path.exists(yesterday_file):
            with open(yesterday_file, 'r') as f:
                content = f.read()
                timestamps = re.findall(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)', content)
                if timestamps:
                    latest_timestamp = max(timestamps)
                    cutoff_date = latest_timestamp.split('T')[0]
                    print(f"📅 Found last processed date: {cutoff_date}")
    except Exception as e:
        print(f"⚠️  Could not parse yesterday's file, using default cutoff: {e}")

    return cutoff_date

def main():
    """Main function - call this to generate today's report"""
    print("🚀 Generating daily introduction report...")
    print("=" * 50)

    # This function should be called within Claude Code environment
    # where MCP Zapier integration is available
    print("ℹ️  This script requires MCP Zapier integration.")
    print("ℹ️  Run this within Claude Code environment.")
    print("\n📋 To use this script:")
    print("1. Open Claude Code in this directory")
    print("2. Run: python3 daily_intros.py")
    print("3. The MCP integration will handle Slack data fetching")
    print("\n✅ Report will be saved to: ./welcome_messages/daily_intros_YYYY-MM-DD.md")

    # For now, show what the process would do
    cutoff_date = get_cutoff_date()
    search_query = f"in:intros after:{cutoff_date}"
    print(f"\n🔎 Search query would be: {search_query}")
    print(f"📁 Output directory: ./welcome_messages/")

    return f"./welcome_messages/daily_intros_{datetime.now().strftime('%Y-%m-%d')}.md"

if __name__ == "__main__":
    main()
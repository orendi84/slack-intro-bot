#!/usr/bin/env python3
"""
Test Slack Intro Bot - Using actual Zapier MCP integration
"""

import json
import re
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
            # Clean up trailing characters
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

    # Check if this looks like an intro message
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

def test_with_sample_data():
    """Test the bot with the sample data we retrieved earlier"""

    # Sample data from the earlier Slack query
    sample_messages = [
        {
            "user": {"real_name": "Chance McCallister", "name": "mcallisterchance"},
            "text": "Hi all,\n\nI'm Chance, a product designer from Canada.\n\nWhere you're based: Melbourne, Australia\n\nWhat you're working on: research project on the history of special economic zones + multi-country visa product (think Schengen visa for remote workers).\n\nA fun fact about yourself: did a marathon once in North Korea\n\nOpen for DMs here for convos.\nhttps://x.com/chancecollabsX>",
            "ts_time": "2025-09-17T07:08:21.000Z"
        },
        {
            "user": {"real_name": "Maksim Mazhov", "name": "maxim.mazhov"},
            "text": "Hey everyone!\nI've been moving here in silence for some time, but it's time to tell a bit about myself\n\nI'm Maksim, a Senior PM based in the US. For the last four years, I've been at career.io helping people build better resumes and land their dream jobs.\n\nFun fact: Over the last three years, I've lived in 80+ places across 16 countries with just one suitcase.\n\nFeel free to ping me here or connect on LinkedIn: http://linkedin.com/in/mazhov",
            "ts_time": "2025-09-16T13:26:40.000Z"
        }
    ]

    print("🧪 Testing Slack Intro Bot with sample data\n")
    print("="*60)

    welcome_messages = []

    for i, message in enumerate(sample_messages, 1):
        print(f"\n📨 Processing message {i}:")

        intro_data = parse_intro_message(message)
        if intro_data:
            welcome_msg = generate_welcome_message(intro_data)
            welcome_messages.append((intro_data, welcome_msg))

            print(f"✅ Intro detected!")
            print(f"   Name: {intro_data['first_name']} ({intro_data['real_name']})")
            print(f"   LinkedIn: {intro_data['linkedin_link'] or 'Not provided'}")
            print(f"   Welcome Message:")
            print(f"   {welcome_msg}")
        else:
            print("❌ Not recognized as intro message")

    print(f"\n🎉 Test completed! Found {len(welcome_messages)} introductions.")

    # Save test results as markdown
    if welcome_messages:
        filename = f"test_daily_intros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# Test Run - Daily Introductions\n\n")
            f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Summary\n\n")
            f.write(f"Found **{len(welcome_messages)}** introduction(s) in test data.\n\n")
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

                f.write(f"- **Posted:** {intro_data.get('timestamp', 'Test data')}\n\n")

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

        print(f"💾 Test results saved to: {filename}")

if __name__ == "__main__":
    test_with_sample_data()
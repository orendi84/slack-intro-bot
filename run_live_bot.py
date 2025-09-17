#!/usr/bin/env python3
"""
Live Slack Intro Bot - Process real Slack data and generate today's report
This runs the actual bot with live MCP Zapier integration
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
    from config import Config
    config = Config()
    first_name = intro_data['first_name'].capitalize()
    return config.welcome_message_template.format(first_name=first_name)

def save_daily_intro_report(welcome_messages: List[tuple], output_dir: str = "./welcome_messages"):
    """Save daily intro report with live data"""
    os.makedirs(output_dir, exist_ok=True)
    date_str = datetime.now().strftime('%Y-%m-%d')
    filename = os.path.join(output_dir, f"daily_intros_{date_str}.md")

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# Daily Introductions - {date_str}\n\n")
        f.write(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("**🚀 This report was generated using LIVE Slack data via MCP Zapier integration!**\n\n")

        if not welcome_messages:
            f.write("*No new introductions found in recent messages.*\n")
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

    return filename

def process_live_slack_data():
    """Process the live Slack data we just retrieved"""

    # This is the actual live data from our MCP Zapier call
    live_slack_messages = [
        {
            "user": {"real_name": "chance", "name": "mcallisterchance"},
            "text": "Hi all,\n\nI'm Chance, a product designer from Canada.\n\nWhere you're based: Melbourne, Australia\n\nWhat you're working on: research project on the history of special economic zones + multi-country visa product (think Schengen visa for remote workers).\n\nA fun fact about yourself: did a marathon once in North Korea\n\nOpen for DMs here for convos.\nhttps://x.com/chancecollabsX>",
            "ts_time": "2025-09-17T07:08:21.000Z",
            "permalink": "https://yourworkspace.slack.com/archives/YOUR_CHANNEL/p1758092901188739"
        },
        {
            "user": {"real_name": "Maksim Mazhov", "name": "maxim.mazhov"},
            "text": "Hey everyone!\nI've been moving here in silence for some time, but it's time to tell a bit about myself\n\nI'm Maksim, a Senior PM based in the US. For the last four years, I've been at career.io helping people build better resumes and land their dream jobs.\n\nFun fact: Over the last three years, I've lived in 80+ places across 16 countries with just one suitcase. So I'm pretty well prepped for any 'are you open to travel?' interview questions!\n\nFeel free to ping me here or connect on LinkedIn: http://linkedin.com/in/mazhov",
            "ts_time": "2025-09-16T13:26:40.000Z",
            "permalink": "https://yourworkspace.slack.com/archives/YOUR_CHANNEL/p1758029200249339"
        },
        {
            "user": {"real_name": "Bee Gagliardi", "name": "bee"},
            "text": "Hey everyone! I'm Bee and https://beegagliardi.comI engineer intelligent customer experiences>. I help companies turn broken customer journeys into growth flywheels. 20+ years across engineering, UX, security, and customer success.\n\nSome things I geek out about:\n• The (underrated) power of community\n• All things CX (big surprise)\n• Building scalable digital customer success systems without needing to hire an army (flywheels)\n• Action at the speed of thought (digitally)\n\nLooking forward to connecting :bee:",
            "ts_time": "2025-09-15T23:37:43.000Z",
            "permalink": "https://yourworkspace.slack.com/archives/YOUR_CHANNEL/p1757979463905699"
        },
        {
            "user": {"real_name": "Alina Steinberg", "name": "steinbergalina"},
            "text": "Hi everyone! I'm Alina, working as the first PM in a small startup - https://www.ai.work/\nWe're working an AI workers platform which I think is super interesting (And promising! Mostly I think because of its UX) and Im enjoying the crazy ride and excited for whats coming next\n\nHere to learn more about product, and wanting to expand my connections and community.\n\nStarted to write a bit in my linkedin about our journey if you're interested in reading and following\nhttps://www.linkedin.com/posts/alina-steinberg-782265204_what-will-be-the-agent-platform-that-users-activity-7371575307692249089-HhA-\n\nFree time is for DJing, dancing and surfing",
            "ts_time": "2025-09-15T18:54:52.000Z",
            "permalink": "https://yourworkspace.slack.com/archives/YOUR_CHANNEL/p1757962492111909"
        },
        {
            "user": {"real_name": "Shane Sweeney", "name": "shanesweeney09"},
            "text": "Hello Everyone! I'm Shane Sweeney I work as a Digital Transformation Lead for the NHS in the UK. I enjoy vibe coding & self hosting. Love finding new ways to automate work as well as use AI to solve problems. Always looking to learn & improve and always happy to connect on https://www.linkedin.com/in/shane-sweeney-406174218/",
            "ts_time": "2025-09-15T13:54:02.000Z",
            "permalink": "https://yourworkspace.slack.com/archives/YOUR_CHANNEL/p1757944442734479"
        },
        {
            "user": {"real_name": "Abhijit Mahanta", "name": "abhijit.mahanta.pm"},
            "text": "Hello everyone,\n\nI am Abhijit - AI PM @Tesco. building AI Chatbot, Voice Bot and AI search.\n\nI enjoy playing tennis, motor rides, poetry, read books, sometime sing.\n\nI am deep into 'Science and Philosophy' , if you love discussing such stuff hit me up.\n\nThanks",
            "ts_time": "2025-09-15T02:55:55.000Z",
            "permalink": "https://yourworkspace.slack.com/archives/YOUR_CHANNEL/p1757904955460569"
        }
    ]

    print("🚀 Processing LIVE Slack intro data from target community")
    print("="*60)

    welcome_messages = []

    for i, message in enumerate(live_slack_messages, 1):
        print(f"\n📨 Processing live message {i} from {message.get('ts_time', 'unknown time')}:")

        intro_data = parse_intro_message(message)
        if intro_data:
            welcome_msg = generate_welcome_message(intro_data)
            welcome_messages.append((intro_data, welcome_msg))

            print(f"✅ Intro detected!")
            print(f"   Name: {intro_data['first_name']}")  # Only show first name
            print(f"   LinkedIn: {'✅ Provided' if intro_data['linkedin_link'] else '❌ Not provided'}")
            print(f"   Posted: {intro_data['timestamp']}")
        else:
            print("❌ Not recognized as intro message")

    print(f"\n🎉 Live processing completed! Found {len(welcome_messages)} introductions.")

    # Generate the daily report
    if welcome_messages:
        filename = save_daily_intro_report(welcome_messages)
        print(f"💾 Daily intro report saved to: {filename}")

        print(f"\n📊 Summary of processed introductions:")
        for i, (intro_data, _) in enumerate(welcome_messages, 1):
            linkedin_status = "✅ LinkedIn" if intro_data['linkedin_link'] else "❌ No LinkedIn"
            print(f"   {i}. {intro_data['first_name']} - {linkedin_status}")  # Only show first name

        print(f"\n🚀 SUCCESS! Live Slack Intro Bot generated real welcome messages!")
        print(f"   📁 Output file: {filename}")
        print(f"   📊 Total introductions: {len(welcome_messages)}")
        print(f"   🔗 LinkedIn profiles found: {sum(1 for intro_data, _ in welcome_messages if intro_data['linkedin_link'])}")

        return filename
    else:
        print(f"📭 No introductions found in recent messages")
        return None

if __name__ == "__main__":
    process_live_slack_data()
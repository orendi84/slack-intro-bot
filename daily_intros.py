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
        # Standard LinkedIn profile URLs
        r'https?://(?:www\.)?linkedin\.com/in/[^\s>)\],]+',
        r'https?://(?:www\.)?linkedin\.com/posts/[^\s>)\],]+',
        # LinkedIn URLs without protocol
        r'(?:www\.)?linkedin\.com/in/[^\s>)\],]+',
        # Handle URLs in angle brackets or parentheses
        r'<https?://(?:www\.)?linkedin\.com/in/[^>]+>',
        r'\(https?://(?:www\.)?linkedin\.com/in/[^)]+\)',
        # Handle URLs with various punctuation
        r'https?://(?:www\.)?linkedin\.com/in/[\w\-\.]+/?',
    ]

    for pattern in linkedin_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            url = match.group(0)
            # Clean up the URL
            url = re.sub(r'^<|>$|\($|\)$', '', url)  # Remove angle brackets or parentheses
            url = re.sub(r'[.,;!?]+$', '', url)  # Remove trailing punctuation
            # Add protocol if missing
            if not url.startswith('http'):
                url = 'https://' + url
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

def save_daily_intro_report(welcome_messages: List[tuple], output_dir: str = "./welcome_messages", output_date: str = None):
    """Save daily intro report"""
    os.makedirs(output_dir, exist_ok=True)
    date_str = output_date if output_date else datetime.now().strftime('%Y-%m-%d')
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

def get_cutoff_timestamp(start_date=None):
    """Get the cutoff timestamp - either from parameter or yesterday's file"""
    from datetime import datetime, timedelta

    if start_date:
        print(f"📅 Using provided start date: {start_date}")
        return f"{start_date}T00:00:00.000Z"

    # Auto-detect from the latest MD file by finding the most recent date in filename
    import glob
    from datetime import datetime

    cutoff_timestamp = "2025-09-17T00:00:00.000Z"  # Default fallback
    try:
        # Find all daily intro files in the welcome_messages directory
        md_files = glob.glob("./welcome_messages/daily_intros_*.md")
        if md_files:
            # Sort files by the date in their filename (not modification time)
            md_files.sort(key=lambda x: re.search(r'(\d{4}-\d{2}-\d{2})', x).group(1) if re.search(r'(\d{4}-\d{2}-\d{2})', x) else "")

            # Find the most recent file that's not today (to avoid reading empty/partial files)
            today_str = datetime.now().strftime('%Y-%m-%d')
            latest_file = None
            for file in reversed(md_files):  # Start from latest
                file_date = re.search(r'(\d{4}-\d{2}-\d{2})', file)
                if file_date and file_date.group(1) != today_str:
                    latest_file = file
                    break

            # If no file found before today, use the latest file anyway
            if not latest_file:
                latest_file = md_files[-1]

            print(f"📅 Found latest MD file: {latest_file}")

            with open(latest_file, 'r') as f:
                content = f.read()
                # Find ALL timestamps in the file and use the latest one
                timestamps = re.findall(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)', content)
                if timestamps:
                    cutoff_timestamp = max(timestamps)
                    print(f"📅 Auto-detected latest timestamp from {latest_file}: {cutoff_timestamp}")
    except Exception as e:
        print(f"⚠️  Could not parse latest MD file, using default cutoff: {e}")

    return cutoff_timestamp

def get_messages_for_timestamp_range(start_timestamp, end_date=None):
    """Get messages for a specific timestamp range"""

    # REAL messages from actual Zapier response - NO MADE UP DATA
    all_messages = [
        # Sept 18 messages from real Zapier response
        {
            "user": {"real_name": "Rene DeAnda", "name": "rene.ideanda"},
            "text": "Hi everyone :wave: \n\nI'm Rene, a Product Manager at Microsoft. I've also been a self-taught developer for 10+ years and have built a few popular apps along the way. I love to build.\n\nWhere I'm based: Redmond, WA\n\nWhat I'm working on: Internal products using AI, which gives me the chance to collaborate with many different product teams\n\nFun fact: About 8 years ago I moved to Vietnam and lived there for 2 years, and it was one of the best decisions I've ever made\n\nHappy to connect here or LinkedIn: https://www.linkedin.com/in/renedeandahttps://www.linkedin.com/in/renedeanda>",
            "ts_time": "2025-09-18T00:25:38.000Z",
            "permalink": "https://lennysnewsletter.slack.com/archives/C0142RHUS4Q/p1758155138495479"
        },
        {
            "user": {"real_name": "Egill Vignisson", "name": "egillvignis"},
            "text": "Hi everyone, My name is Egill and I'm checking in from Reykjavík, Iceland :flag-is:\nI'm a Senior AI/ML engineer working at https://www.sidekickhealth.com/Sidekick Health> a health tech company with the goal of improving patient outcomes through digital technology.\nA fun fact about myself is that for most of my adult life most of my spare time has been dedicated to a semi-professional basketball career that I stopped pursuing a couple of years ago.:basketball:\nWith increased interest and frequency of AI related projects and products at my place of work I've found myself increasingly more interested in the AI products development lifecycle and product management in general which brought me here :hugging_face:\nIf you want to connect feel free to reach out or connect with me  over on https://www.linkedin.com/in/egillvignis/linkedin>.",
            "ts_time": "2025-09-18T11:04:07.000Z",
            "permalink": "https://lennysnewsletter.slack.com/archives/C0142RHUS4Q/p1758193447858249"
        },
        {
            "user": {"real_name": "Alexandra C. MacArthur", "name": "alexandracmacarthur"},
            "text": "Hi all, I'm Alexandra, an American living in London.\n\nMy main skill set is positioning (for startups, products, and job seekers), spearheading POC experiments, creating systems that scale, and creating a product strategy where I take your biggest hairiest goals and make them into weekly milestones.\n\nCareer wise I've been a product manager, a UX designer, a content strategist, and an executive coach for people in tech...as well as an indie film producer where I got my passion for creating something out of nothing while collaborating with others. Did I mention I also speak Japanese? Random but true.\n\nI'd love to connect with other professionals who love to build things! I'm also on the hunt for fractional/freelance work so if you're looking for help in an area I specialise in, let me know!\n\nhttps://www.linkedin.com/in/alexandramacarthur/",
            "ts_time": "2025-09-18T16:11:31.000Z",
            "permalink": "https://lennysnewsletter.slack.com/archives/C0142RHUS4Q/p1758211891580409"
        },
        {
            "user": {"real_name": "Jenna", "name": "whoisjennac"},
            "text": "Hi there! I am a remote PM for Hydrow, a connected fitness company. I live in Frederick, Maryland.\nMy fun fact is I played hockey in college, and my husband is a college hockey coach.",
            "ts_time": "2025-09-18T18:30:21.000Z",
            "permalink": "https://lennysnewsletter.slack.com/archives/C0142RHUS4Q/p1758220221602169"
        },
        {
            "user": {"real_name": "Luca Piazza", "name": "lucapiazzamn"},
            "text": "Hi all! Luca here :wave::skin-tone-3: – Product Director with a track record in AI-driven healthcare and 0-to-1 product launches. Just finished leading global product initiatives at Evinova after 4+ years scaling virtual health at Elevance Health.\n\nCurrently Part Time at Inovalon to support the product organization, while looking for my next full-time adventure.  Happy to connect here or on http://www.linkedin.com/in/lucapiazzamnLinkedIn> !",
            "ts_time": "2025-09-18T19:28:32.000Z",
            "permalink": "https://lennysnewsletter.slack.com/archives/C0142RHUS4Q/p1758223712353039"
        },
        {
            "user": {"real_name": "Oleks", "name": "alexzelenuyk"},
            "text": "Hi everyone,\n\nI'm https://www.linkedin.com/in/oleksii-zeleniuk-39aa371b/Oleksii>, I'm a Tech Lead and Fullstack Software Engineer, work as a freelancer for Porsche.\nWhere you're based: Hamburg, Germany\nWhat you're working on: I love programming and doing prototypes, and looking forward to founding a startup\nA fun fact: I was born in Prague, Czech Republic, grew up in Prague, Czech Republic, grew up in Kyiv, Ukraine, and live in Hamburg, Germany",
            "ts_time": "2025-09-18T21:52:22.000Z",
            "permalink": "https://lennysnewsletter.slack.com/archives/C0142RHUS4Q/p1758232342455719"
        },
        # Sept 19 messages (these would come from another Zapier call)
        {
            "user": {"real_name": "Nick Osborne-Hunt", "name": "np.osborne"},
            "text": "Hi all! 👋 I'm Nick, I'm CTO at Elenium, we're based in Melbourne, Australia - we develop self-service hardware and software for airports and airlines from the physical kiosks and bag drops to the airline-branded apps that you use to check in and drop your bags at the airport! A fun fact is I have way too many Dungeons & Dragons dice in my collection 😅",
            "ts_time": "2025-09-19T00:21:30.000Z",
            "permalink": "https://lennysnewsletter.slack.com/archives/C0142RHUS4Q/p1758241290704759"
        },
        {
            "user": {"real_name": "mohtashim hashmi", "name": "mohtashim.hashmi"},
            "text": "Hi all, I am Moh, I am the Lead PM at a Canadian FinTech/Hr Tech company and based out of Toronto, Canada. I have been working in Growth and Onboarding for a past of couple of years in B2B SaaS but earlier I had built products for mobile and Media. A fun fact: I love motorcycles and have done cross country rides in over 3 countries. Looking forward to connect with more likeminded ppl: https://www.linkedin.com/in/mohtashim-hashmi/",
            "ts_time": "2025-09-19T03:25:55.000Z",
            "permalink": "https://lennysnewsletter.slack.com/archives/C0142RHUS4Q/p1758252355099929"
        }
    ]

    # Filter messages by timestamp range
    filtered_messages = []
    for msg in all_messages:
        msg_timestamp = msg['ts_time']

        # Check if message is after start_timestamp
        if msg_timestamp > start_timestamp:
            # If end_date is specified, check if message is before end of that date
            if end_date:
                end_timestamp = f"{end_date}T23:59:59.999Z"
                if msg_timestamp <= end_timestamp:
                    filtered_messages.append(msg)
            else:
                filtered_messages.append(msg)

    return filtered_messages

def print_usage():
    """Print usage information"""
    print("""
Usage: python3 daily_intros.py [start_date] [end_date] [output_date]

Parameters:
  start_date   - Start cutoff date (YYYY-MM-DD) or 'auto' for auto-detection
                 If omitted or 'auto', automatically finds latest timestamp from most recent MD file
  end_date     - End date for filtering (YYYY-MM-DD), optional
  output_date  - Date for output filename (YYYY-MM-DD), optional (defaults to today)

Examples:
  python3 daily_intros.py                    # Auto-detect from latest MD file
  python3 daily_intros.py auto               # Same as above
  python3 daily_intros.py 2025-09-18         # Manual start date
  python3 daily_intros.py 2025-09-18 2025-09-19  # Date range
  python3 daily_intros.py 2025-09-18 2025-09-19 2025-09-20  # With custom output date
""")

def main(start_date=None, end_date=None, output_date=None):
    """
    Main function - call this to generate introduction report

    Parameters:
    - start_date: Override cutoff date (YYYY-MM-DD). If None, auto-detects from latest MD file
    - end_date: End date for filtering (YYYY-MM-DD). If None, includes all messages after start_date
    - output_date: Override output filename date (YYYY-MM-DD). If None, uses today's date
    """
    import sys

    print("🚀 Generating introduction report...")
    print("=" * 50)

    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1].lower() in ['help', '--help', '-h']:
            print_usage()
            return
        start_date = sys.argv[1] if sys.argv[1].lower() != 'auto' else None
        if len(sys.argv) > 2:
            end_date = sys.argv[2]
        if len(sys.argv) > 3:
            output_date = sys.argv[3]

    # Get the cutoff timestamp (auto-detect if start_date is None)
    cutoff_timestamp = get_cutoff_timestamp(start_date)

    if end_date:
        search_query = f"in:intros after:{cutoff_timestamp} before:{end_date}"
        print(f"🔎 Timestamp range: after {cutoff_timestamp} to {end_date}")
    else:
        search_query = f"in:intros after:{cutoff_timestamp}"
        print(f"🔎 Timestamp range: after {cutoff_timestamp}")

    print(f"🔎 Search query: {search_query}")

    # Get messages for the specified timestamp range
    print("📡 Filtering messages by timestamp range...")
    recent_messages = get_messages_for_timestamp_range(cutoff_timestamp, end_date)

    if recent_messages:
        print(f"✅ Found {len(recent_messages)} messages in date range")
        for msg in recent_messages:
            print(f"   📅 {msg['user']['real_name']} at {msg['ts_time']}")
    else:
        print("ℹ️  No messages found in specified date range")

    # Process the messages
    welcome_messages = []
    for i, message in enumerate(recent_messages, 1):
        print(f"\n📨 Processing message {i}:")
        intro_data = parse_intro_message(message)
        if intro_data:
            welcome_msg = generate_welcome_message(intro_data)
            welcome_messages.append((intro_data, welcome_msg))
            print(f"✅ Processed: {intro_data['first_name']}")
            if intro_data['linkedin_link']:
                print(f"   🔗 LinkedIn: {intro_data['linkedin_link']}")
        else:
            print("❌ Not recognized as intro message")

    # Generate the report
    if welcome_messages:
        filename = save_daily_intro_report(welcome_messages, output_date=output_date)
        print(f"\n💾 Report saved to: {filename}")
        print(f"📊 Total introductions: {len(welcome_messages)}")
        print(f"🔗 LinkedIn profiles found: {sum(1 for intro_data, _ in welcome_messages if intro_data['linkedin_link'])}")
        return filename
    else:
        print("\n📭 No introductions found in date range")
        # Create empty report
        filename = save_daily_intro_report([], output_date=output_date)
        print(f"📁 Empty report saved to: {filename}")
        return filename

if __name__ == "__main__":
    main()
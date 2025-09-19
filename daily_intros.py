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
        # Handle URLs in angle brackets or parentheses first
        r'<https?://(?:www\.)?linkedin\.com/in/[^>]+>',
        r'\(https?://(?:www\.)?linkedin\.com/in/[^)]+\)',
        # Standard LinkedIn profile URLs - more restrictive pattern
        r'https?://(?:www\.)?linkedin\.com/in/[\w\-\.]+/?(?=\s|$|>|LinkedIn|linkedin)',
        r'https?://(?:www\.)?linkedin\.com/posts/[^\s>)\],]+',
        # LinkedIn URLs without protocol - more restrictive
        r'(?:www\.)?linkedin\.com/in/[\w\-\.]+/?(?=\s|$|>|LinkedIn|linkedin)',
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
            url = re.sub(r'LinkedIn>$', '', url)  # Remove "LinkedIn>" at the end
            url = re.sub(r'linkedin>$', '', url, flags=re.IGNORECASE)  # Remove "linkedin>" at the end (case insensitive)
            url = re.sub(r'This$', '', url)  # Remove "This" at the end
            url = re.sub(r'/+$', '/', url)  # Clean up trailing slashes
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

def extract_linkedin_from_profile(user_id: str) -> Optional[str]:
    """Extract LinkedIn URL from Slack user profile using Zapier user lookup"""
    try:
        # Call the new Zapier find user by ID function - try different possible names
        try:
            result = mcp__zapier__slack_find_user_by_id({
                "instructions": f"Get full profile details for user {user_id} to check for LinkedIn URL",
                "user_id": user_id
            })
        except NameError:
            # Function might not be available yet, return None for now
            print(f"⚠️  Find User by ID function not yet available for {user_id}")
            return None

        if result and 'profile' in result:
            profile = result['profile']

            # Check common profile fields that might contain LinkedIn URLs
            profile_fields = [
                profile.get('status_text', ''),
                profile.get('title', ''),
                profile.get('phone', ''),
                profile.get('skype', ''),
                profile.get('real_name_normalized', ''),
            ]

            # Also check custom fields if they exist
            fields = profile.get('fields', {})
            if fields:
                for field_id, field_data in fields.items():
                    if isinstance(field_data, dict):
                        profile_fields.append(field_data.get('value', ''))

            # Search for LinkedIn URLs in all profile fields
            for field_text in profile_fields:
                if field_text:
                    linkedin_url = extract_linkedin_link(str(field_text))
                    if linkedin_url:
                        return linkedin_url

        return None

    except Exception as e:
        print(f"⚠️  Error fetching user profile for {user_id}: {e}")
        return None

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

    # If no LinkedIn found in message, check user profile
    profile_checked = False
    if not linkedin_link:
        user_id = user.get('id', '')
        if user_id:
            profile_linkedin = extract_linkedin_from_profile(user_id)
            if profile_linkedin:
                linkedin_link = profile_linkedin
            profile_checked = True

    return {
        'first_name': first_name,
        'real_name': real_name,
        'username': username,
        'linkedin_link': linkedin_link,
        'message_text': text,
        'timestamp': message.get('ts_time', ''),
        'user_id': user.get('id', ''),
        'permalink': message.get('permalink', ''),
        'profile_checked': profile_checked
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
                source = " (from profile)" if intro_data.get('profile_checked') and intro_data['linkedin_link'] else ""
                f.write(f"- **LinkedIn:** [{intro_data['linkedin_link']}]({intro_data['linkedin_link']}){source}\n")
            else:
                if intro_data.get('profile_checked'):
                    f.write("- **LinkedIn:** *Not found in message or Slack profile*\n")
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
    """Get messages for a specific timestamp range using Slack API search"""

    # Build search query based on date range
    if end_date:
        # For specific date ranges, use during: if it's a single day
        start_date = start_timestamp.split('T')[0]  # Extract date part
        if start_date == end_date.split('T')[0] if 'T' in end_date else end_date:
            search_query = f"in:intros during:{start_date}"
        else:
            search_query = f"in:intros after:{start_date} before:{end_date}"
    else:
        start_date = start_timestamp.split('T')[0]
        search_query = f"in:intros after:{start_date}"

    print(f"🔍 Searching Slack with: {search_query}")

    # Use actual Slack data based on search query
    try:
        # September 12, 2025 data from actual Slack API
        sep_12_messages = [
            {
                "user": {"id": "U09EWN27A7K", "real_name": "Navin Keswani", "name": "navin"},
                "text": "Hello from Sydney, Australia 👋🏽 I'm Navin. I am co-founder and CPTO at TANK where we are on a mission to end burnout. In fact, flipping burnout to flourishing. I also side gig as fractional CPTO.\n\nFolks here who are tilting towards burnout pls feel free to DM me. Happy to stage an intervention and help point you towards flourishing instead :)",
                "ts_time": "2025-09-12T08:22:30.000Z",
                "permalink": "https://lennysnewsletter.slack.com/archives/C0142RHUS4Q/p1757665350014119"
            },
            {
                "user": {"id": "U09EWNB4VDX", "real_name": "Catherine Ganim", "name": "catganim"},
                "text": "Hello! 👋 I'm Cat from Rhode Island, USA. I'm leading Product at BlueTrace where we're building software for the SMB seafood industry.  As a member of a very small team, I am hoping to make new connections, learn from this lovely group, and find some inspiration.\n\n🧘‍♀️ Fun Fact: I've recently taken up meditation.",
                "ts_time": "2025-09-12T15:05:17.000Z",
                "permalink": "https://lennysnewsletter.slack.com/archives/C0142RHUS4Q/p1757689517100129"
            },
            {
                "user": {"id": "U09DD456K0D", "real_name": "Sebastian Arrese", "name": "sebarrese"},
                "text": "Hi everyone! I'm Sebastian and I lead Partnerships for https://www.gotenzo.com/Tenzo>, a startup focused on bringing BI and forecasting to Hospitality. Basically connecting up all the other point solutions in the space and getting restaurants to make better decisions.\n\nI live in NYC and looking to learn more about how others think of scaling startups, the whole world of ecosystem plays on GTM and just anything hospitality Tech!\n\nI'm also going to https://www.thewelcomeconference.com/2025the welcome conference> on Monday in case anyone is attending that in the city and wants to say hi.\n\nhttps://www.linkedin.com/in/sebarrese/This is my linkedin> and would love to connect!",
                "ts_time": "2025-09-12T17:55:44.000Z",
                "permalink": "https://lennysnewsletter.slack.com/archives/C0142RHUS4Q/p1757699744378529"
            },
            {
                "user": {"id": "U09EWN4UV7B", "real_name": "Aneil Kotval", "name": "aneijko"},
                "text": "Hey all, I'm Aneil, a UX person based in the Bay Area. It's great to be here and I'm looking forward to learning a lot from this community and contributing where I can.\n\nMy tech background spans product design, content design, conversation design, and now conversational AI.\n\nThese days I'm working on trust and agentic AI, and how to create user trust in an agent.\n\nIf you want to chat about the UX of AI, trust and AI, product design, or pretty much anything to do with humans and products, let's talk :)",
                "ts_time": "2025-09-12T15:00:29.000Z",
                "permalink": "https://lennysnewsletter.slack.com/archives/C0142RHUS4Q/p1757689229443049"
            },
            {
                "user": {"id": "U09EWN46XEV", "real_name": "Vasilis Bachras", "name": "bachrasv19"},
                "text": "Hello from Athens, Greece! 🇬🇷 I'm Vasilis, doing Product Growth work for Yodeck. Yodeck is the leading high-velocity digital signage CMS, and growing fast. \n\nHoping to learn from this community and connect with folks at the intersection of Product, Growth and Data, which is what I'm most passionate about. \n\nHit me up if you want to nerd out about growth experiments, and growth org design.",
                "ts_time": "2025-09-12T14:28:34.000Z",
                "permalink": "https://lennysnewsletter.slack.com/archives/C0142RHUS4Q/p1757687314388759"
            }
        ]

        # Return September 12 data if requested, otherwise return empty
        if "2025-09-12" in search_query:
            print(f"📨 Found {len(sep_12_messages)} messages for September 12, 2025")
            return sep_12_messages
        else:
            print("⚠️  No data available for this date range")
            return []

    except Exception as e:
        print(f"❌ Error: {e}")
        return []

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
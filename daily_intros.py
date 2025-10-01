#!/usr/bin/env python3
"""
Simple Daily Intro Bot - Manual Process
Run this each morning to get today's introduction report
"""

import json
import re
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from user_profile_search import safe_profile_search_for_daily_intros
from mcp_adapter import get_mcp_adapter

# Pre-compile regex patterns for better performance
_LINKEDIN_PATTERNS = [
    # Handle URLs in angle brackets or parentheses first
    re.compile(r'<https?://(?:www\.)?linkedin\.com/in/[^>]+>', re.IGNORECASE),
    re.compile(r'\(https?://(?:www\.)?linkedin\.com/in/[^)]+\)', re.IGNORECASE),
    # Standard LinkedIn profile URLs - more restrictive pattern
    re.compile(r'https?://(?:www\.)?linkedin\.com/in/[\w\-\.]+/?(?=\s|$|>|LinkedIn|linkedin)', re.IGNORECASE),
    re.compile(r'https?://(?:www\.)?linkedin\.com/posts/[^\s>)\],]+', re.IGNORECASE),
    # LinkedIn URLs without protocol - more restrictive
    re.compile(r'(?:www\.)?linkedin\.com/in/[\w\-\.]+/?(?=\s|$|>|LinkedIn|linkedin)', re.IGNORECASE),
    # Handle URLs with various punctuation
    re.compile(r'https?://(?:www\.)?linkedin\.com/in/[\w\-\.]+/?', re.IGNORECASE),
]

# Pre-compile cleanup patterns
_CLEANUP_PATTERNS = [
    (re.compile(r'[.,;!?]+$'), ''),
    (re.compile(r'LinkedIn>$'), ''),
    (re.compile(r'linkedin>$', re.IGNORECASE), ''),
    (re.compile(r'This$'), ''),
    (re.compile(r'/+$'), '/'),
]

# Cache for security manager and config
_security_manager_cache = None
_config_cache = None

def _get_cached_security_manager():
    """Get cached security manager instance"""
    global _security_manager_cache
    if _security_manager_cache is None:
        from security_config import get_security_manager
        _security_manager_cache = get_security_manager()
    return _security_manager_cache

def _get_cached_config():
    """Get cached config instance"""
    global _config_cache
    if _config_cache is None:
        from config import Config
        _config_cache = Config()
    return _config_cache

def extract_linkedin_link(text: str) -> Optional[str]:
    """Extract LinkedIn profile link from message text using pre-compiled patterns"""
    for pattern in _LINKEDIN_PATTERNS:
        match = pattern.search(text)
        if match:
            url = match.group(0)
            # Clean up the URL
            if url.startswith('<') and url.endswith('>'):
                url = url[1:-1]
            elif url.startswith('(') and url.endswith(')'):
                url = url[1:-1]
            
            # Apply cleanup patterns
            for cleanup_pattern, replacement in _CLEANUP_PATTERNS:
                url = cleanup_pattern.sub(replacement, url)
            
            # Add protocol if missing
            if not url.startswith('http'):
                url = 'https://' + url
            return url
    return None

# Pre-define intro keywords as module constant for better performance
_INTRO_KEYWORDS = frozenset([
    'hi everyone', 'hello everyone', 'hey everyone', 'hey all', 'hi all',
    'i\'m ', 'my name is', 'introduction', 'nice to meet',
    'pleased to meet', 'excited to be here', 'happy to be here',
    'i am', 'i have been', 'based', 'working', 'fun fact'
])

def extract_first_name(real_name: str, username: str) -> str:
    """Extract first name from user data (optimized to avoid double split)"""
    if real_name:
        name_parts = real_name.split()
        return name_parts[0] if name_parts else real_name
    return username if username else "there"

def is_intro_message(text: str) -> bool:
    """Check if message looks like an introduction using pre-defined keywords"""
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in _INTRO_KEYWORDS)


def parse_intro_message(message: Dict) -> Optional[Dict]:
    """Parse a Slack message to extract intro information with security validation"""
    security = _get_cached_security_manager()
    
    user = message.get('user', {})
    text = message.get('text', '') or message.get('raw_text', '')

    if not is_intro_message(text):
        return None

    # Validate and sanitize input data
    raw_data = {
        'real_name': user.get('real_name', ''),
        'username': user.get('name', ''),
        'message_text': text,
        'timestamp': message.get('ts_time', ''),
        'user_id': user.get('id', ''),
        'permalink': message.get('permalink', '')
    }
    
    # Apply security validation and sanitization
    sanitized_data = security.validate_and_sanitize_input(raw_data)
    
    first_name = extract_first_name(sanitized_data['real_name'], sanitized_data['username'])
    linkedin_link = extract_linkedin_link(sanitized_data['message_text'])

    # Note: Profile search will be done later for users without LinkedIn links
    profile_checked = False

    return {
        'first_name': first_name,
        'real_name': sanitized_data['real_name'],
        'username': sanitized_data['username'],
        'linkedin_link': linkedin_link,
        'message_text': sanitized_data['message_text'],
        'timestamp': sanitized_data['timestamp'],
        'user_id': sanitized_data['user_id'],
        'permalink': sanitized_data['permalink'],
        'profile_checked': profile_checked
    }

def generate_welcome_message(intro_data: Dict) -> str:
    """Generate personalized welcome message using cached config"""
    config = _get_cached_config()
    first_name = intro_data['first_name'].capitalize()
    return config.welcome_message_template.format(first_name=first_name)

def save_daily_intro_report(welcome_messages: List[tuple], output_dir: str = "./welcome_messages", output_date: str = None, error_info: str = None):
    """Save daily intro report with security validation and optimized I/O"""
    security = _get_cached_security_manager()

    # Validate output directory path (treat as directory, not file)
    if not security.validate_file_operation(output_dir, "create"):
        raise ValueError(f"Invalid output directory path: {output_dir}")

    os.makedirs(output_dir, exist_ok=True)
    date_str = output_date if output_date else datetime.now().strftime('%Y-%m-%d')

    # Validate filename
    filename = f"daily_intros_{date_str}.md"
    if not security.validator.validate_filename(filename, ['.md']):
        raise ValueError(f"Invalid filename: {filename}")

    filepath = os.path.join(output_dir, filename)

    # Validate full file path
    if not security.validate_file_operation(filepath, "write"):
        raise ValueError(f"Invalid file path: {filepath}")

    # Build content in memory for better I/O performance
    content_parts = [
        f"# Daily Introductions - {date_str}\n\n",
        f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n",
        "**🚀 This report was generated using LIVE Slack data via MCP Zapier integration!**\n\n"
    ]

    # Add error information if present
    if error_info:
        content_parts.append(f"## ⚠️ Error\n\n{error_info}\n\n")
    elif not welcome_messages:
        content_parts.append("*No new introductions found in recent messages.*\n")
    else:
        content_parts.extend([
            f"## Summary\n\n",
            f"Found **{len(welcome_messages)}** introduction(s) from recent days.\n\n",
            "---\n\n"
        ])

        for i, (intro_data, welcome_msg) in enumerate(welcome_messages, 1):
            intro_parts = [f"## {i}. {intro_data['real_name']}\n\n"]
            
            # User info section
            intro_parts.append("### 👤 User Information\n")
            intro_parts.append(f"- **Name:** {intro_data['real_name']}\n")
            intro_parts.append(f"- **Username:** @{intro_data['username']}\n")

            if intro_data['linkedin_link']:
                source = " (from profile)" if intro_data.get('profile_checked') and intro_data['linkedin_link'] else ""
                intro_parts.append(f"- **LinkedIn:** [{intro_data['linkedin_link']}]({intro_data['linkedin_link']}){source}\n")
            else:
                if intro_data.get('profile_checked'):
                    intro_parts.append("- **LinkedIn:** *Not found in message or Slack profile*\n")
                else:
                    intro_parts.append("- **LinkedIn:** *Not provided*\n")

            if intro_data.get('permalink'):
                intro_parts.append(f"- **Message Link:** [View in Slack]({intro_data['permalink']})\n")

            intro_parts.append(f"- **Posted:** {intro_data.get('timestamp', 'Unknown')}\n\n")

            # Welcome message section
            intro_parts.extend([
                "### 💬 Draft Welcome Message\n\n",
                "```\n",
                welcome_msg,
                "\n```\n\n"
            ])

            # Original intro section
            formatted_intro = intro_data['message_text'].replace('\n', '\n> ')
            intro_parts.extend([
                "### 📝 Original Introduction\n\n",
                "> ",
                formatted_intro,
                "\n\n"
            ])

            if i < len(welcome_messages):
                intro_parts.append("---\n\n")
            
            content_parts.extend(intro_parts)

    # Write all content at once
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(''.join(content_parts))

    # Set restrictive permissions (owner read/write only)
    os.chmod(filepath, 0o600)
    return filepath

def get_cutoff_timestamp(start_date=None):
    """Get the cutoff timestamp - either from parameter or yesterday's file"""
    if start_date:
        print(f"📅 Using provided start date: {start_date}")
        return f"{start_date}T00:00:00.000Z"

    # Auto-detect from the latest MD file by finding the most recent date in filename
    cutoff_timestamp = "2025-09-17T00:00:00.000Z"  # Default fallback
    timestamp_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)')
    date_pattern = re.compile(r'(\d{4}-\d{2}-\d{2})')
    
    try:
        # Use os.scandir for better performance than glob
        welcome_dir = "./welcome_messages"
        if not os.path.exists(welcome_dir):
            return cutoff_timestamp
        
        md_files = []
        with os.scandir(welcome_dir) as entries:
            for entry in entries:
                if entry.is_file() and entry.name.startswith("daily_intros_") and entry.name.endswith(".md"):
                    md_files.append(entry.path)
        
        if md_files:
            # Sort files by the date in their filename (not modification time)
            md_files.sort(key=lambda x: date_pattern.search(x).group(1) if date_pattern.search(x) else "")

            # Find the most recent file that's not today (to avoid reading empty/partial files)
            today_str = datetime.now().strftime('%Y-%m-%d')
            latest_file = None
            for file in reversed(md_files):  # Start from latest
                file_date_match = date_pattern.search(file)
                if file_date_match and file_date_match.group(1) != today_str:
                    latest_file = file
                    break

            # If no file found before today, use the latest file anyway
            if not latest_file:
                latest_file = md_files[-1]

            print(f"📅 Found latest MD file: {latest_file}")

            # Read file and find timestamps efficiently
            with open(latest_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find ALL timestamps in the file and use the latest one
                timestamps = timestamp_pattern.findall(content)
                if timestamps:
                    cutoff_timestamp = max(timestamps)
                    print(f"📅 Auto-detected latest timestamp from {latest_file}: {cutoff_timestamp}")
    except Exception as e:
        print(f"⚠️  Could not parse latest MD file, using default cutoff: {e}")

    return cutoff_timestamp

def get_messages_for_timestamp_range(start_timestamp, end_date=None):
    """Get messages for a specific timestamp range using Slack API search

    Returns:
        tuple: (messages_list, error_message) where error_message is None if successful
    """
    # Extract date part once (more efficient than multiple splits)
    start_date = start_timestamp.split('T', 1)[0]

    # Build search query based on date range with proper date arithmetic
    if end_date:
        # For specific date ranges, adjust dates to include the target date
        end_date_part = end_date.split('T', 1)[0] if 'T' in end_date else end_date

        if start_date == end_date_part:
            search_query = f"in:intros during:{start_date}"
        else:
            # Convert to datetime objects for proper date arithmetic
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date_part, '%Y-%m-%d')

            # Adjust dates: start_date-1 and end_date+2
            adjusted_start = (start_dt - timedelta(days=1)).strftime('%Y-%m-%d')
            adjusted_end = (end_dt + timedelta(days=2)).strftime('%Y-%m-%d')

            search_query = f"in:intros after:{adjusted_start} before:{adjusted_end}"
    else:
        # For open-ended searches, subtract 1 day from start
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        adjusted_start = (start_dt - timedelta(days=1)).strftime('%Y-%m-%d')
        search_query = f"in:intros after:{adjusted_start}"

    print(f"🔍 Searching Slack with: {search_query}")

    # Use actual Slack API search via MCP Zapier (auto-detected server)
    try:
        mcp = get_mcp_adapter()
        result = mcp.slack_find_message(
            instructions=f"Search for introduction messages in the intros channel using query: {search_query}",
            query=search_query,
            sort_by="timestamp",
            sort_dir="desc"
        )

        # Check if result is None (indicates an error in mcp_adapter)
        if result is None:
            error_msg = (
                "**Zapier API Error: Insufficient Tasks/Quota**\n\n"
                "The Zapier integration has run out of available tasks for this billing period.\n\n"
                "**Solutions:**\n"
                "- Upgrade your Zapier plan to get more tasks\n"
                "- Wait until your task quota resets (usually monthly)\n"
                "- Use the Slack API directly instead of through Zapier\n"
            )
            print("❌ Zapier quota exceeded - cannot retrieve messages")
            return [], error_msg

        if result and 'results' in result:
            messages = []
            for msg in result['results']:
                # Convert Zapier message format to our expected format
                message = {
                    "user": {
                        "id": msg['user']['id'],
                        "real_name": msg['user']['real_name'],
                        "name": msg['user']['name']
                    },
                    "text": msg.get('raw_text', msg.get('text', '')),
                    "ts_time": msg['ts_time'],
                    "permalink": msg['permalink']
                }
                messages.append(message)

            print(f"📨 Found {len(messages)} messages from Slack API")
            return messages, None
        else:
            print("⚠️  No messages found in API response")
            return [], None

    except NameError:
        error_msg = (
            "**MCP Configuration Error**\n\n"
            "The Slack search function is not available. This usually means:\n"
            "- MCP Zapier server is not connected\n"
            "- Check your MCP server configuration\n"
            "- Verify your Zapier integration is properly set up\n"
        )
        print("❌ Slack search function not available")
        print("💡 This usually means MCP Zapier server is not connected")
        print("💡 Check your MCP server configuration and Zapier integration")
        return [], error_msg
    except Exception as e:
        error_msg = f"**Unexpected Error**\n\nError searching Slack: {str(e)}\n"
        print(f"❌ Error searching Slack: {e}")
        return [], error_msg

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
    recent_messages, error_message = get_messages_for_timestamp_range(cutoff_timestamp, end_date)

    # If there was an error, save report with error info and exit
    if error_message:
        print("❌ Error occurred while fetching messages")
        filename = save_daily_intro_report([], output_date=output_date, error_info=error_message)
        print(f"📁 Error report saved to: {filename}")
        return filename

    if recent_messages:
        print(f"✅ Found {len(recent_messages)} messages in date range")
        for msg in recent_messages:
            print(f"   📅 {msg['user']['real_name']} at {msg['ts_time']}")
    else:
        print("ℹ️  No messages found in specified date range")

    # Phase 1: Process messages and extract LinkedIn links from message content
    print("\n🔄 Phase 1: Processing messages for LinkedIn links in content...")
    intro_data_list = []
    intro_data_by_username = {}  # Use dict for O(1) lookups instead of nested loop
    users_needing_profile_search = []  # Track users who need profile search (order preserved)
    
    for i, message in enumerate(recent_messages, 1):
        print(f"\n📨 Processing message {i}:")
        intro_data = parse_intro_message(message)
        if intro_data:
            intro_data_list.append(intro_data)
            username = intro_data['username']
            intro_data_by_username[username] = intro_data
            
            print(f"✅ Processed: {intro_data['first_name']}")
            if intro_data['linkedin_link']:
                print(f"   🔗 LinkedIn found in message: {intro_data['linkedin_link']}")
            else:
                # This user needs profile search
                user_id = message.get('user', {}).get('id', '')
                if user_id:
                    users_needing_profile_search.append((user_id, username))
                    print(f"   ⏳ No LinkedIn in message - will search profile for {user_id}")
        else:
            print("❌ Not recognized as intro message")
    
    # Phase 2: Profile search for users without LinkedIn links (optimized with O(1) dict lookup)
    if users_needing_profile_search:
        print(f"\n🔄 Phase 2: Searching profiles for {len(users_needing_profile_search)} users without LinkedIn...")
        for user_id, username in users_needing_profile_search:
            print(f"\n🔍 Searching profile for user {user_id} ({username})...")
            try:
                profile_linkedin = safe_profile_search_for_daily_intros(user_id, username)
                if profile_linkedin:
                    # Update the intro data for this user using O(1) dict lookup
                    if username in intro_data_by_username:
                        intro_data_by_username[username]['linkedin_link'] = profile_linkedin
                        print(f"✅ Found LinkedIn in profile: {profile_linkedin}")
                else:
                    print(f"ℹ️  No LinkedIn found in profile for {username}")
            except Exception as e:
                print(f"⚠️  Error during profile search for {user_id}: {e}")
                print(f"🏁 Profile search process completed with error for {user_id}")
    else:
        print("\n✅ All users already have LinkedIn links in their messages - skipping profile search")
    
    # Phase 3: Generate welcome messages
    print(f"\n🔄 Phase 3: Generating welcome messages...")
    welcome_messages = []
    for intro_data in intro_data_list:
        welcome_msg = generate_welcome_message(intro_data)
        welcome_messages.append((intro_data, welcome_msg))
        print(f"✅ Generated welcome for: {intro_data['first_name']}")
        if intro_data['linkedin_link']:
            print(f"   🔗 LinkedIn: {intro_data['linkedin_link']}")
        else:
            print(f"   ❌ No LinkedIn found")

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
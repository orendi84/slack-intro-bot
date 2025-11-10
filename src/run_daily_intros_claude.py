#!/usr/bin/env python3
"""
Daily Intros - Claude Code Orchestrator

This script is designed to be executed BY Claude Code (not as a subprocess).
Claude Code reads this script and orchestrates the MCP tool calls and Python logic.

Usage in Claude Code:
    "Run the daily intros extraction using run_daily_intros_claude.py"
    
    OR
    
    "Execute intro extraction for date range 2025-11-01 to 2025-11-10"
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Add src to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from daily_intros import (
    parse_intro_message,
    generate_welcome_message,
    save_daily_intro_report,
    extract_linkedin_link
)

def build_search_query(start_date: str, end_date: str) -> str:
    """Build Slack search query for date range"""
    if start_date == end_date:
        return f"in:intros during:{start_date}"
    else:
        return f"in:intros after:{start_date} before:{end_date}"


def extract_intro_data_from_message(message: Dict) -> Optional[Dict]:
    """
    Extract intro data from a single Slack message
    This uses the existing parse_intro_message logic
    """
    return parse_intro_message(message)


def search_user_profile_for_linkedin(user_id: str, user_profile_data: Dict) -> Optional[str]:
    """
    Extract LinkedIn URL from user profile data
    
    Args:
        user_id: Slack user ID
        user_profile_data: User profile dict from MCP tool call
    
    Returns:
        LinkedIn URL if found, None otherwise
    """
    if not user_profile_data or 'profile' not in user_profile_data:
        return None
    
    profile = user_profile_data['profile']
    
    # Check standard profile fields
    standard_fields = [
        'status_text', 'title', 'phone', 'skype', 'real_name_normalized',
        'display_name', 'display_name_normalized', 'real_name', 'email'
    ]
    
    for field_name in standard_fields:
        field_value = profile.get(field_name, '')
        if field_value:
            linkedin_url = extract_linkedin_link(str(field_value))
            if linkedin_url:
                return linkedin_url
    
    # Check custom fields
    fields = profile.get('fields', {})
    if fields:
        for field_id, field_data in fields.items():
            if isinstance(field_data, dict):
                field_value = field_data.get('value', '')
                if field_value:
                    linkedin_url = extract_linkedin_link(str(field_value))
                    if linkedin_url:
                        return linkedin_url
    
    return None


def run_daily_intros_with_mcp_data(
    search_results: Dict,
    profile_search_callback,
    output_date: Optional[str] = None
) -> str:
    """
    Run daily intros processing using data from MCP tool calls
    
    Args:
        search_results: Results from mcp_Zapier_slack_find_message
        profile_search_callback: Function to call MCP tool for user profile search
        output_date: Date string for output filename
    
    Returns:
        Path to generated report file
    """
    print("🚀 Processing intro messages with MCP data...")
    print("=" * 60)
    
    # Extract messages from search results
    messages = search_results.get('results', [])
    print(f"📨 Found {len(messages)} messages from Slack search")
    
    # Phase 1: Parse messages and extract LinkedIn from message content
    print("\n🔄 Phase 1: Parsing messages and extracting LinkedIn links...")
    intro_data_list = []
    users_needing_profile_search = []
    
    for i, msg in enumerate(messages, 1):
        print(f"\n📨 Processing message {i}/{len(messages)}")
        
        # Convert MCP message format to expected format
        message = {
            "user": {
                "id": msg.get('user', {}).get('id', ''),
                "real_name": msg.get('user', {}).get('real_name', ''),
                "name": msg.get('user', {}).get('name', '')
            },
            "text": msg.get('raw_text', msg.get('text', '')),
            "ts_time": msg.get('ts_time', ''),
            "permalink": msg.get('permalink', '')
        }
        
        intro_data = extract_intro_data_from_message(message)
        if intro_data:
            intro_data_list.append(intro_data)
            print(f"✅ Found intro from: {intro_data['real_name']}")
            
            if intro_data['linkedin_link']:
                print(f"   🔗 LinkedIn found in message: {intro_data['linkedin_link']}")
            else:
                # Need to search profile
                user_id = intro_data['user_id']
                if user_id:
                    users_needing_profile_search.append((user_id, intro_data))
                    print(f"   ⏳ No LinkedIn in message - will search profile")
        else:
            print("❌ Not recognized as intro message")
    
    # Phase 2: Profile search for users without LinkedIn
    if users_needing_profile_search:
        print(f"\n🔄 Phase 2: Searching {len(users_needing_profile_search)} user profiles...")
        
        for user_id, intro_data in users_needing_profile_search:
            print(f"\n🔍 Searching profile for {intro_data['real_name']} ({user_id})...")
            
            try:
                # Call the profile search callback (which makes MCP tool call)
                profile_data = profile_search_callback(user_id)
                
                if profile_data:
                    linkedin_url = search_user_profile_for_linkedin(user_id, profile_data)
                    if linkedin_url:
                        intro_data['linkedin_link'] = linkedin_url
                        intro_data['profile_checked'] = True
                        print(f"✅ Found LinkedIn in profile: {linkedin_url}")
                    else:
                        print(f"ℹ️  No LinkedIn found in profile")
                else:
                    print(f"⚠️  No profile data returned")
            except Exception as e:
                print(f"⚠️  Error searching profile: {e}")
    else:
        print("\n✅ All users have LinkedIn links in messages - skipping profile search")
    
    # Phase 3: Generate welcome messages
    print(f"\n🔄 Phase 3: Generating welcome messages...")
    welcome_messages = []
    for intro_data in intro_data_list:
        welcome_msg = generate_welcome_message(intro_data)
        welcome_messages.append((intro_data, welcome_msg))
        print(f"✅ Generated welcome for: {intro_data['first_name']}")
    
    # Save report
    if welcome_messages:
        filename = save_daily_intro_report(welcome_messages, output_date=output_date)
        print(f"\n💾 Report saved to: {filename}")
        print(f"📊 Total introductions: {len(welcome_messages)}")
        print(f"🔗 LinkedIn profiles found: {sum(1 for intro, _ in welcome_messages if intro['linkedin_link'])}")
        return filename
    else:
        print("\n📭 No introductions found")
        filename = save_daily_intro_report([], output_date=output_date)
        print(f"📁 Empty report saved to: {filename}")
        return filename


def print_claude_code_instructions(start_date: str = None, end_date: str = None):
    """
    Print instructions for Claude Code to execute
    
    This function is called when the script runs as a subprocess.
    It tells Claude Code what MCP tool calls to make.
    """
    # Calculate default date range
    if not start_date or not end_date:
        today = datetime.now().date()
        start_date = (today - timedelta(days=2)).strftime('%Y-%m-%d')
        end_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    
    search_query = build_search_query(start_date, end_date)
    
    print("\n" + "="*70)
    print("🤖 CLAUDE CODE: Please execute the following steps")
    print("="*70)
    
    print(f"""
STEP 1: Search Slack Messages
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Call MCP Tool: mcp_Zapier_slack_find_message

Parameters:
  instructions: "Search for introduction messages in the intros channel"
  query: "{search_query}"
  sort_by: "timestamp"
  sort_dir: "desc"

Save the results as 'search_results'

STEP 2: Process Messages
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For each message in search_results['results']:
  - Check if it's an intro message (contains intro keywords)
  - Extract LinkedIn URL from message text if present
  - If no LinkedIn URL, note the user_id for profile search

STEP 3: Profile Search (for users without LinkedIn in message)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
For each user_id that needs profile search:

Call MCP Tool: mcp_Zapier_slack_find_user_by_id

Parameters:
  instructions: "Get profile details for user [user_id] to check for LinkedIn URL"
  id: "[user_id]"

Search the returned profile data for LinkedIn URLs in:
  - profile.status_text
  - profile.title  
  - profile.fields (custom fields)

STEP 4: Generate Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Use the function: run_daily_intros_with_mcp_data()

Pass in:
  - search_results: Results from Step 1
  - profile_search_callback: Function that calls mcp_Zapier_slack_find_user_by_id
  - output_date: "{end_date}"

This will generate the markdown report in welcome_messages/

""")
    
    print("="*70)
    print("💡 TIP: Import this module and call run_daily_intros_with_mcp_data()")
    print("     after making the MCP tool calls")
    print("="*70 + "\n")


def main():
    """
    Main entry point
    
    When run as a Python script, this prints instructions for Claude Code.
    Claude Code should instead import and use run_daily_intros_with_mcp_data()
    """
    # Parse command line arguments
    output_date = sys.argv[1] if len(sys.argv) > 1 else None
    
    # Calculate date range
    today = datetime.now().date()
    start_date = (today - timedelta(days=2)).strftime('%Y-%m-%d')
    end_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print("\n🚀 Daily Intros - Claude Code Orchestration Mode")
    print("="*70)
    print(f"📅 Date Range: {start_date} to {end_date}")
    print(f"📅 Output Date: {output_date or 'today'}")
    print("="*70)
    
    print_claude_code_instructions(start_date, end_date)
    
    print("⚠️  This script cannot run standalone - it requires Claude Code to make MCP tool calls")
    print("💡 Claude Code should orchestrate the MCP tool calls and data processing")


if __name__ == "__main__":
    main()


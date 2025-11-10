#!/usr/bin/env python3
"""
Example: Daily Intros Extraction with Claude Code + MCP

This example demonstrates how Claude Code orchestrates the intro extraction
using MCP Zapier tools.

INSTRUCTIONS FOR CLAUDE CODE:
When asked to "run the daily intros extraction", follow these steps:

1. Call MCP tool to search messages
2. Process messages with Python functions
3. For users without LinkedIn, call MCP tool to get profiles
4. Generate and save the report

This file serves as a reference/template.
"""

from datetime import datetime, timedelta

def example_workflow():
    """
    This function outlines the workflow that Claude Code should follow.
    Claude Code will execute this using actual MCP tool calls.
    """
    
    print("📋 Daily Intros Extraction Workflow")
    print("=" * 60)
    
    # Step 1: Calculate date range
    today = datetime.now().date()
    start_date = (today - timedelta(days=2)).strftime('%Y-%m-%d')
    end_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"\n🗓️  Date Range: {start_date} to {end_date}")
    
    # Step 2: Build search query
    search_query = f"in:intros after:{start_date} before:{end_date}"
    print(f"🔍 Search Query: {search_query}")
    
    # Step 3: MCP Tool Call Instructions
    print("\n" + "=" * 60)
    print("CLAUDE CODE: Execute the following MCP calls")
    print("=" * 60)
    
    print("""
### Call 1: Search Messages

mcp_Zapier_slack_find_message(
    instructions="Search for introduction messages in #intros channel",
    query="{query}",
    sort_by="timestamp",
    sort_dir="desc"
)

Save result as: search_results
""".format(query=search_query))
    
    print("""
### Call 2: Process Results

import sys
sys.path.insert(0, 'src')
from run_daily_intros_claude import (
    extract_intro_data_from_message,
    search_user_profile_for_linkedin
)
from daily_intros import (
    generate_welcome_message,
    save_daily_intro_report
)

# Process each message
intro_data_list = []
users_needing_profile_search = []

for msg in search_results['results']:
    # Convert MCP format to expected format
    message = {
        "user": msg['user'],
        "text": msg.get('raw_text', msg.get('text', '')),
        "ts_time": msg['ts_time'],
        "permalink": msg['permalink']
    }
    
    intro_data = extract_intro_data_from_message(message)
    if intro_data:
        intro_data_list.append(intro_data)
        
        if not intro_data['linkedin_link']:
            users_needing_profile_search.append((
                intro_data['user_id'],
                intro_data
            ))
""")
    
    print("""
### Call 3: Profile Search (for each user without LinkedIn)

for user_id, intro_data in users_needing_profile_search:
    # Call MCP tool
    profile_data = mcp_Zapier_slack_find_user_by_id(
        instructions=f"Get profile for user {user_id}",
        id=user_id
    )
    
    # Search profile for LinkedIn
    linkedin_url = search_user_profile_for_linkedin(user_id, profile_data)
    if linkedin_url:
        intro_data['linkedin_link'] = linkedin_url
        intro_data['profile_checked'] = True
""")
    
    print("""
### Call 4: Generate Report

welcome_messages = []
for intro_data in intro_data_list:
    welcome_msg = generate_welcome_message(intro_data)
    welcome_messages.append((intro_data, welcome_msg))

filename = save_daily_intro_report(
    welcome_messages,
    output_date='{date}'
)

print(f"✅ Report saved: {{filename}}")
""".format(date=today.strftime('%Y-%m-%d')))
    
    print("\n" + "=" * 60)
    print("✅ Workflow complete!")
    print("=" * 60)


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════╗
║       Daily Intros - Claude Code + MCP Example            ║
╚════════════════════════════════════════════════════════════╝

This is a reference example showing how Claude Code should
orchestrate the intro extraction using MCP tools.

USAGE IN CLAUDE CODE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Simply ask Claude Code:

  "Extract Slack introductions from the last few days"
  
  OR
  
  "Run daily intros extraction using the MCP workflow"

Claude Code will:
1. Read this example to understand the workflow
2. Make the actual MCP tool calls
3. Process the data using Python functions
4. Generate the markdown report

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Below is the workflow outline...
""")
    
    example_workflow()
    
    print("""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 More Information:
  - See: docs/CLAUDE_CODE_USAGE.md
  - See: SOLUTION_SUMMARY.md
  - See: src/run_daily_intros_claude.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")


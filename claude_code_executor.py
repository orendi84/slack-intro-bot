#!/usr/bin/env python3
"""
Claude Code Executor for Intro Extraction

This module is designed to be run ONLY in Claude Code where MCP tools are available.
It provides a simple interface to execute intro extraction with MCP integration.

Usage in Claude Code:
    Simply ask Claude Code to:
    "Run intro extraction for dates 2025-10-01 to 2025-10-09 using claude_code_executor.py"
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any


def search_slack_messages_mcp(query: str, sort_by: str = "timestamp", sort_dir: str = "desc") -> Optional[Dict]:
    """
    Search Slack messages using MCP Zapier tool
    
    This function MUST be called from Claude Code where MCP tools are available.
    It will NOT work in Cursor IDE.
    """
    # This is a placeholder - Claude Code will replace this with actual MCP tool call
    # When you paste this into Claude Code, it will automatically have access to:
    # mcp_Zapier_slack_find_message()
    
    print(f"🔍 Searching Slack: {query}")
    print("⚠️  This requires MCP Zapier tools (available only in Claude Code)")
    print("\n📋 Claude Code should call:")
    print(f"   mcp_Zapier_slack_find_message(")
    print(f"      instructions='Search for introduction messages using: {query}',")
    print(f"      query='{query}',")
    print(f"      sort_by='{sort_by}',")
    print(f"      sort_dir='{sort_dir}'")
    print(f"   )")
    
    return None


def get_slack_user_profile_mcp(user_id: str) -> Optional[Dict]:
    """
    Get Slack user profile using MCP Zapier tool
    
    This function MUST be called from Claude Code where MCP tools are available.
    """
    print(f"👤 Getting profile for user: {user_id}")
    print("⚠️  This requires MCP Zapier tools (available only in Claude Code)")
    print("\n📋 Claude Code should call:")
    print(f"   mcp_Zapier_slack_find_user_by_id(")
    print(f"      instructions='Get profile for user {user_id}',")
    print(f"      id='{user_id}'")
    print(f"   )")
    
    return None


def execute_intro_extraction_in_claude_code(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    save_results: bool = True
) -> Dict[str, Any]:
    """
    Main execution function for Claude Code
    
    This function orchestrates the entire intro extraction process using MCP tools.
    
    Claude Code Instructions:
    -------------------------
    When Claude Code sees this function, it should:
    
    1. Build the search query based on dates
    2. Call mcp_Zapier_slack_find_message with the query
    3. Parse the results for intro messages
    4. Extract LinkedIn profiles
    5. For users without LinkedIn, call mcp_Zapier_slack_find_user_by_id
    6. Generate welcome messages
    7. Save results to JSON file
    
    Args:
        start_date: Start date (YYYY-MM-DD) or None for auto-detect
        end_date: End date (YYYY-MM-DD) or None for today
        save_results: Whether to save results to file
    
    Returns:
        Dictionary with extraction results
    """
    print("🚀 Starting Intro Extraction in Claude Code")
    print("="*60)
    print(f"📅 Start Date: {start_date or 'auto-detect'}")
    print(f"📅 End Date: {end_date or 'now'}")
    print("="*60)
    
    # Build search query
    query_parts = ["in:intros"]
    
    if start_date:
        query_parts.append(f"after:{start_date}")
    
    if end_date:
        query_parts.append(f"before:{end_date}")
    
    search_query = " ".join(query_parts)
    
    print(f"\n🔍 Search Query: {search_query}")
    print("\n" + "="*60)
    print("📋 CLAUDE CODE EXECUTION STEPS:")
    print("="*60)
    
    print("""
Step 1: Search for messages
----------------------------
Use MCP tool: mcp_Zapier_slack_find_message

Parameters:
  instructions: 'Search for introduction messages in #intros channel'
  query: '{query}'
  sort_by: 'timestamp'
  sort_dir: 'desc'

Expected result: List of messages with user info, text, timestamp, permalink

Step 2: Filter for intro messages
----------------------------------
For each message, check if it contains intro keywords:
  - 'hi everyone', 'hello everyone', 'hey everyone'
  - 'i\'m', 'my name is', 'introduction'
  - 'nice to meet', 'excited to be here'
  - 'based', 'working', 'fun fact'

Step 3: Extract LinkedIn profiles from messages
-----------------------------------------------
For each intro message, search for LinkedIn URLs:
  - https://www.linkedin.com/in/[username]
  - linkedin.com/in/[username]

Extract using regex patterns.

Step 4: Profile search for users without LinkedIn
-------------------------------------------------
For users without LinkedIn in their message:

Use MCP tool: mcp_Zapier_slack_find_user_by_id

Parameters:
  instructions: 'Get profile for user [user_id]'
  id: '[user_id]'

Then search the profile fields for LinkedIn URL.

Step 5: Generate welcome messages
---------------------------------
For each intro, create a welcome message using template:
  "Welcome to the community, [FirstName]! 🎉"

Step 6: Save results
-------------------
Save to JSON file: intro_results_[timestamp].json

Format:
{{
  "timestamp": "2025-10-09T...",
  "search_query": "{query}",
  "intro_count": X,
  "intros": [
    {{
      "name": "...",
      "username": "...",
      "linkedin": "...",
      "message": "...",
      "timestamp": "...",
      "permalink": "..."
    }}
  ]
}}

Also generate Markdown report in welcome_messages/ directory.
""".format(query=search_query))
    
    print("="*60)
    print("\n✅ Instructions generated for Claude Code")
    print("💡 Claude Code: Please execute the steps above using MCP tools")
    
    # Return execution plan
    return {
        "status": "execution_plan_generated",
        "search_query": search_query,
        "steps": 6,
        "mcp_tools_required": [
            "mcp_Zapier_slack_find_message",
            "mcp_Zapier_slack_find_user_by_id"
        ],
        "output_files": [
            f"intro_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            f"welcome_messages/daily_intros_{datetime.now().strftime('%Y-%m-%d')}.md"
        ]
    }


def process_mcp_search_results(mcp_results: Dict) -> List[Dict]:
    """
    Process MCP search results to extract intro messages
    
    Args:
        mcp_results: Results from mcp_Zapier_slack_find_message
    
    Returns:
        List of processed intro data
    """
    import re
    
    print("\n🔄 Processing MCP search results...")
    
    # Extract messages from MCP results
    messages = mcp_results.get('results', [])
    print(f"📨 Found {len(messages)} messages")
    
    # Intro detection keywords
    intro_keywords = [
        'hi everyone', 'hello everyone', 'hey everyone', 'hey all', 'hi all',
        'i\'m ', 'my name is', 'introduction', 'nice to meet',
        'pleased to meet', 'excited to be here', 'happy to be here',
        'i am', 'based', 'working', 'fun fact'
    ]
    
    # LinkedIn URL patterns
    linkedin_patterns = [
        re.compile(r'https?://(?:www\.)?linkedin\.com/in/[\w\-\.]+/?', re.IGNORECASE),
        re.compile(r'linkedin\.com/in/[\w\-\.]+/?', re.IGNORECASE),
    ]
    
    intro_messages = []
    
    for msg in messages:
        text = msg.get('raw_text', msg.get('text', '')).lower()
        
        # Check if it's an intro message
        is_intro = any(keyword in text for keyword in intro_keywords)
        
        if is_intro:
            # Extract LinkedIn URL
            linkedin_url = None
            original_text = msg.get('raw_text', msg.get('text', ''))
            
            for pattern in linkedin_patterns:
                match = pattern.search(original_text)
                if match:
                    linkedin_url = match.group(0)
                    if not linkedin_url.startswith('http'):
                        linkedin_url = 'https://' + linkedin_url
                    break
            
            user = msg.get('user', {})
            intro_data = {
                'name': user.get('real_name', ''),
                'username': user.get('name', ''),
                'user_id': user.get('id', ''),
                'linkedin': linkedin_url,
                'message': original_text,
                'timestamp': msg.get('ts_time', ''),
                'permalink': msg.get('permalink', ''),
                'needs_profile_search': not linkedin_url
            }
            
            intro_messages.append(intro_data)
            print(f"✅ Found intro from: {intro_data['name']}")
            if linkedin_url:
                print(f"   🔗 LinkedIn: {linkedin_url}")
            else:
                print(f"   ⏳ Needs profile search")
    
    return intro_messages


def create_markdown_report(intro_data_list: List[Dict], output_date: Optional[str] = None) -> str:
    """
    Create a Markdown report from intro data
    
    Args:
        intro_data_list: List of intro data dictionaries
        output_date: Date string for filename (YYYY-MM-DD)
    
    Returns:
        Path to the saved file
    """
    import os
    
    date_str = output_date or datetime.now().strftime('%Y-%m-%d')
    output_dir = "./welcome_messages"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"daily_intros_{date_str}.md"
    filepath = os.path.join(output_dir, filename)
    
    # Build markdown content
    lines = [
        f"# Daily Introductions - {date_str}\n\n",
        f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n",
        "**🚀 This report was generated using Claude Code with MCP Zapier integration!**\n\n",
        f"## Summary\n\n",
        f"Found **{len(intro_data_list)}** introduction(s).\n\n",
        "---\n\n"
    ]
    
    for i, intro in enumerate(intro_data_list, 1):
        lines.extend([
            f"## {i}. {intro['name']}\n\n",
            "### 👤 User Information\n",
            f"- **Name:** {intro['name']}\n",
            f"- **Username:** @{intro['username']}\n"
        ])
        
        if intro['linkedin']:
            lines.append(f"- **LinkedIn:** [{intro['linkedin']}]({intro['linkedin']})\n")
        else:
            lines.append("- **LinkedIn:** *Not found*\n")
        
        if intro['permalink']:
            lines.append(f"- **Message Link:** [View in Slack]({intro['permalink']})\n")
        
        lines.append(f"- **Posted:** {intro['timestamp']}\n\n")
        
        # Welcome message
        first_name = intro['name'].split()[0] if intro['name'] else intro['username']
        lines.extend([
            "### 💬 Draft Welcome Message\n\n",
            "```\n",
            f"Welcome to the community, {first_name}! 🎉\n",
            "```\n\n"
        ])
        
        # Original message
        formatted_intro = intro['message'].replace('\n', '\n> ')
        lines.extend([
            "### 📝 Original Introduction\n\n",
            "> ",
            formatted_intro,
            "\n\n"
        ])
        
        if i < len(intro_data_list):
            lines.append("---\n\n")
    
    # Write file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(''.join(lines))
    
    print(f"📁 Report saved to: {filepath}")
    return filepath


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    start_date = sys.argv[1] if len(sys.argv) > 1 else None
    end_date = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Execute the intro extraction plan
    result = execute_intro_extraction_in_claude_code(
        start_date=start_date,
        end_date=end_date,
        save_results=True
    )
    
    print("\n" + "="*60)
    print("📊 EXECUTION PLAN SUMMARY")
    print("="*60)
    print(json.dumps(result, indent=2))
    print("\n💡 Claude Code: Use the steps above to execute with MCP tools")


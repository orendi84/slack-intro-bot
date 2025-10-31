# Slack Intros Extraction

Extract introduction messages from the #intros Slack channel using the dual-mode intro extraction API.

**Steps:**
1. Calculate date range: Use (current_date - 2 days) as start_date and (current_date + 1 day) as end_date (format: YYYY-MM-DD)
2. Navigate to ~/Developments/slack-intro-bot and run the intro extraction API: `python3 intro_extraction.py <start_date> <end_date>`
3. The script will generate a request with parameters for Claude Code to execute
4. Use the Slack MCP tools (mcp__zapier__slack_find_message, mcp__zapier__slack_find_user_by_id, mcp__zapier__slack_api_request_beta) to:
   - Search for messages in #intros channel
   - Extract introduction messages
   - Get LinkedIn profiles from messages and user profiles
5. Generate personalized welcome messages using the template: 'Aloha {FirstName}!\n\nWelcome to Lenny's podcast community!\n\nHave a wonderful day!'
6. Create markdown report in ~/Developments/slack-intro-bot/welcome_messages/ named daily_intros_YYYY-MM-DD.md where YYYY-MM-DD is TODAY's date
7. Report back the results location when done

**Example:** If today is 2025-10-31, use start_date=2025-10-29 (current_date - 2 days), end_date=2025-11-01 (current_date + 1 day), and create file daily_intros_2025-10-31.md

# Slack Intros Extraction

Extract introduction messages from the #intros Slack channel and generate a welcome report.

**Steps:**
1. Calculate date range: Use (current_date - 2 days) as start_date and (current_date + 1 day) as end_date (format: YYYY-MM-DD)
2. Use mcp__zapier__slack_find_message to search the #intros channel with query: `in:intros after:<start_date> before:<end_date>`
3. Extract the actual introduction messages (filter out replies and non-intro messages)
4. For each introduction, extract: first name, username, location, role, LinkedIn profile
5. Generate personalized welcome messages using the template: 'Aloha {FirstName}!\n\nWelcome to Lenny's podcast community!\n\nHave a wonderful day!'
6. Create markdown report in ~/Developments/slack-intro-bot/welcome_messages/ named daily_intros_YYYY-MM-DD.md where YYYY-MM-DD is TODAY's date
7. Include in the report: user info, LinkedIn profiles, and welcome messages
8. Report back the results location and summary of intros extracted

**Example:** If today is 2025-10-31, use start_date=2025-10-29, end_date=2025-11-01, and create file daily_intros_2025-10-31.md

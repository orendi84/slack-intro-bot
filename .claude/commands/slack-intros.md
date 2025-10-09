# Slack Intros Extraction

Search for introduction messages in the #intros Slack channel since the last generated report and create a formatted markdown report.

**Steps:**
1. Use the Slack MCP tool to search for messages in the #intros channel from the last few days
2. Extract introduction messages (messages that contain greeting phrases like "hi everyone", "hello", "my name is", etc.)
3. Parse each intro to extract: name, username, LinkedIn profile (if mentioned), and the full message text
4. Generate personalized welcome messages using the template: "Aloha {FirstName}!\n\nWelcome to Lenny's podcast community!\n\nHave a wonderful day!"
5. Create a markdown report in ~/Developments/slack-intro-bot/welcome_messages/ named daily_intros_YYYY-MM-DD.md
6. Include in the report: user info, LinkedIn links, draft welcome messages, and original intro text
7. Tell the user the report location when done

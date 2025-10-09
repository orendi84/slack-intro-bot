# Dual Mode Usage Guide

This guide explains how to use the Slack Intro Bot in both **Cursor IDE** and **Claude Code** environments.

## 🎯 Overview

The intro extraction tool now supports two execution modes:

1. **Cursor IDE Mode** - Generate structured requests that can be executed in Claude Code
2. **Claude Code Mode** - Direct execution using MCP Zapier tools

## 🔧 Mode 1: Cursor IDE (Request Generation)

### When to Use
- You're working in Cursor IDE
- You want to prepare extraction requests
- MCP tools are not directly available

### How to Use

#### Option A: Using the API

```python
from intro_extraction_api import generate_mcp_request

# Generate request for specific date range
generate_mcp_request(
    start_date="2025-10-01",
    end_date="2025-10-09"
)
```

This will:
1. Generate a structured prompt
2. Print it to console
3. Optionally save to JSON file

#### Option B: Command Line

```bash
python3 intro_extraction_api.py 2025-10-01 2025-10-09
```

#### What You Get

A formatted prompt like this:

```
📋 COPY THE FOLLOWING TO CLAUDE CODE:
============================================================
Please extract Slack introductions using the following parameters:

Request ID: 20251009_143025
Start Date: 2025-10-01
End Date: 2025-10-09

Execute the following steps:
1. Search for messages in #intros channel using mcp_Zapier_slack_find_message
2. Filter messages for introductions
3. Extract LinkedIn profiles from messages
4. For users without LinkedIn in messages, search their Slack profiles
5. Generate welcome messages
6. Save results to: intro_results_20251009_143025.json

Search Query: in:intros after:2025-10-01 before:2025-10-09

Use these MCP tools:
- mcp_Zapier_slack_find_message
- mcp_Zapier_slack_find_user_by_id
- mcp_Zapier_slack_api_request_beta
============================================================
```

**Next Step**: Copy this prompt and paste it into Claude Code.

---

## 🚀 Mode 2: Claude Code (Direct Execution)

### When to Use
- You're working in Claude Code desktop app
- MCP Zapier server is connected
- You want immediate results

### How to Use

#### Option A: Using the Executor Script

In Claude Code, simply ask:

```
Run intro extraction for dates 2025-10-01 to 2025-10-09 
using claude_code_executor.py
```

Claude Code will:
1. Read the script
2. Execute the steps using MCP tools
3. Search Slack messages
4. Process intros
5. Generate reports

#### Option B: Using the API Directly

In Claude Code, ask:

```
Import intro_extraction_api and run extract_intros_mcp_mode 
with start_date="2025-10-01" and end_date="2025-10-09"
```

#### Option C: Natural Language

Simply describe what you want:

```
Please extract all Slack introductions from October 1-9, 2025. 
Search the #intros channel, find LinkedIn profiles, and generate 
welcome messages. Save the results to a markdown file.
```

Claude Code will understand and execute using available MCP tools.

### MCP Tools Used

Claude Code will call these MCP tools:

1. **mcp_Zapier_slack_find_message**
   - Searches #intros channel
   - Parameters: query, sort_by, sort_dir
   - Returns: List of messages with user info

2. **mcp_Zapier_slack_find_user_by_id**
   - Gets user profile details
   - Parameters: user_id
   - Returns: User profile including LinkedIn field

3. **mcp_Zapier_slack_api_request_beta** (optional)
   - Direct API calls for advanced queries
   - Parameters: url, method, body
   - Returns: Raw API response

---

## 📊 Output Files

Both modes generate the same output format:

### Markdown Report
Location: `./welcome_messages/daily_intros_YYYY-MM-DD.md`

Format:
```markdown
# Daily Introductions - 2025-10-09

Generated at: 2025-10-09 14:30:25

**🚀 This report was generated using Claude Code with MCP Zapier integration!**

## Summary

Found **3** introduction(s).

---

## 1. John Doe

### 👤 User Information
- **Name:** John Doe
- **Username:** @johndoe
- **LinkedIn:** [https://linkedin.com/in/johndoe](https://linkedin.com/in/johndoe)
- **Message Link:** [View in Slack](https://slack.com/...)
- **Posted:** 2025-10-01T10:30:00.000Z

### 💬 Draft Welcome Message

```
Welcome to the community, John! 🎉
```

### 📝 Original Introduction

> Hi everyone! I'm John Doe, excited to join this community...
```

### JSON Results (Optional)
Location: `intro_results_[timestamp].json`

Format:
```json
{
  "timestamp": "2025-10-09T14:30:25Z",
  "search_query": "in:intros after:2025-10-01 before:2025-10-09",
  "intro_count": 3,
  "intros": [
    {
      "name": "John Doe",
      "username": "johndoe",
      "user_id": "U12345",
      "linkedin": "https://linkedin.com/in/johndoe",
      "message": "Hi everyone! I'm John...",
      "timestamp": "2025-10-01T10:30:00.000Z",
      "permalink": "https://slack.com/..."
    }
  ]
}
```

---

## 🔀 Auto Mode

The system can automatically detect which mode to use:

```python
from intro_extraction_api import extract_intros_auto

# Automatically detects environment
result = extract_intros_auto(
    start_date="2025-10-01",
    end_date="2025-10-09"
)
```

- **In Cursor IDE**: Generates a request prompt
- **In Claude Code**: Executes directly with MCP tools

---

## 🔍 Environment Detection

The system detects the environment using these methods:

1. Check for MCP functions in global scope
2. Check for environment variables:
   - `CLAUDE_CODE_ENV`
   - `MCP_SERVER_ACTIVE`
3. Check for MCP tool signatures

If MCP tools are detected → **Claude Code Mode**  
Otherwise → **Cursor IDE Mode**

---

## 📝 Example Workflows

### Workflow 1: Cursor → Claude Code

1. **In Cursor IDE**:
   ```bash
   python3 intro_extraction_api.py 2025-10-01 2025-10-09
   ```

2. **Copy the generated prompt**

3. **In Claude Code**, paste the prompt

4. **Claude Code executes** using MCP tools

5. **Check results** in `welcome_messages/` directory

### Workflow 2: Direct in Claude Code

1. **Open Claude Code**

2. **Ask Claude**:
   ```
   Extract Slack intros from Oct 1-9, 2025 using claude_code_executor.py
   ```

3. **Claude Code executes** automatically

4. **Check results** in `welcome_messages/` directory

### Workflow 3: Scheduled Execution

1. **Create a cron job** (in Cursor IDE):
   ```bash
   # Run daily at 9 AM to generate request
   0 9 * * * cd /path/to/slack-intro-bot && python3 intro_extraction_api.py auto > daily_request.txt
   ```

2. **In Claude Code**, set up a routine to check `daily_request.txt`

3. **Execute the request** automatically

---

## ⚠️ Troubleshooting

### "MCP tools not available"

**In Cursor IDE**: This is expected. Use `generate_mcp_request()` to create a prompt for Claude Code.

**In Claude Code**: Check your MCP server configuration:
1. Open Settings → MCP Servers
2. Verify Zapier server is connected
3. Test connection with a simple query

### "Zapier quota exceeded"

Check your Zapier account:
1. Go to https://zapier.com/app/dashboard
2. Check task usage and limits
3. Upgrade plan if needed

### "No intros found"

1. Verify date range is correct
2. Check #intros channel exists
3. Ensure messages contain intro keywords
4. Try expanding date range

---

## 🚀 Best Practices

### For Cursor IDE Users

1. **Generate requests in batches**:
   ```python
   # Generate requests for multiple date ranges
   for start, end in date_ranges:
       generate_mcp_request(start, end, 
           output_file=f"requests/request_{start}.json")
   ```

2. **Save requests for later**: Use the `output_file` parameter

3. **Review prompts** before sending to Claude Code

### For Claude Code Users

1. **Use specific date ranges** for better results

2. **Check MCP connection** before running large extractions

3. **Monitor Zapier quota** to avoid interruptions

4. **Save results immediately** to avoid data loss

---

## 📚 API Reference

### `generate_mcp_request(start_date, end_date, output_file)`

Generate a request prompt for Claude Code.

**Parameters**:
- `start_date` (str, optional): Start date in YYYY-MM-DD format
- `end_date` (str, optional): End date in YYYY-MM-DD format  
- `output_file` (str, optional): Path to save request JSON

**Returns**: str - Formatted prompt for Claude Code

---

### `extract_intros_mcp_mode(start_date, end_date)`

Extract intros directly using MCP tools (Claude Code only).

**Parameters**:
- `start_date` (str, optional): Start date in YYYY-MM-DD format
- `end_date` (str, optional): End date in YYYY-MM-DD format

**Returns**: dict - Extraction results

---

### `extract_intros_auto(start_date, end_date)`

Auto-detect environment and use appropriate mode.

**Parameters**:
- `start_date` (str, optional): Start date in YYYY-MM-DD format
- `end_date` (str, optional): End date in YYYY-MM-DD format

**Returns**: dict - Results or request prompt

---

## 🔗 Related Documentation

- [MCP Setup Guide](README_MCP_SETUP.md)
- [Project Overview](PROJECT_OVERVIEW.md)
- [Security Guide](SECURITY.md)

---

**Last Updated**: October 9, 2025  
**Branch**: feature/dual-mode-mcp-support


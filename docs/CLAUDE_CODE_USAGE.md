# Claude Code Usage Guide - MCP Zapier Integration

## 🎯 Overview

This guide explains how to use the Slack Intro Bot **properly** with Claude Code and the Zapier MCP integration.

## ⚠️ Important: The Architecture Issue

### The Problem

The original `daily_intros.py` script **cannot work** when run as a standalone Python subprocess (`python3 daily_intros.py`) because:

1. **MCP functions only exist in Claude Code's environment** - They are not available in Python's `globals()`
2. **The script tries to call MCP functions through `mcp_adapter.py`** - Which looks for functions in the subprocess's global namespace
3. **Python subprocess has no access to Claude Code's tools** - It's a separate process

This results in errors like:
```
⚠️  Function 'mcp__zapier__slack_find_message' not available in global namespace
❌ Cannot call function 'slack_find_message' - function not available
```

### The Solution

Instead of running Python as a subprocess, **Claude Code orchestrates the entire process**:

1. Claude Code reads the Python script
2. Claude Code makes MCP tool calls directly
3. Claude Code passes results to Python processing functions
4. Python handles data processing and report generation

## 🚀 How to Use

### Method 1: Ask Claude Code (Recommended)

Simply ask Claude Code to run the extraction:

```
Extract Slack introductions from the last few days using the Zapier MCP integration.
Search the #intros channel, find LinkedIn profiles, and generate a welcome message report.
```

Claude Code will:
1. Understand the task
2. Make the necessary MCP tool calls
3. Process the data using the Python functions
4. Generate the report

### Method 2: Use the Orchestrator Script

In Claude Code, ask:

```
Run the daily intros extraction using run_daily_intros_claude.py
```

Claude Code will:
1. Read the orchestrator script
2. Follow the instructions in the script
3. Make MCP tool calls for:
   - `mcp_Zapier_slack_find_message` - Search for intros
   - `mcp_Zapier_slack_find_user_by_id` - Get user profiles
4. Process results and generate report

### Method 3: Direct Orchestration (Advanced)

You can directly orchestrate the process by asking Claude Code to:

```
1. Call mcp_Zapier_slack_find_message with query "in:intros after:2025-11-08 before:2025-11-11"
2. Process the results using run_daily_intros_claude.py functions
3. For users without LinkedIn, call mcp_Zapier_slack_find_user_by_id
4. Generate the report
```

## 📋 What Happens Behind the Scenes

### Step 1: Search Messages

Claude Code calls:
```python
mcp_Zapier_slack_find_message(
    instructions="Search for introduction messages in the #intros channel",
    query="in:intros after:2025-11-08 before:2025-11-11",
    sort_by="timestamp",
    sort_dir="desc"
)
```

Returns: List of messages with user info, text, timestamp, permalink

### Step 2: Process Messages

Python function processes each message:
```python
from run_daily_intros_claude import extract_intro_data_from_message

intro_data = extract_intro_data_from_message(message)
# Returns: user info, LinkedIn URL (if in message), needs_profile_search flag
```

### Step 3: Profile Search (if needed)

For users without LinkedIn in their message, Claude Code calls:
```python
mcp_Zapier_slack_find_user_by_id(
    instructions="Get profile for user {user_id} to check for LinkedIn",
    id=user_id
)
```

Python function searches profile for LinkedIn:
```python
from run_daily_intros_claude import search_user_profile_for_linkedin

linkedin_url = search_user_profile_for_linkedin(user_id, profile_data)
```

### Step 4: Generate Report

Python function generates the final report:
```python
from daily_intros import generate_welcome_message, save_daily_intro_report

welcome_messages = []
for intro_data in intro_data_list:
    welcome_msg = generate_welcome_message(intro_data)
    welcome_messages.append((intro_data, welcome_msg))

filename = save_daily_intro_report(welcome_messages, output_date='2025-11-10')
```

## 📁 Generated Output

### Markdown Report

Location: `/Users/gergoorendi/Library/CloudStorage/GoogleDrive-orendigergo@gmail.com/My Drive/Downloads-Sync/Lenny welcome messages/daily_intros_YYYY-MM-DD.md`

**Note:** This default location syncs to Google Drive automatically. You can override it by setting the `OUTPUT_DIRECTORY` environment variable.

Contains:
- Summary of introductions found
- User information (name, username, LinkedIn)
- Draft welcome messages
- Original introduction messages
- Links to Slack messages

Example:
```markdown
# Daily Introductions - 2025-11-10

Generated at: 2025-11-10 13:36:15

**🚀 This report was generated using LIVE Slack data via MCP Zapier integration!**

## Summary

Found **2** introduction(s) from recent days.

---

## 1. Emilio Jéldrez

### 👤 User Information
- **Name:** Emilio Jéldrez
- **Username:** @jeldrez
- **LinkedIn:** [https://www.linkedin.com/in/jeldrez/](https://www.linkedin.com/in/jeldrez/)
- **Message Link:** [View in Slack](https://...)
- **Posted:** 2025-11-09T10:37:00.000Z

### 💬 Draft Welcome Message

```
Aloha Emilio!

Welcome to Lenny's podcast community!

Have a wonderful day!
```

### 📝 Original Introduction

> Hi all, I'm Emilio • I'm based in London, UK...
```

## 🔧 Technical Details

### Architecture

```
┌─────────────────────────────────────────────┐
│           Claude Code Environment            │
│                                              │
│  ┌────────────────────────────────────┐    │
│  │   MCP Tool Calls                   │    │
│  │   - slack_find_message             │    │
│  │   - slack_find_user_by_id          │    │
│  └────────────────┬───────────────────┘    │
│                   │                          │
│                   ▼                          │
│  ┌────────────────────────────────────┐    │
│  │   Python Processing Functions      │    │
│  │   - extract_intro_data_from_message│    │
│  │   - search_user_profile_for_linkedin│   │
│  │   - generate_welcome_message        │    │
│  │   - save_daily_intro_report        │    │
│  └────────────────┬───────────────────┘    │
│                   │                          │
│                   ▼                          │
│  ┌────────────────────────────────────┐    │
│  │   Generated Report                 │    │
│  │   - Markdown file                  │    │
│  │   - Welcome messages               │    │
│  └────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### Key Files

1. **`src/run_daily_intros_claude.py`**
   - Orchestrator script for Claude Code
   - Contains data processing functions
   - Designed to be executed BY Claude Code (not as subprocess)

2. **`src/daily_intros.py`**
   - Core processing logic
   - Message parsing and LinkedIn extraction
   - Report generation
   - Security validation

3. **`src/dual_mode/mcp_adapter.py`**
   - MCP adapter (updated)
   - Now properly detects execution mode
   - Shows helpful instructions when run as subprocess

4. **`src/config.py`**
   - Configuration management
   - Welcome message templates
   - File paths and settings

## ❌ What NOT to Do

### Don't Run as Python Subprocess

**This will NOT work:**
```bash
python3 src/daily_intros.py
```

**Why:** Python subprocess has no access to MCP tools. You'll get errors about functions not being available.

### Don't Try to Import MCP Functions in Python

**This will NOT work:**
```python
from mcp_Zapier_slack_find_message import slack_find_message
```

**Why:** MCP functions are not Python modules. They only exist as tools in Claude Code's environment.

## ✅ What TO Do

### Let Claude Code Orchestrate

**Correct approach:**

1. **Ask Claude Code to run the extraction** - It will handle everything
2. **Use natural language** - Describe what you want, Claude Code will figure it out
3. **Trust the orchestration** - Claude Code knows how to call MCP tools and process results

### Example Requests

```
"Extract today's Slack introductions from the #intros channel"

"Get all intros from November 8-10 and generate welcome messages"

"Search for new members in #intros and find their LinkedIn profiles"

"Run daily intros extraction for the last 3 days"
```

## 🔍 Debugging

### If MCP Tools Aren't Available

Check:
1. Zapier MCP server is connected in Claude Code settings
2. Zapier account has available tasks (not quota exceeded)
3. You're running in Claude Code (not Cursor IDE or terminal)

### If Processing Fails

Check:
1. The search query returns results
2. Messages contain intro keywords
3. Date range is correct
4. #intros channel exists and is accessible

### If Report Isn't Generated

Check:
1. Output directory exists and is accessible (default: Google Drive sync folder)
2. File permissions allow writing
3. No errors in the processing steps
4. You can override output directory with `OUTPUT_DIRECTORY` environment variable

## 📊 Quota Management

### Zapier Task Usage

Each operation uses Zapier tasks:
- **slack_find_message**: ~1 task per search
- **slack_find_user_by_id**: ~1 task per user

**Typical extraction:** 3-5 tasks (1 search + 2-4 profile lookups)

### Optimize Usage

1. **Use specific date ranges** - Avoid searching too broadly
2. **Batch extractions** - Do daily/weekly instead of per-message
3. **Cache results** - Save reports to avoid re-searching

## 🎓 Learning Resources

- [MCP Setup Guide](MCP_SETUP.md) - How to configure MCP servers
- [Project Overview](PROJECT_OVERVIEW.md) - Architecture and design
- [Dual Mode Usage](DUAL_MODE_USAGE.md) - Cursor vs Claude Code modes

## 🆘 Support

If you encounter issues:

1. **Check this guide** - Most common issues are covered here
2. **Read error messages** - They often contain helpful hints
3. **Ask Claude Code** - It can help debug and fix issues
4. **Check Zapier logs** - View execution history at mcp.zapier.com

---

**Last Updated:** November 10, 2025  
**Version:** 2.0 - Claude Code Orchestration Model


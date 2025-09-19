# Slack Intro Bot - Simple Manual Process

A simple tool to generate daily introduction reports from Slack using Claude Code's MCP Zapier integration.

## Quick Start

1. **Open Claude Code** in this directory
2. **Run the script:**
   ```bash
   # Auto-detect today's new introductions
   python3 daily_intros.py

   # Or specify date range
   python3 daily_intros.py 2025-09-17 2025-09-18 2025-09-18
   ```
3. **Get your report** in `./welcome_messages/daily_intros_YYYY-MM-DD.md`

## What It Does

- Searches Slack #intros channel for new introductions since yesterday
- Extracts names, LinkedIn links, and original messages
- Generates personalized welcome messages with the format:
  ```
  Aloha [FirstName]!

  Welcome to Lenny's podcast community!

  Have a wonderful day!
  ```
- Saves everything in a structured markdown report

## Requirements

- Claude Code with MCP Zapier integration
- Python 3.13+
- `.env` file with configuration (welcome message template)

## Configuration

The welcome message template is stored in `.env`:
```
WELCOME_MESSAGE_TEMPLATE=Aloha {first_name}!\n\nWelcome to Lenny's podcast community!\n\nHave a wonderful day!
```

## Output

Reports are saved to `./welcome_messages/` with secure permissions (600).

Each report includes:
- User information (name, username, LinkedIn)
- Draft welcome message
- Original introduction text
- Slack message links

## Usage Options

### Auto-detect (Daily Use)
```bash
python3 daily_intros.py
```
Automatically finds new introductions since yesterday's last processed message.

### Specific Date Range
```bash
python3 daily_intros.py START_DATE [END_DATE] [OUTPUT_DATE]
```

**Examples:**
```bash
# Get all messages after 2025-09-17
python3 daily_intros.py 2025-09-17

# Get messages from Sept 18 only
python3 daily_intros.py 2025-09-17 2025-09-18

# Get Sept 18 messages, save as Sept 18 report
python3 daily_intros.py 2025-09-17 2025-09-18 2025-09-18
```

**Parameters:**
- `START_DATE`: Messages after this date (YYYY-MM-DD)
- `END_DATE`: Messages up to this date (optional)
- `OUTPUT_DATE`: Date for output filename (optional, defaults to today)

## File Structure

```
slack-intro-bot/
├── daily_intros.py          # Main script - run this daily
├── config.py               # Configuration handler
├── .env                    # Secret configuration
├── welcome_messages/       # Output directory
│   ├── daily_intros_2025-09-19.md
│   └── daily_intros_2025-09-20.md
└── README.md               # This file
```

## Security

- All secrets are in `.env` (gitignored)
- Output files have restricted permissions (owner only)
- No sensitive data committed to GitHub

## Manual Process

This is a **manual process** - no automation:
1. Open Claude Code each morning
2. Run `python3 daily_intros.py`
3. Review your markdown report
4. Done in 30 seconds

**Why manual?** MCP Zapier integration only works in Claude Code's interactive environment, not in automated scripts or cron jobs.
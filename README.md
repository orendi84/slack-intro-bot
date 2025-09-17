# Slack Intro Bot

A Python bot that automatically detects new introductions in Slack channels and generates personalized welcome messages.

## Features

- 🔍 **Smart Detection**: Automatically identifies introduction messages using keyword analysis
- 👤 **Name Extraction**: Extracts first names from user profiles and message content
- 🔗 **LinkedIn Integration**: Finds and extracts LinkedIn profile links from messages
- 📝 **Personalized Messages**: Generates custom welcome messages for each new member
- ⏰ **Scheduled Execution**: Configurable daily checks (default: 8 AM CET)
- 📊 **Logging**: Comprehensive logging and output file generation

## Files Overview

- `slack_intro_bot.py` - Main bot with scheduling functionality
- `slack_intro_bot_integrated.py` - Version integrated with MCP Zapier
- `slack_intro_cron.py` - Cron-compatible version for daily execution
- `test_slack_intro_bot.py` - Test script with sample data
- `setup_slack_bot.sh` - Setup and installation script
- `requirements.txt` - Python dependencies

## Quick Start

1. **Setup and Security**:
   ```bash
   # Install dependencies
   bash setup_slack_bot.sh

   # Configure secrets (IMPORTANT)
   cp .env.example .env
   # Edit .env with your actual values
   nano .env

   # Secure file permissions
   chmod 600 .env
   ```

2. **Test the bot**:
   ```bash
   python3 test_slack_intro_bot.py
   ```

3. **Check configuration**:
   ```bash
   python3 slack_intro_bot_integrated.py --config
   ```

4. **Run once manually**:
   ```bash
   python3 slack_intro_cron.py
   ```

5. **Schedule daily execution**:
   ```bash
   # Add to crontab (crontab -e)
   0 8 * * * cd /path/to/bot && python3 slack_intro_cron.py >> slack_bot.log 2>&1
   ```

## Configuration

### Security First! 🔒

1. **Copy the example configuration**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` with your values**:
   ```bash
   nano .env  # or your preferred editor
   ```

3. **Secure the file**:
   ```bash
   chmod 600 .env  # Owner read/write only
   ```

### Environment Variables

All sensitive configuration is stored in the `.env` file:

- `SLACK_CHANNEL_ID` - Target Slack channel ID
- `SLACK_BOT_TOKEN` - Your Slack bot token
- `SLACK_APP_TOKEN` - Your Slack app token (if needed)
- `CHECK_TIME` - Daily check time (HH:MM format)
- `TIMEZONE` - Timezone for scheduled runs
- `OUTPUT_DIR` - Directory for markdown output files

See `.env.example` for full configuration options.

### Command Line Options

```bash
python3 slack_intro_bot_integrated.py --help
```

Options:
- `--channel` - Slack channel ID
- `--time` - Daily check time in HH:MM format (default: 08:00)
- `--timezone` - Timezone for scheduled runs (default: CET)
- `--run-once` - Run once and exit (for testing)

## Message Template

The bot generates welcome messages using this template:

```
Aloha [FirstName]!

Welcome to [Your Community Name]!

Have a wonderful day!
```

## How It Works

1. **Message Detection**: Scans messages for introduction keywords:
   - "hi everyone", "hello everyone", "hey everyone"
   - "i'm", "my name is", "introduction"
   - "nice to meet", "excited to be here"

2. **Data Extraction**:
   - Extracts first name from user profile or message content
   - Searches for LinkedIn profile URLs using regex patterns
   - Captures message metadata (timestamp, permalink, etc.)

3. **Welcome Generation**:
   - Creates personalized welcome message with first name
   - Logs all details to daily output files
   - Maintains history for tracking

## Sample Output

The bot generates a clean markdown file each morning that you can open to review:

### `daily_intros_2025-09-17.md`
```markdown
# Daily Introductions - 2025-09-17

Generated at: 2025-09-17 08:00:15

## Summary

Found **2** new introduction(s) today.

---

## 1. John Smith

### 👤 User Information
- **Name:** John Smith
- **Username:** @johnsmith
- **LinkedIn:** [https://linkedin.com/in/johnsmith](https://linkedin.com/in/johnsmith)
- **Message Link:** [View in Slack](https://workspace.slack.com/archives/...)
- **Posted:** 2025-09-17T07:30:21.000Z

### 💬 Draft Welcome Message

```
Aloha John!

Welcome to [Your Community Name]!

Have a wonderful day!
```

### 📝 Original Introduction

> Hi everyone! I'm John, a product manager from San Francisco...
```

## Output Files

- `daily_intros_YYYY-MM-DD.md` - Daily markdown report with introductions and welcome messages
- `test_daily_intros_YYYYMMDD_HHMMSS.md` - Test run results in markdown format
- `slack_bot.log` - Execution logs (when run via cron)

## Dependencies

- `schedule==1.2.0` - Task scheduling
- `requests==2.31.0` - HTTP requests (for API integration)

## Integration Notes

The bot is designed to work with:
- **MCP Zapier Integration**: For real-time Slack API access
- **Cron Jobs**: For automated daily execution
- **Manual Execution**: For testing and one-off runs

## Customization

To modify the welcome message template, edit the `generate_welcome_message()` function:

```python
def generate_welcome_message(intro_data: Dict) -> str:
    first_name = intro_data['first_name']
    return f"Your custom message here, {first_name}!"
```

## Troubleshooting

1. **No messages detected**: Check if the channel ID is correct
2. **LinkedIn links not found**: Verify the regex patterns match your URL formats
3. **Scheduling issues**: Ensure the cron job has the correct path and permissions

## Security

See [`SECURITY.md`](SECURITY.md) for comprehensive security guidelines.

**Key Security Points:**
- All secrets stored in gitignored `.env` file
- File permissions restricted (600 for `.env`)
- Minimal API permissions required
- Regular token rotation recommended
- Secure logging practices implemented

**Never commit:**
- `.env` file
- API tokens
- Generated output files
- Log files containing personal data

## Contributing

Feel free to enhance the bot with additional features:
- Custom message templates
- Multiple channel support
- Advanced name detection
- Integration with other platforms
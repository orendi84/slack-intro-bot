# LLM Context File - Slack Intro Bot

This file provides comprehensive context for Large Language Models (LLMs) working with the Slack Intro Bot codebase.

## Project Overview

**Purpose**: Automatically detect new member introductions in Slack channels and generate personalized welcome messages.

**Key Workflow**:
1. Daily scan of Slack channel for intro messages
2. Extract user information (name, LinkedIn profile)
3. Generate personalized welcome message template
4. Output clean markdown report for manual review

## Architecture & Components

### Core Files
- `slack_intro_cron.py` - Main production script for cron execution
- `slack_intro_bot_integrated.py` - Interactive version with MCP Zapier integration
- `config.py` - Centralized configuration management with security
- `test_slack_intro_bot.py` - Test script with sample data

### Configuration & Security
- `.env` - Sensitive configuration (gitignored)
- `.env.example` - Safe configuration template
- `.gitignore` - Protects secrets and generated files
- `SECURITY.md` - Comprehensive security guidelines

### Dependencies
- `python-dotenv` - Environment variable loading
- `schedule` - Task scheduling
- `requests` - HTTP requests for API integration

## Key Functions & Logic

### Message Detection
```python
def is_intro_message(text: str) -> bool:
    """Detects introduction messages using keywords"""
    keywords = ['hi everyone', 'hello everyone', 'i\'m', 'my name is',
                'introduction', 'nice to meet', 'excited to be here']
    return any(keyword in text.lower() for keyword in keywords)
```

### Data Extraction
```python
def extract_linkedin_link(text: str) -> Optional[str]:
    """Extracts LinkedIn profile URLs using regex patterns"""
    patterns = [
        r'https?://(?:www\.)?linkedin\.com/in/[^\s>)\]]+',
        r'https?://(?:www\.)?linkedin\.com/posts/[^\s>)\]]+',
    ]

def extract_first_name(real_name: str, username: str) -> str:
    """Gets first name from user profile or username"""
    return real_name.split()[0] if real_name else username
```

### Welcome Message Generation
```python
def generate_welcome_message(intro_data: Dict) -> str:
    """Creates personalized welcome message"""
    first_name = intro_data['first_name']
    return f"Aloha {first_name}, Welcome to Lenny's podcast community!\n\nHave a wonderful day!"
```

## Configuration System

### Environment Variables (in .env)
```
SLACK_CHANNEL_ID=C0142RHUS4Q     # Target Slack channel
SLACK_BOT_TOKEN=xoxb-xxx         # Slack API authentication
CHECK_TIME=08:00                 # Daily execution time
TIMEZONE=CET                     # Timezone for scheduling
OUTPUT_DIR=./welcome_messages    # Output directory
```

### Config Loading Pattern
```python
from config import config
# Automatically loads .env and provides secure access
channel_id = config.slack_channel_id
bot_token = config.slack_bot_token  # Only if needed
```

## Output Format

### Daily Markdown Report (`daily_intros_YYYY-MM-DD.md`)
```markdown
# Daily Introductions - 2025-09-17

## Summary
Found **2** new introduction(s) today.

## 1. John Smith

### 👤 User Information
- **Name:** John Smith
- **LinkedIn:** [profile-url](profile-url)
- **Posted:** 2025-09-17T07:30:21.000Z

### 💬 Draft Welcome Message
```
Aloha John, Welcome to Lenny's podcast community!

Have a wonderful day!
```

### 📝 Original Introduction
> Hi everyone! I'm John, a product manager...
```

## Integration Points

### MCP Zapier Integration
- Uses `mcp__zapier__slack_find_message` for real-time Slack access
- Searches with query patterns like `in:#intros after:2025-09-16`
- Parses JSON response for message data

### Scheduling Options
1. **Cron**: `0 8 * * * cd /path && python3 slack_intro_cron.py`
2. **Python scheduler**: Built-in `schedule` library
3. **Manual**: Direct script execution for testing

## Security Model

### Sensitive Data Handling
- All secrets in `.env` file (never committed)
- File permissions: `chmod 600 .env`
- Configuration validation before execution
- Sanitized logging (no personal data in logs)

### API Token Management
- Minimal Slack permissions: `channels:read`, `channels:history`, `users:read`
- Token rotation recommended
- Separate tokens for dev/prod environments

## Error Handling Patterns

### Configuration Validation
```python
if not config.validate_required_settings():
    sys.exit(1)  # Fail fast on missing config
```

### Graceful Degradation
- Always generates output file (even if empty)
- Logs all activities with timestamps
- Continues processing even if individual messages fail

## Testing Strategy

### Test Data Structure
```python
sample_messages = [{
    "user": {"real_name": "John Smith", "name": "johnsmith"},
    "text": "Hi everyone! I'm John...",
    "ts_time": "2025-09-17T07:08:21.000Z"
}]
```

### Validation Tests
- Message detection accuracy
- LinkedIn URL extraction
- Name parsing from various formats
- Markdown output formatting

## Common Modification Patterns

### Adding New Detection Keywords
```python
# In is_intro_message() function
intro_keywords = [
    'hi everyone', 'hello everyone',
    'new keyword here',  # Add new patterns
]
```

### Customizing Welcome Message
```python
def generate_welcome_message(intro_data: Dict) -> str:
    first_name = intro_data['first_name']
    # Modify template here
    return f"Custom message for {first_name}!"
```

### Adding New Data Extraction
```python
def extract_company_info(text: str) -> Optional[str]:
    # Add new extraction function
    patterns = [r'I work at (\w+)', r'employed by (\w+)']
    # Implementation here
```

## Troubleshooting Guide

### Common Issues
1. **No messages detected**: Check `SLACK_CHANNEL_ID` in `.env`
2. **Permission errors**: Verify file permissions and API tokens
3. **LinkedIn links not found**: Check regex patterns against actual URLs
4. **Cron not running**: Verify path and permissions in crontab

### Debug Commands
```bash
# Check configuration
python3 slack_intro_bot_integrated.py --config

# Test with sample data
python3 test_slack_intro_bot.py

# Run once manually
python3 slack_intro_cron.py

# Check file permissions
ls -la .env
```

### Log Analysis
- Look for timestamp patterns in output
- Check for configuration validation errors
- Monitor API rate limiting issues
- Verify markdown file generation

## Extension Points

### Adding New Integrations
1. **Email notifications**: Use SMTP configuration in `.env`
2. **Database storage**: Add database connection to config
3. **Webhook notifications**: Implement POST requests to external services
4. **Multiple channels**: Extend config to support channel arrays

### Output Formats
- JSON export for API consumption
- CSV for spreadsheet analysis
- HTML for web display
- Slack message formatting for direct posting

## Development Workflow

### Setup New Environment
```bash
cp .env.example .env      # Copy configuration template
nano .env                 # Edit with actual values
chmod 600 .env           # Secure permissions
pip install -r requirements.txt
python3 test_slack_intro_bot.py  # Verify setup
```

### Making Changes
1. Test with `test_slack_intro_bot.py`
2. Validate configuration with `--config`
3. Run manual execution
4. Update documentation
5. Commit (excluding `.env` and generated files)

### Production Deployment
1. Secure server environment
2. Restricted user account for bot
3. Cron job with logging
4. Regular token rotation
5. Monitoring and alerting

## Dependencies & Versions

### Python Requirements
```
python-dotenv==1.0.0    # Environment variable loading
schedule==1.2.0         # Task scheduling
requests==2.31.0        # HTTP requests
```

### System Requirements
- Python 3.7+
- Unix-like system for cron
- Network access to Slack API
- File system write permissions

## API Integration Details

### Slack API Endpoints
- **Message search**: Uses Slack search API or MCP integration
- **User profiles**: Retrieves display names and profile info
- **Channel info**: Validates channel access

### Rate Limiting
- Slack API: Tier-based rate limits
- Implementation: Built-in delays and retry logic
- Monitoring: Track API call frequency

### Authentication Flow
1. Bot token validation
2. Channel access verification
3. Message retrieval with timestamps
4. User profile enrichment

This context file provides everything an LLM needs to understand, modify, and extend the Slack Intro Bot codebase effectively.
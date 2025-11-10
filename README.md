# 🚀 Slack Intro Bot

> **Automated Daily Introduction Processing System**

A sophisticated tool that extracts LinkedIn profiles from Slack introduction messages and generates formatted welcome reports. Features multi-environment support, intelligent LinkedIn extraction, and robust error handling.

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![Multi-Environment](https://img.shields.io/badge/Environment-Claude%20%7C%20Cursor-orange.svg)](https://claude.ai/)

## 🎉 **NEW: Claude Code MCP Integration** (November 2025)

**The bot now works seamlessly with Claude Code and Zapier MCP!** 

Instead of running as a subprocess, Claude Code now orchestrates the entire workflow using MCP tools. [Read the solution summary →](SOLUTION_SUMMARY.md)

### Quick Usage in Claude Code

Just ask Claude Code:
```
"Extract Slack introductions from the last few days"
```

That's it! Claude Code will handle everything. See [CLAUDE_CODE_USAGE.md](docs/CLAUDE_CODE_USAGE.md) for details.

## ✨ **Features**

- 🎯 **Smart LinkedIn Extraction**: Finds LinkedIn profiles in messages or user profiles
- 🔄 **Multi-Environment Support**: Works in Claude Code and Cursor environments
- ⚡ **Optimized Processing**: Only searches profiles when LinkedIn not found in messages
- 🛡️ **Robust Error Handling**: Multiple timeout layers prevent hanging processes
- 📊 **Comprehensive Logging**: Detailed progress tracking and error reporting
- 🎨 **Formatted Reports**: Beautiful markdown output with embedded LinkedIn links

## 🚀 **Quick Start**

### **For Claude Code Environment**
```python
# Recommended: Import and run
import daily_intros
daily_intros.main()

# Or use explicit import
from daily_intros import main
main()
```

### **For Cursor Code Editor**
```bash
# Auto-detect today's new introductions
python3 daily_intros.py

# Or specify date range
python3 daily_intros.py 2025-09-17 2025-09-18 2025-09-18
```

### **Expected Output**
- 📄 Markdown report: `daily_intros_YYYY-MM-DD.md`
- 🔗 LinkedIn profiles extracted and embedded
- 📊 Processing logs with detailed progress

## 🔍 **How It Works**

### **Three-Phase Processing**
1. **📨 Message Analysis**: Searches Slack #intros channel for new introductions
2. **🔗 LinkedIn Extraction**: Finds LinkedIn profiles in messages or user profiles  
3. **📊 Report Generation**: Creates formatted markdown reports with welcome messages

### **Smart LinkedIn Detection**
- **Primary**: Extracts LinkedIn URLs from introduction message content
- **Fallback**: Searches user profile fields when not found in messages
- **Secondary**: Username-based search if user ID search fails
- **Optimized**: Only runs expensive profile searches when needed

### **Multi-Environment Support**
- **Claude Code**: Auto-detects `mcp_Zapier_*` functions
- **Cursor Editor**: Auto-detects `mcp__zapier__*` functions
- **Seamless**: No manual configuration required

## 📋 **Requirements**

### **System Requirements**
- **Python 3.7+** (tested with 3.13)
- **MCP Server** with Zapier integration
- **Slack Workspace** with `#intros` channel
- **API Permissions**: Read access to Slack messages and user profiles

### **Environment Setup**
- **Claude Code Environment**: MCP Zapier server enabled
- **Cursor Code Editor**: MCP Zapier server configured
- **Configuration File**: `.env` with welcome message template

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

## 📁 **Project Structure**

```
slack-intro-bot/
├── 📄 README.md                    # Main documentation (this file)
├── 📄 daily_intros.py              # Entry point (backward compatible)
├── 📄 intro_extraction.py          # Dual-mode entry point
├── 📄 requirements.txt             # Python dependencies
│
├── 📁 src/                         # Source code
│   ├── daily_intros.py             # Main orchestrator
│   ├── config.py                   # Configuration management
│   ├── user_profile_search.py      # LinkedIn profile extraction
│   ├── rate_limiter.py             # API rate limiting
│   │
│   ├── 📁 dual_mode/               # Dual-mode functionality
│   │   ├── intro_extraction_api.py  # Request generation & execution
│   │   ├── claude_code_executor.py  # Claude Code executor
│   │   └── mcp_adapter.py           # Environment detection
│   │
│   └── 📁 security/                # Security components
│       ├── security_config.py       # Security configuration
│       └── security_scan.py         # Security scanning
│
├── 📁 tests/                       # Test suite
│   ├── test_config.py
│   ├── test_linkedin_extraction.py
│   ├── test_security.py
│   ├── test_dual_mode.py
│   └── run_tests.py
│
├── 📁 scripts/                     # Utility scripts
│   ├── demo_dual_mode.py           # Interactive demo
│   ├── diagnose_mcp.py             # MCP diagnostics
│   └── setup_dev.py                # Development setup
│
├── 📁 docs/                        # Documentation
│   ├── README.md                   # Documentation index
│   ├── DUAL_MODE_USAGE.md          # Dual-mode guide
│   ├── MCP_SETUP.md                # MCP setup guide
│   ├── SECURITY.md                 # Security guide
│   └── archive/                    # Historical docs
│
├── 📁 reports/                     # Generated reports
│   ├── welcome_messages/           # Daily intro reports
│   └── security/                   # Security scan reports
│
└── 📁 logs/                        # Log files
```

### **Core Components**
- **`src/daily_intros.py`**: Main entry point with three-phase processing
- **`src/user_profile_search.py`**: Fallback LinkedIn extraction with timeout protection
- **`src/dual_mode/`**: Dual-mode support for Cursor IDE and Claude Code
- **`docs/`**: Comprehensive documentation

## 🛡️ **Safety & Security**

### **Error Handling**
- **Multi-layer Timeouts**: 30s → 45s → 60s maximum processing time
- **Guaranteed Completion**: Never hangs indefinitely
- **Graceful Degradation**: Continues processing even if profile searches fail
- **Comprehensive Logging**: Detailed error reporting and progress tracking

### **Security Features**
- **Environment Variables**: All secrets in `.env` (gitignored)
- **Restricted Permissions**: Output files owner-only access (600)
- **No Sensitive Data**: No API keys or tokens in code
- **Safe Processing**: No external data execution or injection

### **Reliability**
- **Signal-based Timeouts**: Proper cleanup of system resources
- **Exception Handling**: Catches all possible error scenarios
- **Fallback Mechanisms**: Multiple search strategies for robustness
- **Process Isolation**: Individual failures don't crash the entire process

## 🔄 **Usage Patterns**

### **Daily Workflow**
1. **Morning**: Open Claude Code or Cursor
2. **Execute**: Run the daily intros script
3. **Review**: Check generated markdown report
4. **Complete**: Process takes 30-60 seconds

### **Batch Processing**
- **Multiple Users**: Handles multiple introductions per execution
- **Date Ranges**: Process historical introductions
- **Flexible Output**: Customizable report naming and formatting

### **Integration Ready**
- **API Compatible**: Easy integration with other tools
- **Data Export**: Structured output for analytics
- **Customizable**: Configurable templates and processing rules

---

## 📚 **Documentation**

- **📖 [README.md](README.md)**: Main guide (this file)
- **📋 [docs/PROJECT_OVERVIEW.md](docs/PROJECT_OVERVIEW.md)**: Technical documentation
- **🎯 [docs/DUAL_MODE_USAGE.md](docs/DUAL_MODE_USAGE.md)**: Dual-mode guide
- **🔒 [docs/SECURITY.md](docs/SECURITY.md)**: Security guide
- **⚡ [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)**: Quick commands
- **📚 [docs/README.md](docs/README.md)**: Documentation index

## 🤝 **Contributing**

This project follows software engineering best practices:
- **Modular Architecture**: Clean separation of concerns
- **Error Resilience**: Comprehensive error handling
- **Documentation**: Both human and LLM-optimized docs
- **Testing**: Robust test coverage (coming soon)
- **Monitoring**: Detailed logging and observability
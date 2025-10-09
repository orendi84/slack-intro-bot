# Feature Branch: Dual-Mode MCP Support

## 🎯 Purpose

This branch implements dual-mode support for the Slack Intro Bot, enabling it to work seamlessly in both:

1. **Cursor IDE** - where MCP tools are not directly available
2. **Claude Code** - where MCP Zapier tools can be used directly

## 🆕 New Files

### 1. `intro_extraction_api.py`
Main API for dual-mode operation.

**Key Functions**:
- `detect_execution_environment()` - Auto-detects if running in Cursor or Claude Code
- `generate_mcp_request()` - Creates structured prompts for Claude Code
- `extract_intros_mcp_mode()` - Directly executes extraction in Claude Code
- `extract_intros_auto()` - Auto-selects appropriate mode

**Usage in Cursor IDE**:
```python
from intro_extraction_api import generate_mcp_request

# Generate request for Claude Code
generate_mcp_request("2025-10-01", "2025-10-09")
```

**Usage in Claude Code**:
```python
from intro_extraction_api import extract_intros_mcp_mode

# Execute directly
result = extract_intros_mcp_mode("2025-10-01", "2025-10-09")
```

### 2. `claude_code_executor.py`
Specialized executor designed for Claude Code environment.

**Key Features**:
- Clear step-by-step execution instructions
- MCP tool call templates
- Result processing functions
- Markdown report generation

**Usage in Claude Code**:
Just ask Claude Code:
```
Run intro extraction for October 1-9, 2025 using claude_code_executor.py
```

### 3. `DUAL_MODE_USAGE.md`
Comprehensive documentation covering:
- How to use both modes
- When to use each mode
- Example workflows
- Troubleshooting tips
- API reference

### 4. `test_dual_mode.py`
Test suite to verify dual-mode functionality.

**Run tests**:
```bash
python3 test_dual_mode.py
```

## 📝 Modified Files

### `daily_intros.py`
- Added documentation about dual-mode support
- No functional changes to preserve backward compatibility

### `mcp_adapter.py`
- Already supports environment detection
- Works with both Cursor and Claude Code

## 🔄 How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Execution Environment                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────┐              ┌──────────────────┐       │
│  │  Cursor IDE    │              │   Claude Code    │       │
│  │                │              │                  │       │
│  │  - Code Editor │              │  - MCP Tools     │       │
│  │  - No MCP      │              │  - Direct Access │       │
│  └────────┬───────┘              └────────┬─────────┘       │
│           │                               │                 │
│           ▼                               ▼                 │
│  ┌──────────────────┐          ┌──────────────────┐        │
│  │ Request Generator│          │  MCP Executor    │        │
│  │                  │          │                  │        │
│  │ - Creates prompt │          │ - Calls MCP tools│        │
│  │ - Formats params │          │ - Processes data │        │
│  │ - Saves JSON     │          │ - Generates MD   │        │
│  └──────────┬───────┘          └──────────┬───────┘        │
│             │                              │                │
│             │      Prompt Transfer         │                │
│             └──────────►  ◄────────────────┘                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Flow Diagram

```
User Request
     │
     ▼
Environment Detection
     │
     ├─────────► Cursor IDE Detected
     │                 │
     │                 ▼
     │           Generate Request
     │                 │
     │                 ▼
     │           Format Prompt
     │                 │
     │                 ▼
     │           Display/Save
     │                 │
     │                 ▼
     │           USER COPIES TO CLAUDE CODE ──┐
     │                                         │
     └─────────► Claude Code Detected  ◄──────┘
                       │
                       ▼
                 Execute with MCP
                       │
                       ▼
                 Process Results
                       │
                       ▼
                 Save Reports
                       │
                       ▼
                    Complete
```

## 🚀 Usage Examples

### Example 1: Cursor IDE → Claude Code

**Step 1: In Cursor IDE**
```bash
cd /path/to/slack-intro-bot
python3 intro_extraction_api.py 2025-10-01 2025-10-09
```

**Output**:
```
============================================================
📋 COPY THE FOLLOWING TO CLAUDE CODE:
============================================================
Please extract Slack introductions using the following parameters:

Request ID: 20251009_143025
Start Date: 2025-10-01
End Date: 2025-10-09

[... full prompt ...]
============================================================
```

**Step 2: Copy the prompt**

**Step 3: In Claude Code, paste and execute**

Claude Code will:
1. Parse the request
2. Call `mcp_Zapier_slack_find_message`
3. Process intros
4. Save results

### Example 2: Direct in Claude Code

**Ask Claude Code**:
```
Please extract Slack introductions from October 1-9, 2025.
Use claude_code_executor.py to search #intros, find LinkedIn profiles,
and generate welcome messages.
```

**Claude Code executes automatically** and saves results.

### Example 3: Programmatic Auto-Mode

```python
from intro_extraction_api import extract_intros_auto

# Works in both environments
result = extract_intros_auto(
    start_date="2025-10-01",
    end_date="2025-10-09"
)

if result.get("mode") == "request_generated":
    print("Running in Cursor - copy the prompt above")
elif result.get("success"):
    print(f"Executed in Claude Code - saved to {result['filename']}")
```

## 🧪 Testing

### Run Full Test Suite
```bash
python3 test_dual_mode.py
```

### Expected Output in Cursor IDE
```
🚀 DUAL MODE TESTING SUITE
============================================================

🧪 Testing Environment Detection
✅ Detected environment: CURSOR
   📌 MCP tools are NOT available
   📌 Running in Cursor IDE mode

🧪 Testing Cursor IDE Mode (Request Generation)
✅ Request generated successfully

🧪 Testing Auto Mode
✅ Auto mode: Generated request (Cursor IDE)

✅ All tests passed for Cursor IDE mode
```

### Expected Output in Claude Code
```
🧪 Testing Environment Detection
✅ Detected environment: MCP
   📌 MCP tools are available
   📌 Running in Claude Code mode

🧪 Testing MCP Mode
✅ Extraction complete
📁 Report saved to: welcome_messages/daily_intros_2025-10-09.md
```

## 🔍 Environment Detection

The system detects the environment using:

1. **Global Function Check**: Looks for MCP functions in global namespace
2. **Environment Variables**: Checks for `CLAUDE_CODE_ENV` or `MCP_SERVER_ACTIVE`
3. **Frame Inspection**: Uses Python introspection to detect MCP context

```python
def detect_execution_environment() -> str:
    # Try multiple detection methods
    # Returns: 'mcp', 'cursor', or 'unknown'
```

## 📊 Output Formats

### Markdown Report
Standard format (unchanged):
```markdown
# Daily Introductions - 2025-10-09

## 1. John Doe
### 👤 User Information
- **Name:** John Doe
- **LinkedIn:** https://linkedin.com/in/johndoe

### 💬 Draft Welcome Message
Welcome to the community, John! 🎉

### 📝 Original Introduction
> Hi everyone! I'm John...
```

### JSON Results (New)
```json
{
  "request_id": "20251009_143025",
  "timestamp": "2025-10-09T14:30:25Z",
  "search_query": "in:intros after:2025-10-01 before:2025-10-09",
  "intro_count": 3,
  "intros": [...]
}
```

## ⚠️ Known Limitations

### Cursor IDE Mode
- Cannot directly execute MCP tools
- Requires manual copy-paste to Claude Code
- Cannot verify Slack connection

### Claude Code Mode
- Requires MCP Zapier server to be connected
- Subject to Zapier API quota limits
- May have latency depending on Zapier response time

## 🔧 Troubleshooting

### Issue: "MCP tools not available" in Claude Code

**Solution**:
1. Open Claude Code Settings → MCP Servers
2. Verify Zapier server is connected and active
3. Test connection with a simple Slack search
4. Reconnect if necessary

### Issue: Environment detection incorrect

**Solution**:
1. Set environment variable manually:
   ```bash
   export CLAUDE_CODE_ENV=true  # For Claude Code
   export CLAUDE_CODE_ENV=false # For Cursor
   ```

2. Or specify mode explicitly in code:
   ```python
   # Force MCP mode
   result = extract_intros_mcp_mode(...)
   
   # Force request generation
   prompt = generate_mcp_request(...)
   ```

### Issue: Zapier quota exceeded

**Solution**:
1. Check https://zapier.com/app/dashboard
2. Upgrade plan or wait for quota reset
3. Use direct Slack API as alternative

## 📚 Documentation

- **Main Guide**: [DUAL_MODE_USAGE.md](DUAL_MODE_USAGE.md)
- **MCP Setup**: [README_MCP_SETUP.md](README_MCP_SETUP.md)
- **Project Overview**: [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- **Security**: [SECURITY.md](SECURITY.md)

## 🔄 Merging to Main

### Pre-Merge Checklist

- [ ] All tests pass in Cursor IDE
- [ ] All tests pass in Claude Code
- [ ] Documentation is complete
- [ ] No breaking changes to existing API
- [ ] Backward compatibility verified
- [ ] Security review completed

### Merge Command
```bash
git checkout main
git merge feature/dual-mode-mcp-support
git push origin main
```

## 🎯 Benefits

### For Cursor IDE Users
- ✅ Can prepare extraction requests
- ✅ Can batch multiple requests
- ✅ Can review prompts before execution
- ✅ Clear instructions for next steps

### For Claude Code Users
- ✅ Direct execution with MCP tools
- ✅ No manual copy-paste needed
- ✅ Immediate results
- ✅ Full automation possible

### For Both
- ✅ Consistent output format
- ✅ Same data quality
- ✅ Shared codebase
- ✅ Easy to switch between modes

## 🚀 Future Enhancements

### Planned Features
1. **Web UI**: Browser-based interface for both modes
2. **Scheduled Execution**: Cron jobs + auto-sync between environments
3. **Result Cache**: Store results to avoid re-processing
4. **Batch Processing**: Handle multiple date ranges in one request
5. **Direct Slack API**: Fallback when MCP/Zapier unavailable

### API Extensions
1. **Webhook Support**: Trigger extraction from external events
2. **REST API**: HTTP endpoints for programmatic access
3. **WebSocket**: Real-time intro notifications
4. **GraphQL**: Flexible query interface

---

**Branch Created**: October 9, 2025  
**Status**: Ready for testing  
**Maintainer**: Development Team


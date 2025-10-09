# Slack Intro Bot - Project Overview for LLMs

## 🎯 **Project Purpose**
Automated daily introduction processing system for Slack workspaces that extracts LinkedIn profiles from new team member introductions and generates formatted welcome messages.

## 🏗️ **Architecture Overview**

### **Core Components**
1. **`daily_intros.py`** - Main orchestrator and entry point
2. **`user_profile_search.py`** - LinkedIn profile extraction module
3. **`mcp_adapter.py`** - Multi-environment MCP server abstraction layer

### **Execution Flow**
```
Message Search → LinkedIn Extraction → Profile Search (if needed) → Report Generation
```

## 📁 **File Structure & Responsibilities**

### **Primary Files**
- **`daily_intros.py`** (416 lines)
  - Main entry point for the application
  - Three-phase processing: Message extraction → Profile search → Report generation
  - Handles Slack message parsing and LinkedIn link extraction from message content
  - Generates markdown reports with welcome messages

- **`user_profile_search.py`** (305 lines)
  - Fallback LinkedIn profile search when not found in messages
  - Multi-layer timeout protection (30s → 45s → 60s)
  - Safe wrapper function for guaranteed completion
  - Comprehensive error handling and logging

- **`mcp_adapter.py`** (New)
  - Auto-detects MCP server environment (Claude vs Cursor)
  - Maps function calls to environment-specific implementations
  - Handles `mcp_Zapier_*` vs `mcp__zapier__*` function naming differences

## 🔧 **Key Features**

### **Multi-Environment Support**
- **Claude Code Environment**: Uses `mcp_Zapier_*` functions
- **Cursor Code Editor**: Uses `mcp__zapier__*` functions
- **Auto-detection**: No manual configuration required

### **Optimized Processing**
- **Conditional Profile Search**: Only searches profiles when LinkedIn not found in messages
- **Batch Processing**: Processes all messages before profile searches
- **Timeout Protection**: Multiple layers prevent hanging processes

### **Robust Error Handling**
- **Guaranteed Completion**: Always returns within 60 seconds maximum
- **Comprehensive Logging**: Detailed progress tracking and error reporting
- **Graceful Degradation**: Continues processing even when profile search fails

## 🚀 **Usage Instructions**

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
python3 daily_intros.py
```

### **Expected Output**
- Markdown report file: `daily_intros_YYYY-MM-DD.md`
- Console logs showing processing progress
- LinkedIn profile extraction results

## 🔍 **LinkedIn Extraction Strategy**

### **Phase 1: Message Content Analysis**
- Extracts LinkedIn URLs from introduction message text
- Uses regex patterns for various LinkedIn URL formats
- Handles URLs in angle brackets, parentheses, and plain text

### **Phase 2: Profile Search (Fallback)**
- Only triggered when LinkedIn not found in message content
- Searches Slack user profile fields: `status_text`, `title`, `display_name`, etc.
- Includes custom profile fields if available
- Fallback to recent message search if profile fields empty

### **Phase 3: Username Search (Secondary Fallback)**
- Searches by username if user ID search fails
- Checks same profile fields as user ID search

## ⚙️ **Configuration**

### **Default Settings**
- **Slack Channel**: `#intros`
- **Time Range**: Last 24 hours
- **Timeout Limits**: 30s (basic) → 45s (fallback) → 60s (safe wrapper)
- **Output Format**: Markdown with embedded LinkedIn links

### **Customizable Parameters**
- Date range for message search
- Output file naming convention
- Timeout durations
- LinkedIn URL pattern matching

## 🛡️ **Safety Features**

### **Timeout Protection**
- Signal-based timeout handlers
- Multiple timeout layers with escalation
- Automatic cleanup of alarm signals
- Guaranteed process completion

### **Error Recovery**
- Continues processing if individual profile searches fail
- Provides detailed error logging
- Never hangs or crashes the main process
- Graceful handling of missing MCP functions

## 📊 **Performance Characteristics**

### **Optimization Strategies**
- **Batch Processing**: Reduces API calls by processing all messages first
- **Conditional Execution**: Only runs expensive profile searches when needed
- **Caching**: Reuses MCP adapter instances
- **Early Termination**: Stops searching once LinkedIn found

### **Resource Usage**
- **Memory**: Minimal - processes messages sequentially
- **API Calls**: Optimized to minimize Slack API usage
- **Time Complexity**: O(n) where n is number of introduction messages

## 🔧 **Technical Implementation**

### **Dependencies**
- **Python 3.7+**
- **MCP Server Integration** (Zapier)
- **Slack API Access** (via MCP)
- **Standard Library**: `re`, `signal`, `datetime`, `json`, `os`

### **Error Handling Strategy**
- **Try-Catch Blocks**: Around all MCP function calls
- **Timeout Handlers**: Signal-based with proper cleanup
- **Fallback Mechanisms**: Multiple search strategies
- **Logging**: Comprehensive progress and error reporting

## 📈 **Monitoring & Observability**

### **Logging Levels**
- **🔍 Debug**: Detailed field analysis and search progress
- **✅ Success**: LinkedIn URLs found and processing completion
- **⚠️ Warning**: Non-critical errors and fallback activations
- **🚨 Error**: Critical failures and timeout scenarios
- **🏁 Completion**: Process termination and final status

### **Key Metrics**
- Number of messages processed
- LinkedIn extraction success rate
- Profile search fallback usage
- Processing time per user
- Error rates and types

## 🚀 **Deployment Considerations**

### **Environment Requirements**
- Access to Slack workspace with `#intros` channel
- MCP server with Zapier integration enabled
- Python environment with required dependencies
- Appropriate Slack API permissions

### **Scalability**
- Handles multiple users per execution
- Processes messages in batches
- Configurable timeout limits for different environments
- Memory-efficient sequential processing

## 🔮 **Future Enhancement Opportunities**

### **Potential Improvements**
- **Caching**: Store profile data to reduce repeated API calls
- **Parallel Processing**: Concurrent profile searches for multiple users
- **Advanced NLP**: Better introduction message detection
- **Integration**: Connect with HR systems or employee databases
- **Analytics**: Track onboarding metrics and engagement

### **Extensibility Points**
- **Custom Extractors**: Plugin system for different profile sources
- **Output Formats**: Support for HTML, PDF, or other formats
- **Notification Systems**: Integration with email or other communication tools
- **Data Export**: Structured data output for analytics platforms

---

**Last Updated**: January 2025
**Version**: 2.0
**Maintainer**: Development Team

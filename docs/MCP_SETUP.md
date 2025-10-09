# MCP Zapier Setup Guide

## 🔧 Current Issue

The daily intros script is generating empty MD files because the MCP Zapier server connection is not working properly. Here's what's happening:

### ❌ Problem Identified
1. **MCP Functions Not Available**: The `mcp_Zapier_slack_find_message` functions are not available in the Python global namespace
2. **Zapier Quota Exceeded**: When MCP functions are called directly, they return "insufficient tasks on account" error
3. **Environment Mismatch**: The script works in some MCP environments but not others

### 🧪 Diagnostic Results
```
Available MCP functions: 0/4
Missing MCP functions: 4
Connection status: no_response
```

## 💡 Solutions

### Option 1: Fix Zapier Quota (Recommended)
The MCP Zapier server is working, but your Zapier account has insufficient tasks/quota:

1. **Check your Zapier account dashboard**:
   - Go to https://zapier.com/app/dashboard
   - Check your current task usage and quota
   - Look for any billing or quota warnings

2. **Upgrade your Zapier plan**:
   - Free plan: 100 tasks/month
   - Starter plan: 750 tasks/month ($19.99/month)
   - Professional plan: 2,000 tasks/month ($49/month)

3. **Wait for quota reset**:
   - Zapier quotas reset monthly
   - Check when your next reset date is

### Option 2: Use Alternative MCP Environment
The script works better in certain MCP environments:

1. **Claude Code Environment**: Try running the script within Claude Code
2. **Cursor with MCP**: Ensure Cursor has MCP Zapier server properly configured
3. **Direct MCP Tool Usage**: Use MCP tools directly instead of the Python script

### Option 3: Manual Data Input
If MCP connection continues to fail, you can manually input introduction data:

1. **Create sample data file**:
   ```bash
   python3 create_sample_data.py
   ```

2. **Run with sample data**:
   ```bash
   python3 daily_intros.py --use-sample-data
   ```

## 🔧 Technical Details

### MCP Function Availability
The script expects these functions to be available:
- `mcp_Zapier_slack_find_message`
- `mcp_Zapier_slack_find_user_by_id`
- `mcp_Zapier_slack_find_user_by_username`
- `mcp_Zapier_slack_api_request_beta`

### Environment Variables (Optional)
You can set these environment variables for better MCP integration:
```bash
export MCP_SERVER_URL="your_mcp_server_url"
export ZAPIER_API_KEY="your_zapier_api_key"
export SLACK_BOT_TOKEN="your_slack_bot_token"
```

## 🚀 Quick Fix

### Immediate Solution
1. **Check your Zapier account quota**
2. **Upgrade Zapier plan if needed**
3. **Try running the script again**

### Verification
Run the diagnostic script to check if the issue is resolved:
```bash
python3 diagnose_mcp.py
```

## 📊 Expected Behavior

When working correctly, you should see:
```
✅ MCP connection working!
📨 Found X messages from Slack API
✅ Generated welcome for: [User Name]
💾 Report saved to: ./welcome_messages/daily_intros_YYYY-MM-DD.md
```

## 🆘 Troubleshooting

### Still Getting Empty Files?
1. Check Zapier quota: https://zapier.com/app/dashboard
2. Verify Slack workspace has `#intros` channel
3. Ensure Slack app has proper permissions
4. Try running in a different MCP environment

### Need Help?
- Check Zapier documentation: https://zapier.com/help
- Review MCP server logs
- Contact Zapier support for quota issues

---

**Last Updated**: September 21, 2025
**Status**: MCP Zapier quota exceeded - needs account upgrade or quota reset

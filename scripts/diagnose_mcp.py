#!/usr/bin/env python3
"""
MCP Zapier Connection Diagnostic Script

This script helps diagnose and fix MCP Zapier server connection issues.
"""

import sys
import os
import subprocess
from typing import Dict, List, Any

def check_mcp_functions():
    """Check what MCP functions are available"""
    print("🔍 Checking MCP Functions Availability")
    print("=" * 50)
    
    # Check for Zapier MCP functions
    zapier_functions = [
        'mcp_Zapier_slack_find_message',
        'mcp_Zapier_slack_find_user_by_id', 
        'mcp_Zapier_slack_find_user_by_username',
        'mcp_Zapier_slack_api_request_beta'
    ]
    
    available_functions = []
    missing_functions = []
    
    for func_name in zapier_functions:
        if func_name in globals():
            available_functions.append(func_name)
            print(f"✅ {func_name}")
        else:
            missing_functions.append(func_name)
            print(f"❌ {func_name}")
    
    print(f"\n📊 Summary:")
    print(f"   Available: {len(available_functions)}/{len(zapier_functions)}")
    print(f"   Missing: {len(missing_functions)}")
    
    return available_functions, missing_functions

def test_mcp_connection():
    """Test MCP connection by trying to call a function"""
    print("\n🧪 Testing MCP Connection")
    print("=" * 50)
    
    try:
        # Try to use the MCP function directly
        from mcp_adapter import get_mcp_adapter
        
        mcp = get_mcp_adapter()
        print(f"✅ MCP Adapter created successfully")
        print(f"   Server type: {mcp.server_type}")
        print(f"   Function mapping: {mcp.function_map}")
        
        # Try to call a simple function
        print("\n📞 Testing Slack message search...")
        result = mcp.slack_find_message(
            instructions="Test search for any messages",
            query="test",
            sort_by="timestamp",
            sort_dir="desc"
        )
        
        if result:
            if isinstance(result, dict) and result.get('isError'):
                error_msg = result.get('error', ['Unknown error'])
                print(f"⚠️  MCP call returned error: {error_msg}")
                
                if 'insufficient tasks' in str(error_msg).lower():
                    print("\n💡 SOLUTION FOUND:")
                    print("   Your Zapier account has insufficient tasks/quota")
                    print("   Options:")
                    print("   1. Upgrade your Zapier plan")
                    print("   2. Wait for monthly quota reset")
                    print("   3. Use a different Zapier account")
                    return "quota_exceeded"
                else:
                    print(f"   Other API error: {error_msg}")
                    return "api_error"
            else:
                print("✅ MCP connection working!")
                return "working"
        else:
            print("❌ MCP call returned None")
            return "no_response"
            
    except Exception as e:
        print(f"❌ Error testing MCP connection: {e}")
        return "connection_error"

def check_environment():
    """Check the current environment setup"""
    print("\n🌍 Environment Check")
    print("=" * 50)
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check if we're in a specific environment
    if 'claude' in sys.executable.lower():
        print("✅ Running in Claude environment")
    elif 'cursor' in sys.executable.lower():
        print("✅ Running in Cursor environment")
    else:
        print("⚠️  Unknown environment")
    
    # Check for environment variables
    env_vars = ['MCP_SERVER_URL', 'ZAPIER_API_KEY', 'SLACK_BOT_TOKEN']
    for var in env_vars:
        if var in os.environ:
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set")

def provide_solutions(status: str):
    """Provide solutions based on the diagnostic results"""
    print("\n💡 SOLUTIONS")
    print("=" * 50)
    
    if status == "quota_exceeded":
        print("🔧 Zapier Quota Exceeded - Solutions:")
        print("   1. Check your Zapier account dashboard for quota usage")
        print("   2. Upgrade to a higher Zapier plan if needed")
        print("   3. Wait for monthly quota reset")
        print("   4. Use a different Zapier account with available quota")
        print("   5. Consider using Zapier's free tier limits")
        
    elif status == "connection_error":
        print("🔧 Connection Error - Solutions:")
        print("   1. Check if MCP Zapier server is properly configured")
        print("   2. Verify Zapier API credentials")
        print("   3. Check network connectivity")
        print("   4. Restart the MCP server")
        print("   5. Check MCP server logs for errors")
        
    elif status == "api_error":
        print("🔧 API Error - Solutions:")
        print("   1. Check Zapier API documentation for recent changes")
        print("   2. Verify Slack app permissions")
        print("   3. Check if Slack workspace has the required channels")
        print("   4. Verify Slack bot token permissions")
        
    elif status == "no_response":
        print("🔧 No Response - Solutions:")
        print("   1. Check MCP server status")
        print("   2. Verify Zapier integration is active")
        print("   3. Check API rate limits")
        print("   4. Try again after a few minutes")
        
    else:
        print("🔧 General Troubleshooting:")
        print("   1. Restart the MCP Zapier server")
        print("   2. Check Zapier account status")
        print("   3. Verify Slack workspace permissions")
        print("   4. Check network connectivity")
        print("   5. Review MCP server configuration")

def main():
    """Main diagnostic function"""
    print("🔧 MCP Zapier Connection Diagnostic")
    print("=" * 60)
    print("This script will help diagnose MCP Zapier server connection issues.\n")
    
    # Run diagnostics
    available_funcs, missing_funcs = check_mcp_functions()
    connection_status = test_mcp_connection()
    check_environment()
    
    # Provide solutions
    provide_solutions(connection_status)
    
    print(f"\n📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print(f"Available MCP functions: {len(available_funcs)}")
    print(f"Missing MCP functions: {len(missing_funcs)}")
    print(f"Connection status: {connection_status}")
    
    if connection_status == "working":
        print("✅ MCP Zapier connection is working correctly!")
        return 0
    else:
        print("❌ MCP Zapier connection has issues that need to be resolved.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

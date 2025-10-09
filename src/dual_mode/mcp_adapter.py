#!/usr/bin/env python3
"""
MCP Server Adapter

This module handles the detection of different MCP servers and provides
the correct function calls based on the execution environment.

Supports:
- Claude Code Environment (mcp_Zapier_* functions)
- Cursor Code Editor (mcp__zapier__* functions)
"""

import inspect
from typing import Dict, Any, Optional, Callable

class MCPAdapter:
    """Adapter class to handle different MCP server function naming conventions"""
    
    def __init__(self):
        self.function_map = {}
        self.server_type = self._detect_mcp_server()
        self._setup_function_mapping()
    
    def _detect_mcp_server(self) -> str:
        """Detect which MCP server is available"""
        # Check for Claude Code Environment functions (mcp__zapier__*)
        claude_functions = [
            'mcp__zapier__slack_find_message',
            'mcp__zapier__slack_find_user_by_id',
            'mcp__zapier__slack_find_user_by_username'
        ]

        # Check for Cursor functions (also mcp__zapier__*)
        cursor_functions = [
            'mcp__zapier__slack_find_message',
            'mcp__zapier__slack_find_user_by_id',
            'mcp__zapier__slack_find_user_by_username'
        ]
        
        # Check if Claude functions exist
        claude_available = any(self._function_exists(func) for func in claude_functions)
        
        # Check if Cursor functions exist
        cursor_available = any(self._function_exists(func) for func in cursor_functions)
        
        if claude_available:
            return 'claude'
        elif cursor_available:
            return 'cursor'
        
        # If neither is found, default to claude and let the error handling take care of it
        return 'claude'
    
    def _function_exists(self, function_name: str) -> bool:
        """Check if a function exists in the global namespace"""
        try:
            return function_name in globals()
        except:
            return False
    
    def _check_tool_availability(self) -> bool:
        """Check if MCP tools are available through the tool interface"""
        # This is a workaround - in some environments, MCP functions
        # are available through tools but not in globals()
        return True  # Assume tools are available if we're running in an MCP environment
    
    def _setup_function_mapping(self):
        """Setup function mapping based on detected server type"""
        if self.server_type == 'claude':
            # Claude Code Environment uses mcp__zapier__* functions
            self.function_map = {
                'slack_find_message': 'mcp__zapier__slack_find_message',
                'slack_find_user_by_id': 'mcp__zapier__slack_find_user_by_id',
                'slack_find_user_by_username': 'mcp__zapier__slack_find_user_by_username',
                'slack_api_request_beta': 'mcp__zapier__slack_api_request_beta'
            }
        elif self.server_type == 'cursor':
            # Cursor uses mcp__zapier__* functions
            self.function_map = {
                'slack_find_message': 'mcp__zapier__slack_find_message',
                'slack_find_user_by_id': 'mcp__zapier__slack_find_user_by_id',
                'slack_find_user_by_username': 'mcp__zapier__slack_find_user_by_username',
                'slack_api_request_beta': 'mcp__zapier__slack_api_request_beta'
            }
        
        print(f"🔧 MCP Server detected: {self.server_type.upper()}")
        print(f"📋 Function mapping: {self.function_map}")
    
    def _refresh_detection(self):
        """Refresh server detection and function mapping"""
        old_server_type = self.server_type
        self.server_type = self._detect_mcp_server()
        
        if old_server_type != self.server_type:
            print(f"🔄 MCP Server type changed from {old_server_type} to {self.server_type}")
            self._setup_function_mapping()
    
    def get_function(self, function_key: str) -> Optional[Callable]:
        """Get the actual function based on the detected server type"""
        # Refresh detection before getting function
        self._refresh_detection()
        
        function_name = self.function_map.get(function_key)
        if not function_name:
            print(f"⚠️  Function key '{function_key}' not found in mapping")
            return None
        
        try:
            return globals()[function_name]
        except KeyError:
            print(f"⚠️  Function '{function_name}' not available in global namespace")
            return None
    
    def call_function(self, function_key: str, **kwargs) -> Optional[Any]:
        """Call the appropriate MCP function based on the detected server type"""
        func = self.get_function(function_key)
        if not func:
            print(f"❌ Cannot call function '{function_key}' - function not available")
            return None
        
        try:
            print(f"📞 Calling {self.function_map[function_key]} with {len(kwargs)} parameters")
            result = func(**kwargs)
            
            # Check for Zapier account limitations
            if isinstance(result, dict) and result.get('isError'):
                error_msg = result.get('error', ['Unknown error'])
                if 'insufficient tasks' in str(error_msg).lower():
                    print("❌ Zapier account has insufficient tasks/quota")
                    print("💡 Solution: Upgrade Zapier plan or wait for quota reset")
                    print(f"📊 Error details: {error_msg}")
                else:
                    print(f"⚠️  Zapier API error: {error_msg}")
                return None
            
            return result
        except Exception as e:
            print(f"⚠️  Error calling {self.function_map[function_key]}: {e}")
            return None
    
    def slack_find_message(self, **kwargs) -> Optional[Dict]:
        """Find Slack messages using the appropriate MCP server"""
        return self.call_function('slack_find_message', **kwargs)
    
    def slack_find_user_by_id(self, **kwargs) -> Optional[Dict]:
        """Find Slack user by ID using the appropriate MCP server"""
        return self.call_function('slack_find_user_by_id', **kwargs)
    
    def slack_find_user_by_username(self, **kwargs) -> Optional[Dict]:
        """Find Slack user by username using the appropriate MCP server"""
        return self.call_function('slack_find_user_by_username', **kwargs)
    
    def slack_api_request_beta(self, **kwargs) -> Optional[Dict]:
        """Make Slack API request using the appropriate MCP server"""
        return self.call_function('slack_api_request_beta', **kwargs)

# Global instance
mcp_adapter = MCPAdapter()

def get_mcp_adapter() -> MCPAdapter:
    """Get the global MCP adapter instance"""
    return mcp_adapter

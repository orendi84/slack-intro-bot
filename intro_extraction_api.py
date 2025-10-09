#!/usr/bin/env python3
"""
Intro Extraction API - Dual Mode Support

This module provides intro extraction functionality that works in two modes:
1. MCP Mode (Claude Code): Direct access to MCP Zapier tools
2. Request Mode (Cursor IDE): Generates structured requests for Claude Code

Usage in Claude Code:
    from intro_extraction_api import extract_intros_mcp_mode
    result = extract_intros_mcp_mode(start_date="2025-10-01")

Usage in Cursor IDE:
    from intro_extraction_api import generate_mcp_request
    request = generate_mcp_request(start_date="2025-10-01")
    # Copy this request and run it in Claude Code
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os


class IntroExtractionRequest:
    """Represents a request for intro extraction that can be executed in Claude Code"""
    
    def __init__(self, start_date: Optional[str] = None, end_date: Optional[str] = None):
        self.start_date = start_date
        self.end_date = end_date
        self.request_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert request to dictionary format"""
        return {
            "request_id": self.request_id,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "timestamp": datetime.now().isoformat()
        }
    
    def to_json(self) -> str:
        """Convert request to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    def generate_claude_code_prompt(self) -> str:
        """Generate a prompt that can be copied into Claude Code"""
        return f"""Please extract Slack introductions using the following parameters:

Request ID: {self.request_id}
Start Date: {self.start_date or 'auto-detect from latest report'}
End Date: {self.end_date or 'now'}

Execute the following steps:
1. Search for messages in #intros channel using mcp_Zapier_slack_find_message
2. Filter messages for introductions
3. Extract LinkedIn profiles from messages
4. For users without LinkedIn in messages, search their Slack profiles
5. Generate welcome messages
6. Save results to: intro_results_{self.request_id}.json

Search Query: in:intros {self._build_search_query()}

Use these MCP tools:
- mcp_Zapier_slack_find_message
- mcp_Zapier_slack_find_user_by_id
- mcp_Zapier_slack_api_request_beta
"""
    
    def _build_search_query(self) -> str:
        """Build Slack search query based on date parameters"""
        if self.start_date and self.end_date:
            return f"after:{self.start_date} before:{self.end_date}"
        elif self.start_date:
            return f"after:{self.start_date}"
        elif self.end_date:
            return f"before:{self.end_date}"
        else:
            # Default to last 7 days
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            return f"after:{week_ago}"


def detect_execution_environment() -> str:
    """
    Detect if we're running in Claude Code (MCP available) or Cursor IDE
    
    Returns:
        'mcp' if MCP tools are available
        'cursor' if running in Cursor IDE
        'unknown' if cannot determine
    """
    # Try to detect MCP functions in the environment
    try:
        # In Claude Code, MCP tools are available as functions
        # We can't directly check for them in Python, but we can use frame inspection
        import inspect
        frame = inspect.currentframe()
        if frame and hasattr(frame, 'f_globals'):
            # Check for MCP tool signatures in globals
            globals_keys = frame.f_globals.keys()
            mcp_indicators = [
                'mcp_Zapier_slack_find_message',
                'mcp_zapier_slack_find_message',
                '__mcp_tools__'  # Potential MCP environment marker
            ]
            if any(indicator in globals_keys for indicator in mcp_indicators):
                return 'mcp'
    except:
        pass
    
    # Check for Claude Code environment variables
    if os.getenv('CLAUDE_CODE_ENV') or os.getenv('MCP_SERVER_ACTIVE'):
        return 'mcp'
    
    # Default to Cursor IDE mode
    return 'cursor'


def generate_mcp_request(start_date: Optional[str] = None, 
                        end_date: Optional[str] = None,
                        output_file: Optional[str] = None) -> str:
    """
    Generate a request for intro extraction that can be run in Claude Code
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        output_file: Path to save the request JSON
    
    Returns:
        Claude Code prompt as string
    """
    request = IntroExtractionRequest(start_date, end_date)
    
    # Save request to file if specified
    if output_file:
        os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(request.to_json())
        print(f"📝 Request saved to: {output_file}")
    
    prompt = request.generate_claude_code_prompt()
    print("\n" + "="*60)
    print("📋 COPY THE FOLLOWING TO CLAUDE CODE:")
    print("="*60)
    print(prompt)
    print("="*60)
    
    return prompt


def extract_intros_mcp_mode(start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Extract intros directly using MCP tools (for use in Claude Code)
    
    This function should only be called in Claude Code where MCP tools are available.
    In Cursor IDE, use generate_mcp_request() instead.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Dictionary with extraction results
    """
    env = detect_execution_environment()
    
    if env == 'cursor':
        print("⚠️  WARNING: Running in Cursor IDE mode")
        print("MCP tools are not directly available in this environment.")
        print("\nUse generate_mcp_request() instead to create a request for Claude Code:")
        print("\n    from intro_extraction_api import generate_mcp_request")
        print("    generate_mcp_request(start_date='2025-10-01')")
        return {
            "error": "MCP tools not available in Cursor IDE",
            "solution": "Use generate_mcp_request() to create a Claude Code prompt"
        }
    
    # If we're in MCP mode, import the actual implementation
    try:
        from daily_intros import (
            get_cutoff_timestamp,
            get_messages_for_timestamp_range,
            parse_intro_message,
            generate_welcome_message,
            save_daily_intro_report
        )
        from user_profile_search import safe_profile_search_for_daily_intros
        
        print("🚀 Running in MCP mode (Claude Code)")
        print("="*60)
        
        # Get cutoff timestamp
        cutoff_timestamp = get_cutoff_timestamp(start_date)
        
        # Get messages
        messages, error = get_messages_for_timestamp_range(cutoff_timestamp, end_date)
        
        if error:
            return {
                "error": error,
                "messages": []
            }
        
        # Process messages
        intro_data_list = []
        for message in messages:
            intro_data = parse_intro_message(message)
            if intro_data:
                intro_data_list.append(intro_data)
                
                # Profile search if needed
                if not intro_data['linkedin_link']:
                    user_id = message.get('user', {}).get('id')
                    if user_id:
                        linkedin = safe_profile_search_for_daily_intros(
                            user_id, 
                            intro_data['username']
                        )
                        if linkedin:
                            intro_data['linkedin_link'] = linkedin
        
        # Generate welcome messages
        welcome_messages = []
        for intro_data in intro_data_list:
            welcome_msg = generate_welcome_message(intro_data)
            welcome_messages.append((intro_data, welcome_msg))
        
        # Save report
        output_date = end_date.split('T')[0] if end_date else None
        filename = save_daily_intro_report(welcome_messages, output_date=output_date)
        
        return {
            "success": True,
            "filename": filename,
            "intro_count": len(welcome_messages),
            "intros": intro_data_list
        }
    
    except Exception as e:
        return {
            "error": f"Error in MCP mode: {str(e)}",
            "success": False
        }


def extract_intros_auto(start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> Dict[str, Any]:
    """
    Auto-detect environment and run appropriate mode
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Dictionary with results or request prompt
    """
    env = detect_execution_environment()
    
    if env == 'mcp':
        print("🔧 Detected MCP environment - running extraction")
        return extract_intros_mcp_mode(start_date, end_date)
    else:
        print("🔧 Detected Cursor IDE - generating request")
        prompt = generate_mcp_request(start_date, end_date)
        return {
            "mode": "request_generated",
            "prompt": prompt,
            "instructions": "Copy the prompt above and run it in Claude Code"
        }


if __name__ == "__main__":
    import sys
    
    # Handle command line arguments
    start_date = sys.argv[1] if len(sys.argv) > 1 else None
    end_date = sys.argv[2] if len(sys.argv) > 2 else None
    
    print("🤖 Intro Extraction API - Dual Mode")
    print("="*60)
    
    result = extract_intros_auto(start_date, end_date)
    
    if result.get("mode") == "request_generated":
        print("\n✅ Request generated successfully!")
        print("📋 Copy the prompt above and paste it into Claude Code")
    elif result.get("success"):
        print(f"\n✅ Extraction complete!")
        print(f"📁 Report saved to: {result['filename']}")
        print(f"📊 Total introductions: {result['intro_count']}")
    else:
        print(f"\n❌ Error: {result.get('error')}")


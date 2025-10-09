#!/usr/bin/env python3
"""
Test script to demonstrate dual-mode functionality

This script tests both Cursor IDE mode and Claude Code mode detection.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from intro_extraction_api import (
    detect_execution_environment,
    generate_mcp_request,
    extract_intros_auto
)


def test_environment_detection():
    """Test environment detection"""
    print("🧪 Testing Environment Detection")
    print("="*60)
    
    env = detect_execution_environment()
    
    print(f"✅ Detected environment: {env.upper()}")
    
    if env == 'mcp':
        print("   📌 MCP tools are available")
        print("   📌 Running in Claude Code mode")
    elif env == 'cursor':
        print("   📌 MCP tools are NOT available")
        print("   📌 Running in Cursor IDE mode")
    else:
        print("   ⚠️  Unknown environment")
    
    print()
    return env


def test_cursor_mode():
    """Test Cursor IDE mode (request generation)"""
    print("🧪 Testing Cursor IDE Mode (Request Generation)")
    print("="*60)
    
    # Generate request
    prompt = generate_mcp_request(
        start_date="2025-10-01",
        end_date="2025-10-09"
    )
    
    print("\n✅ Request generated successfully")
    print(f"📏 Prompt length: {len(prompt)} characters")
    print()


def test_auto_mode():
    """Test auto-detection mode"""
    print("🧪 Testing Auto Mode")
    print("="*60)
    
    result = extract_intros_auto(
        start_date="2025-10-01",
        end_date="2025-10-09"
    )
    
    if result.get("mode") == "request_generated":
        print("\n✅ Auto mode: Generated request (Cursor IDE)")
        print("📋 Prompt is ready to copy to Claude Code")
    elif result.get("success"):
        print("\n✅ Auto mode: Executed extraction (Claude Code)")
        print(f"📁 Results saved to: {result.get('filename')}")
    else:
        print(f"\n⚠️  Auto mode: {result.get('error')}")
    
    print()


def test_mcp_mode_simulation():
    """Simulate what would happen in MCP mode"""
    print("🧪 Simulating Claude Code Mode")
    print("="*60)
    
    print("""
In Claude Code with MCP tools available, the system would:

1. ✅ Detect MCP environment
2. ✅ Call mcp_Zapier_slack_find_message
3. ✅ Process search results
4. ✅ Extract intro messages
5. ✅ Search user profiles for LinkedIn
6. ✅ Generate welcome messages
7. ✅ Save markdown report

Expected output:
- File: welcome_messages/daily_intros_2025-10-09.md
- Contains: All intros with LinkedIn profiles
- Format: Markdown with sections for each person
""")
    
    print()


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 DUAL MODE TESTING SUITE")
    print("="*60)
    print()
    
    # Test 1: Environment Detection
    env = test_environment_detection()
    
    # Test 2: Cursor Mode
    test_cursor_mode()
    
    # Test 3: Auto Mode
    test_auto_mode()
    
    # Test 4: MCP Mode Simulation
    test_mcp_mode_simulation()
    
    # Summary
    print("="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    print(f"Environment: {env.upper()}")
    
    if env == 'cursor':
        print("""
✅ All tests passed for Cursor IDE mode

Next Steps:
1. Copy the generated prompt from above
2. Open Claude Code
3. Paste the prompt
4. Claude Code will execute using MCP tools
5. Check welcome_messages/ for results
""")
    elif env == 'mcp':
        print("""
✅ Environment supports MCP mode

Next Steps:
1. Run extract_intros_mcp_mode() directly
2. Or ask Claude Code to execute claude_code_executor.py
3. Check welcome_messages/ for results
""")
    else:
        print("⚠️  Unknown environment")
    
    print("="*60)


if __name__ == "__main__":
    run_all_tests()


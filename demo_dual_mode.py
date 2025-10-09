#!/usr/bin/env python3
"""
Live Demo: Dual-Mode Intro Extraction

This script demonstrates how to use the dual-mode functionality.
Run this in Cursor IDE to see it in action.
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


def demo():
    """Run a live demonstration"""
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           SLACK INTRO BOT - DUAL MODE DEMONSTRATION          ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

This demonstration shows how the dual-mode system works.

""")
    
    # Step 1: Environment Detection
    print("STEP 1: Environment Detection")
    print("─" * 60)
    
    env = detect_execution_environment()
    
    if env == 'cursor':
        print("✅ Detected: CURSOR IDE")
        print("   You're currently in Cursor IDE")
        print("   This environment cannot directly access MCP tools")
        print()
    elif env == 'mcp':
        print("✅ Detected: CLAUDE CODE")
        print("   You're in Claude Code with MCP tools available")
        print("   Can execute extractions directly")
        print()
    else:
        print("⚠️  Detected: UNKNOWN")
        print("   Cannot determine environment")
        print()
    
    # Step 2: Show What Each Mode Does
    print("\nSTEP 2: Mode Capabilities")
    print("─" * 60)
    print()
    
    if env == 'cursor':
        print("📋 CURSOR IDE MODE CAPABILITIES:")
        print("   ✅ Generate requests for Claude Code")
        print("   ✅ Save requests to JSON files")
        print("   ✅ Review prompts before execution")
        print("   ✅ Batch process multiple requests")
        print("   ❌ Cannot execute MCP tools directly")
        print("   ❌ Cannot access Slack API")
        print()
        print("   💡 Solution: Generate request → Copy to Claude Code")
        print()
    elif env == 'mcp':
        print("🚀 CLAUDE CODE MODE CAPABILITIES:")
        print("   ✅ Execute MCP tools directly")
        print("   ✅ Access Slack API via Zapier")
        print("   ✅ Search messages in real-time")
        print("   ✅ Extract user profiles")
        print("   ✅ Generate reports automatically")
        print("   ✅ Immediate results")
        print()
    
    # Step 3: Practical Example
    print("\nSTEP 3: Practical Example")
    print("─" * 60)
    print()
    print("Let's extract intros from October 1-9, 2025")
    print()
    
    input("Press Enter to continue...")
    print()
    
    if env == 'cursor':
        print("🔄 Generating request for Claude Code...")
        print()
        print("─" * 60)
        
        # Generate the request
        prompt = generate_mcp_request(
            start_date="2025-10-01",
            end_date="2025-10-09"
        )
        
        print()
        print("─" * 60)
        print()
        print("✅ Request generated successfully!")
        print()
        print("NEXT STEPS:")
        print("1. Copy the prompt text shown above")
        print("2. Open Claude Code desktop application")
        print("3. Paste the prompt into Claude Code")
        print("4. Claude Code will execute it using MCP tools")
        print("5. Check welcome_messages/ for results")
        print()
        
    elif env == 'mcp':
        print("🚀 Executing directly with MCP tools...")
        print()
        
        result = extract_intros_auto(
            start_date="2025-10-01",
            end_date="2025-10-09"
        )
        
        if result.get('success'):
            print("✅ Extraction complete!")
            print(f"📁 Results saved to: {result.get('filename')}")
            print(f"📊 Found {result.get('intro_count')} introductions")
        else:
            print(f"⚠️  {result.get('error')}")
        print()
    
    # Step 4: Summary
    print("\nSTEP 4: Summary")
    print("─" * 60)
    print()
    
    if env == 'cursor':
        print("""
The dual-mode system detected you're in Cursor IDE.

✅ What happened:
   - Environment was detected automatically
   - A structured request was generated
   - The request includes all necessary parameters
   - Instructions for Claude Code execution were provided

🎯 What you should do:
   1. Copy the prompt shown above
   2. Open Claude Code
   3. Paste and execute
   4. Get your results!

📚 Learn more:
   - DUAL_MODE_USAGE.md - Complete guide
   - QUICK_REFERENCE.md - Quick commands
   - BRANCH_README.md - Technical details
""")
    elif env == 'mcp':
        print("""
The dual-mode system detected you're in Claude Code.

✅ What happened:
   - Environment was detected automatically
   - MCP tools were called directly
   - Results were processed immediately
   - Reports were generated and saved

🎯 What you got:
   - Markdown report with all intros
   - LinkedIn profiles extracted
   - Welcome messages generated
   - Ready to send to new members!

📚 Learn more:
   - DUAL_MODE_USAGE.md - Complete guide
   - QUICK_REFERENCE.md - Quick commands
   - BRANCH_README.md - Technical details
""")
    
    print()
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║                   DEMONSTRATION COMPLETE                      ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print()


if __name__ == "__main__":
    try:
        demo()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error during demo: {e}")
        sys.exit(1)


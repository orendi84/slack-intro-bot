#!/usr/bin/env python3
"""
Claude Code Test Script
Run this in Claude Code to test the restructured project with MCP tools
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

print("🧪 Testing Restructured Slack Intro Bot in Claude Code")
print("="*60)

# Test 1: Import modules
print("\n1️⃣ Testing imports...")
try:
    from dual_mode import extract_intros_mcp_mode, detect_execution_environment
    print("   ✅ Imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Environment detection
print("\n2️⃣ Testing environment detection...")
env = detect_execution_environment()
print(f"   Environment: {env.upper()}")

# Test 3: Run actual extraction
print("\n3️⃣ Running intro extraction...")
print("   Extracting intros from Oct 1-9, 2025...")

try:
    result = extract_intros_mcp_mode(
        start_date="2025-10-01",
        end_date="2025-10-09"
    )
    
    if result.get('success'):
        print(f"\n   ✅ SUCCESS!")
        print(f"   📁 Report: {result.get('filename')}")
        print(f"   📊 Intros found: {result.get('intro_count')}")
        
        # Show intro details
        if result.get('intros'):
            print(f"\n   👥 People:")
            for intro in result['intros']:
                name = intro.get('real_name', 'Unknown')
                linkedin = intro.get('linkedin_link', 'No LinkedIn')
                print(f"      - {name}: {linkedin}")
    else:
        print(f"\n   ⚠️  Error: {result.get('error')}")
        
except Exception as e:
    print(f"\n   ❌ Extraction failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Test complete!")


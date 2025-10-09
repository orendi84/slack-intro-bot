#!/usr/bin/env python3
"""
Entry point for intro_extraction_api
Maintains backward compatibility
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dual_mode.intro_extraction_api import extract_intros_auto

if __name__ == "__main__":
    # Parse command line arguments
    start_date = sys.argv[1] if len(sys.argv) > 1 else None
    end_date = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = extract_intros_auto(start_date, end_date)
    
    if result.get("mode") == "request_generated":
        print("\n✅ Request generated successfully!")
    elif result.get("success"):
        print(f"\n✅ Extraction complete!")
        print(f"📁 Report saved to: {result['filename']}")
    else:
        print(f"\n❌ Error: {result.get('error')}")


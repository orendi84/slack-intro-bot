#!/usr/bin/env python3
"""
Entry point for daily_intros script
Maintains backward compatibility with the original location
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from daily_intros import main

if __name__ == "__main__":
    main()


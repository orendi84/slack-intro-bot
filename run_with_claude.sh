#!/bin/bash
# This script is meant to be run by Claude Code
# It provides MCP access to the Python script via environment variables

# Export the search results as JSON
export MCP_SLACK_MESSAGES='__PLACEHOLDER__'

# Run the Python script
python3 daily_intros.py "$@"

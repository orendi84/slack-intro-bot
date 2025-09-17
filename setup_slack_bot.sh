#!/bin/bash
"""
Setup script for Slack Intro Bot
Installs dependencies and sets up cron job
"""

echo "🚀 Setting up Slack Intro Bot"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install schedule requests

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x slack_intro_bot.py
chmod +x slack_intro_bot_integrated.py
chmod +x slack_intro_cron.py
chmod +x test_slack_intro_bot.py

# Create output directory
echo "📁 Creating output directory..."
mkdir -p ./welcome_messages

echo "✅ Setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Test the bot: python3 test_slack_intro_bot.py"
echo "2. Run once: python3 slack_intro_cron.py"
echo "3. Set up cron job for daily execution:"
echo "   Add this line to your crontab (crontab -e):"
echo "   0 8 * * * cd $(pwd) && python3 slack_intro_cron.py >> slack_bot.log 2>&1"
echo ""
echo "⚙️  Configuration options:"
echo "   SLACK_CHANNEL_ID - Target Slack channel (set in .env file)"
echo "   OUTPUT_DIR - Directory for output files (default: current directory)"
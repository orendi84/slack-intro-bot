#!/bin/bash
"""
Setup script for Slack Intro Bot cron job
"""

echo "🕐 Setting up Slack Intro Bot cron job"

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "📁 Project directory: $SCRIPT_DIR"

# Check if cron job already exists
CRON_JOB="0 8 * * * cd $SCRIPT_DIR && python3 slack_intro_cron.py >> slack_bot.log 2>&1"
EXISTING_CRON=$(crontab -l 2>/dev/null | grep "slack_intro_cron.py" || true)

if [ -n "$EXISTING_CRON" ]; then
    echo "⚠️  Cron job already exists:"
    echo "   $EXISTING_CRON"
    echo ""
    echo "To update, remove the existing job first:"
    echo "   crontab -e"
    echo "   # Remove the slack_intro_cron.py line"
    echo "   # Then run this script again"
else
    echo "📝 Adding cron job for daily execution at 8:00 AM..."
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ Cron job added successfully!"
    echo ""
    echo "📋 Current crontab:"
    crontab -l | grep slack_intro_cron.py
fi

echo ""
echo "🔧 Configuration:"
echo "   Runs daily at: 8:00 AM"
echo "   Working directory: $SCRIPT_DIR"
echo "   Log file: $SCRIPT_DIR/slack_bot.log"
echo "   Output directory: $SCRIPT_DIR/welcome_messages/"

echo ""
echo "📝 To manage the cron job:"
echo "   View: crontab -l"
echo "   Edit: crontab -e"
echo "   Remove: crontab -r"

echo ""
echo "🧪 To test manually:"
echo "   cd $SCRIPT_DIR"
echo "   python3 slack_intro_cron.py"

echo ""
echo "📊 To monitor logs:"
echo "   tail -f $SCRIPT_DIR/slack_bot.log"
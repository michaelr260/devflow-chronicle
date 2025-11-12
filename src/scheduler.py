"""
Scheduler
Scheduled analysis with optional Slack integration
"""

import schedule
import time
import subprocess
from datetime import datetime
from config import Config

try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_AVAILABLE = True
except ImportError:
    SLACK_AVAILABLE = False
    print("  Slack SDK not available. Install slack-sdk for Slack integration.")


def run_daily_analysis():
    """Run daily analysis and optionally post to Slack"""
    print(f" Running scheduled analysis at {datetime.now()}")

    try:
        # Run analysis
        result = subprocess.run([
            'python', 'src/main.py',
            '.',
            '-f', 'standup',
            '--preset', 'daily'
        ], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"X Analysis failed: {result.stderr}")
            return

        print(" Analysis complete")

        # Post to Slack if enabled
        if Config.SLACK_ENABLED and SLACK_AVAILABLE:
            post_to_slack()

    except Exception as e:
        print(f"X Error: {e}")


def post_to_slack():
    """Post latest standup report to Slack"""
    if not Config.SLACK_TOKEN:
        print("  SLACK_TOKEN not configured")
        return

    try:
        client = WebClient(token=Config.SLACK_TOKEN)

        # Read latest standup report
        standup_file = Config.OUTPUT_DIR / "devflow_standup_latest.md"

        if not standup_file.exists():
            print("  No standup report found")
            return

        with open(standup_file, 'r') as f:
            report = f.read()

        # Post to Slack
        response = client.chat_postMessage(
            channel=Config.SLACK_CHANNEL,
            text=" Daily DevFlow Chronicle Report",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": report[:3000]  # Slack has message limits
                    }
                }
            ]
        )

        print(f" Posted to Slack channel {Config.SLACK_CHANNEL}")

    except SlackApiError as e:
        print(f"X Slack API error: {e.response['error']}")
    except Exception as e:
        print(f"X Error posting to Slack: {e}")


def main():
    """Main scheduler loop"""
    print(" DevFlow Chronicle Scheduler Started")
    print(f" Daily analysis scheduled for 9:00 AM")

    if Config.SLACK_ENABLED:
        print(f" Slack integration enabled → {Config.SLACK_CHANNEL}")

    # Schedule daily at 9 AM
    schedule.every().day.at("09:00").do(run_daily_analysis)

    # Optional: Weekly summary on Mondays at 10 AM
    schedule.every().monday.at("10:00").do(run_weekly_summary)

    print(" Scheduler running. Press Ctrl+C to stop.\n")

    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)


def run_weekly_summary():
    """Run weekly summary analysis"""
    print(" Running weekly summary...")

    subprocess.run([
        'python', 'src/main.py',
        '.',
        '--preset', 'weekly'
    ])


if __name__ == '__main__':
    main()

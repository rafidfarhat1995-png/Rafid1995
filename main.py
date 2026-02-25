"""
Main entry point.

Usage:
  python main.py            # Run one scan immediately
  python main.py --schedule # Run on a nightly schedule (default: 11 PM)
"""

import argparse
import logging
import time
from datetime import datetime

import schedule

from tiktok_scanner import run_tiktok_scan
from reddit_scanner import scan_reddit_economy
from report import generate_report, save_report, print_summary
from config import SCAN_HOUR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_scan():
    """Run a full TikTok + Reddit scan and save the report."""
    logger.info("Starting scan...")

    logger.info("Scanning TikTok...")
    tiktok_data = run_tiktok_scan()

    logger.info("Scanning Reddit...")
    reddit_data = scan_reddit_economy()

    logger.info("Generating report...")
    report = generate_report(tiktok_data, reddit_data)
    json_path, md_path = save_report(report)

    print_summary(report)
    logger.info(f"Report saved: {md_path}")
    logger.info(f"Raw data saved: {json_path}")

    return report


def run_scheduler():
    """Run the scanner every night at the configured hour."""
    scan_time = f"{SCAN_HOUR:02d}:00"
    logger.info(f"Scheduler started. Scans will run daily at {scan_time}.")
    print(f"\nScheduler running. Next scan at {scan_time} every night.")
    print("Press Ctrl+C to stop.\n")

    schedule.every().day.at(scan_time).do(run_scan)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="TikTok & Reddit trend/economy scanner"
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help=f"Run on nightly schedule at {SCAN_HOUR:02d}:00 instead of immediately",
    )
    args = parser.parse_args()

    if args.schedule:
        run_scheduler()
    else:
        run_scan()

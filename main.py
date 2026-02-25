"""
Main entry point.

Usage:
  python main.py            # Run one scan immediately
  python main.py --schedule # Run on a nightly schedule (default: 11 PM)
  python main.py --x-only   # Run only the X AI scanner
"""

import argparse
import logging
import time
from datetime import datetime

import schedule

from tiktok_scanner import run_tiktok_scan
from reddit_scanner import scan_reddit_economy
from x_scanner import scan_x_for_ai
from investment_signals import extract_investment_signals, save_signals
from report import generate_report, save_report, print_summary
from config import SCAN_HOUR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def run_scan():
    """Run a full TikTok + Reddit + X scan with investment signal extraction."""
    logger.info("Starting scan...")

    logger.info("Scanning TikTok...")
    tiktok_data = run_tiktok_scan()

    logger.info("Scanning Reddit...")
    reddit_data = scan_reddit_economy()

    logger.info("Scanning X for AI updates...")
    x_data = scan_x_for_ai()

    logger.info("Extracting investment signals (Chris Camillo lens)...")
    signals = extract_investment_signals(tiktok_data, reddit_data, x_data)
    date_str = datetime.now().strftime("%Y-%m-%d")
    signals_path = save_signals(signals, date_str)
    logger.info(f"Signals saved: {signals_path}")

    logger.info("Generating report...")
    report = generate_report(tiktok_data, reddit_data, x_data, signals)
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
        description="TikTok, Reddit & X trend/economy/AI scanner"
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help=f"Run on nightly schedule at {SCAN_HOUR:02d}:00 instead of immediately",
    )
    parser.add_argument(
        "--x-only",
        action="store_true",
        help="Run only the X AI scanner (quick check)",
    )
    args = parser.parse_args()

    if args.schedule:
        run_scheduler()
    elif args.x_only:
        from report import generate_report, save_report, print_summary
        x_data = scan_x_for_ai()
        report = generate_report({}, {}, x_data)
        _, md_path = save_report(report)
        print_summary(report)
        logger.info(f"X-only report saved: {md_path}")
    else:
        run_scan()

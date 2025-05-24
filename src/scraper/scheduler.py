#!/usr/bin/env python3
"""
Scheduler for running the Devin credit scraper at regular intervals.
"""

import os
import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dotenv import load_dotenv
from scraper import DevinCreditScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scheduler.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def scrape_job():
    """Job to run the scraper."""
    logger.info(f"Running scheduled scrape job at {datetime.now()}")
    scraper = DevinCreditScraper()
    success = scraper.run()
    if success:
        logger.info("Scheduled scrape job completed successfully")
    else:
        logger.error("Scheduled scrape job failed")

def main():
    """Set up and run the scheduler."""
    # Get the scrape interval from environment variables (default to 24 hours)
    interval_hours = int(os.getenv("SCRAPE_INTERVAL_HOURS", "24"))
    
    logger.info(f"Setting up scheduler to run every {interval_hours} hours")
    
    # Create scheduler
    scheduler = BlockingScheduler()
    
    # Add job to run at the specified interval
    scheduler.add_job(
        scrape_job,
        trigger=IntervalTrigger(hours=interval_hours),
        id='scrape_job',
        name='Scrape Devin credit usage',
        replace_existing=True
    )
    
    # Add job to run immediately on startup
    scheduler.add_job(
        scrape_job,
        trigger='date',
        run_date=datetime.now(),
        id='initial_scrape_job',
        name='Initial scrape job'
    )
    
    try:
        logger.info("Starting scheduler")
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    main()

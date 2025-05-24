#!/usr/bin/env python3
"""
Script to run the Devin credit scraper.
"""

import logging
from scraper import DevinCreditScraper

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scraper = DevinCreditScraper()
    success = scraper.run()
    exit(0 if success else 1)

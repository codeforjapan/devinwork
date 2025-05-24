import os
import json
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DevinCreditScraper:
    """
    Scraper for Devin credit usage and limits.
    """
    
    def __init__(self):
        self.url = os.getenv("DEVIN_URL", "https://app.devin.ai/account")
        self.username = os.getenv("DEVIN_USERNAME")
        self.password = os.getenv("DEVIN_PASSWORD")
        self.data_file = os.path.join("data", "credit_data.json")
        
    def setup_driver(self):
        """Set up the Chrome WebDriver with headless options."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def login(self, driver):
        """Log in to the Devin platform."""
        try:
            logger.info("Attempting to log in...")
            
            # Navigate to login page
            driver.get(self.url)
            
            # Wait for login form to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            
            # Fill in login credentials
            driver.find_element(By.ID, "email").send_keys(self.username)
            driver.find_element(By.ID, "password").send_keys(self.password)
            
            # Submit login form
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            
            # Wait for successful login
            WebDriverWait(driver, 10).until(
                EC.url_contains("account")
            )
            
            logger.info("Login successful")
            return True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def extract_credit_data(self, driver):
        """
        Extract credit usage and limits from the account page.
        
        Note: This method needs to be updated with the actual selectors
        once we know the structure of the page.
        """
        try:
            logger.info("Extracting credit data...")
            
            # Wait for the credit information to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Credit')]"))
            )
            
            # Extract credit usage and limits
            # Note: These selectors are placeholders and need to be updated
            # based on the actual page structure
            credit_used = driver.find_element(
                By.XPATH, "//div[contains(@class, 'credit-usage')]"
            ).text
            
            credit_limit = driver.find_element(
                By.XPATH, "//div[contains(@class, 'credit-limit')]"
            ).text
            
            # Extract any other relevant information
            
            # Create data object
            data = {
                "timestamp": datetime.now().isoformat(),
                "credit_used": credit_used,
                "credit_limit": credit_limit,
                # Add other data points as needed
            }
            
            logger.info(f"Extracted data: {data}")
            return data
        except Exception as e:
            logger.error(f"Data extraction failed: {str(e)}")
            return None
    
    def save_data(self, data):
        """Save the scraped data to a JSON file."""
        try:
            # Create data directory if it doesn't exist
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            # Load existing data if available
            existing_data = []
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    existing_data = json.load(f)
            
            # Append new data
            existing_data.append(data)
            
            # Save updated data
            with open(self.data_file, 'w') as f:
                json.dump(existing_data, f, indent=2)
            
            logger.info(f"Data saved to {self.data_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data: {str(e)}")
            return False
    
    def run(self):
        """Run the scraper to extract and save credit data."""
        driver = None
        try:
            logger.info("Starting scraper run...")
            
            # Set up the WebDriver
            driver = self.setup_driver()
            
            # Log in to the platform
            if not self.login(driver):
                logger.error("Scraper run failed due to login failure")
                return False
            
            # Extract credit data
            data = self.extract_credit_data(driver)
            if not data:
                logger.error("Scraper run failed due to data extraction failure")
                return False
            
            # Save the data
            if not self.save_data(data):
                logger.error("Scraper run failed due to data saving failure")
                return False
            
            logger.info("Scraper run completed successfully")
            return True
        except Exception as e:
            logger.error(f"Scraper run failed: {str(e)}")
            return False
        finally:
            # Clean up
            if driver:
                driver.quit()

if __name__ == "__main__":
    scraper = DevinCreditScraper()
    scraper.run()

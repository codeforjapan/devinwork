import os
import json
import logging
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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
        self.login_url = os.getenv("DEVIN_LOGIN_URL", "https://app.devin.ai/login")
        self.usage_url = os.getenv("DEVIN_USAGE_URL", "https://app.devin.ai/settings/usage")
        self.history_url = os.getenv("DEVIN_HISTORY_URL", "https://app.devin.ai/settings/usage?tab=history")
        
        # Authentication credentials
        self.username = os.getenv("DEVIN_USERNAME")
        self.password = os.getenv("DEVIN_PASSWORD")
        
        self.data_file = os.path.join("data", "credit_data.json")
        
    def setup_driver(self):
        """Set up the Chrome WebDriver with headless options."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")  # Set window size for better element visibility
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
    
    def login(self, driver):
        """Log in to the Devin platform."""
        try:
            logger.info("Attempting to log in...")
            
            # Navigate to login page
            driver.get(self.login_url)
            
            # Wait for login form to load - try different possible selectors
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "email"))
                )
                email_field = driver.find_element(By.ID, "email")
                password_field = driver.find_element(By.ID, "password")
            except (NoSuchElementException, TimeoutException):
                # Try alternative selectors
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.NAME, "email"))
                    )
                    email_field = driver.find_element(By.NAME, "email")
                    password_field = driver.find_element(By.NAME, "password")
                except (NoSuchElementException, TimeoutException):
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@type='email']"))
                    )
                    email_field = driver.find_element(By.XPATH, "//input[@type='email']")
                    password_field = driver.find_element(By.XPATH, "//input[@type='password']")
            
            # Fill in login credentials
            email_field.send_keys(self.username)
            password_field.send_keys(self.password)
            
            try:
                submit_button = driver.find_element(By.XPATH, "//button[@type='submit']")
            except NoSuchElementException:
                try:
                    submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Sign in')]")
                except NoSuchElementException:
                    submit_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Log in')]")
            
            submit_button.click()
            
            # Wait for successful login - check for redirect to dashboard or settings
            WebDriverWait(driver, 15).until(
                lambda d: "login" not in d.current_url
            )
            
            logger.info(f"Login successful, current URL: {driver.current_url}")
            return True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def extract_current_usage(self, driver):
        """
        Extract current credit usage from the usage page.
        """
        try:
            logger.info("Navigating to usage page...")
            driver.get(self.usage_url)
            
            # Wait for page to load
            time.sleep(2)
            
            logger.info("Extracting current credit usage data...")
            
            # Wait for the credit information to load - look for "Available ACUs"
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.XPATH, "//*[contains(text(), 'Available ACUs')]")) > 0
            )
            
            available_acus = None
            
            try:
                available_acus_element = driver.find_element(
                    By.XPATH, "//*[contains(text(), 'Available ACUs')]/following-sibling::*"
                )
                available_acus = available_acus_element.text.strip()
            except NoSuchElementException:
                try:
                    available_acus_element = driver.find_element(
                        By.XPATH, "//*[contains(text(), 'Available ACUs')]/.."
                    )
                    # Extract the number from the text
                    text = available_acus_element.text
                    import re
                    match = re.search(r'(\d+)', text)
                    if match:
                        available_acus = match.group(1)
                    else:
                        available_acus = text.replace("Available ACUs", "").strip()
                except NoSuchElementException:
                    logger.warning("Could not find 'Available ACUs' element using standard selectors")
                    driver.save_screenshot("debug_usage_page.png")
                    
                    page_text = driver.find_element(By.TAG_NAME, "body").text
                    logger.info(f"Page text: {page_text}")
                    
                    import re
                    match = re.search(r'Available ACUs[:\s]+(\d+)', page_text)
                    if match:
                        available_acus = match.group(1)
                    else:
                        available_acus = "Unknown"
            
            logger.info(f"Extracted available ACUs: {available_acus}")
            
            # Create data object for current usage
            current_usage = {
                "timestamp": datetime.now().isoformat(),
                "available_acus": available_acus
            }
            
            return current_usage
        except Exception as e:
            logger.error(f"Failed to extract current usage data: {str(e)}")
            driver.save_screenshot("error_usage_page.png")
            return None
    
    def extract_usage_history(self, driver):
        """
        Extract usage history from the history tab.
        """
        try:
            logger.info("Navigating to usage history page...")
            driver.get(self.history_url)
            
            # Wait for page to load
            time.sleep(2)
            
            logger.info("Extracting usage history data...")
            
            # Wait for the history table to load - look for "Session", "Created At", or "ACUs Used"
            WebDriverWait(driver, 10).until(
                lambda d: (
                    len(d.find_elements(By.XPATH, "//*[contains(text(), 'Session')]")) > 0 or
                    len(d.find_elements(By.XPATH, "//*[contains(text(), 'Created At')]")) > 0 or
                    len(d.find_elements(By.XPATH, "//*[contains(text(), 'ACUs Used')]")) > 0
                )
            )
            
            history_rows = []
            
            try:
                table = None
                for potential_table in driver.find_elements(By.TAG_NAME, "table"):
                    if "Session" in potential_table.text or "Created At" in potential_table.text:
                        table = potential_table
                        break
                
                if table:
                    rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row
                    
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        if len(cells) >= 3:  # Ensure we have enough cells
                            session_name = cells[0].text.strip()
                            created_at = cells[1].text.strip()
                            acus_used = cells[2].text.strip()
                            
                            history_rows.append({
                                "session_name": session_name,
                                "created_at": created_at,
                                "acus_used": acus_used
                            })
            except Exception as e:
                logger.warning(f"Could not extract history using table approach: {str(e)}")
                
                try:
                    row_elements = driver.find_elements(
                        By.XPATH, "//div[contains(@class, 'row') or contains(@class, 'item') or contains(@class, 'list-item')]"
                    )
                    
                    for row_element in row_elements:
                        row_text = row_element.text
                        if row_text and ("Session" in row_text or "ACUs" in row_text):
                            import re
                            session_match = re.search(r'Session[:\s]+([^\n]+)', row_text)
                            created_match = re.search(r'Created At[:\s]+([^\n]+)', row_text)
                            acus_match = re.search(r'ACUs Used[:\s]+([^\n]+)', row_text)
                            
                            session_name = session_match.group(1) if session_match else "Unknown"
                            created_at = created_match.group(1) if created_match else "Unknown"
                            acus_used = acus_match.group(1) if acus_match else "Unknown"
                            
                            history_rows.append({
                                "session_name": session_name,
                                "created_at": created_at,
                                "acus_used": acus_used
                            })
                except Exception as e:
                    logger.warning(f"Could not extract history using div approach: {str(e)}")
                    
                    driver.save_screenshot("debug_history_page.png")
                    logger.info(f"Page content: {driver.find_element(By.TAG_NAME, 'body').text}")
            
            logger.info(f"Extracted {len(history_rows)} history rows")
            
            return history_rows
        except Exception as e:
            logger.error(f"Failed to extract usage history data: {str(e)}")
            driver.save_screenshot("error_history_page.png")
            return []
    
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
            
            # Extract current usage data
            current_usage = self.extract_current_usage(driver)
            if not current_usage:
                logger.error("Failed to extract current usage data")
                return False
            
            # Extract usage history data
            usage_history = self.extract_usage_history(driver)
            
            # Combine the data
            data = {
                "timestamp": datetime.now().isoformat(),
                "current_usage": current_usage,
                "usage_history": usage_history
            }
            
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

from playwright.sync_api import sync_playwright
from datetime import datetime
import os
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DOWNLOAD_DIR = os.getcwd()
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Browser configuration
BROWSER_ARGS = [
    '--disable-dev-shm-usage',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-gpu',
    '--disable-software-rasterizer',
    '--disable-extensions',
    '--disable-default-apps',
    '--disable-sync',
    '--disable-translate',
    '--hide-scrollbars',
    '--metrics-recording-only',
    '--mute-audio',
    '--no-first-run',
    '--safebrowsing-disable-auto-update'
]

def download_traffic_view_with_product():
    max_retries = 3
    retry_delay = 5  # seconds

    filename = f"TrafficView_Product_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    final_path = os.path.join(DOWNLOAD_DIR, filename)

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🟢 Attempt {attempt}: Starting Traffic View with Product dimension...")

            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(
                    headless=False,
                    args=BROWSER_ARGS
                )
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    accept_downloads=True
                )
                page = context.new_page()

                # Go to login page
                logger.info("Navigating to login page...")
                page.goto("https://goldie.vrio.app/auth/login")
                page.wait_for_load_state("networkidle")

                # Login with retries
                login_success = False
                for login_attempt in range(3):
                    try:
                        logger.info(f"Login attempt {login_attempt + 1}...")
                        page.get_by_placeholder("email").click()
                        page.get_by_placeholder("email").fill("team123@team123proton.com")
                        page.get_by_placeholder("password").click()
                        page.get_by_placeholder("password").fill("GFTeam123!@")
                        page.get_by_role("button", name="Login").click()
                        page.wait_for_load_state("networkidle")
                        login_success = True
                        break
                    except Exception as e:
                        logger.error(f"Login attempt {login_attempt + 1} failed: {e}")
                        if login_attempt < 2:
                            page.reload()
                            time.sleep(2)
                
                if not login_success:
                    raise Exception("Failed to login after multiple attempts")

                # Navigate to Analytics
                logger.info("Navigating to Analytics...")
                page.get_by_role("link", name=" Analytics").click()
                page.wait_for_load_state("networkidle")

                # Go to Saved Reports tab
                logger.info("Opening Saved Reports...")
                page.get_by_role("tab", name="Saved Reports").click()
                page.wait_for_load_state("networkidle")

                # Open Traffic View (not Traffic View 1)
                logger.info("Opening Traffic View...")
                page.get_by_role("link", name=" Traffic View").click()
                page.wait_for_load_state("networkidle")
                time.sleep(3)  # Wait for report to load

                # Add Product (tracking2) dimension
                logger.info("Adding Product (tracking2) dimension...")
                page.get_by_role("link", name="Add Dimension").click()
                page.wait_for_timeout(2000)
                
                page.get_by_role("textbox", name="Select Next Dimension").click()
                page.wait_for_timeout(1000)
                
                page.get_by_role("option", name="Product (tracking2)").click()
                page.wait_for_load_state("networkidle")
                time.sleep(5)  # Wait for report to refresh with new dimension

                # Export the report
                logger.info("Initiating download...")
                more_options = page.get_by_role("button", name="More Options ")
                more_options.wait_for(state="visible", timeout=10000)
                more_options.click()
                page.wait_for_timeout(2000)
                
                with page.expect_download(timeout=30000) as download_info:
                    logger.info("Clicking Export Report...")
                    export_link = page.get_by_role("link", name="Export Report")
                    export_link.wait_for(state="visible", timeout=10000)
                    export_link.click()
                
                download = download_info.value
                download.save_as(final_path)
                logger.info(f"✅ File downloaded and saved as: {final_path}")

                context.close()
                browser.close()
                return final_path  # Return the file path on success

        except Exception as e:
            logger.error(f"Attempt {attempt} failed: {str(e)}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All retry attempts failed")
                raise

def main():
    try:
        downloaded_file = download_traffic_view_with_product()
        print(f"✅ Successfully downloaded: {downloaded_file}")
    except Exception as e:
        print(f"❌ Failed to download Traffic View report: {e}")

if __name__ == "__main__":
    main() 
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import os
import asyncio
import platform

# Configuration
DOWNLOAD_DIR = os.getcwd()
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
IS_SERVER = platform.system() == "Linux"

async def Playwright_GF_Affiliate_PnL_async(playwright, current_date):
    max_retries = 3
    retry_delay = 5  # seconds

    filename = f"GF_Affiliate_PnL_Export_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    final_path = os.path.join(DOWNLOAD_DIR, filename)

    for attempt in range(1, max_retries + 1):
        browser = None
        context = None
        try:
            print(f"🟢 Attempt {attempt}: Starting GF Affiliate P&L data extraction...")
            
            browser = await playwright.chromium.launch(
                headless=False,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--remote-debugging-port=9222',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-software-rasterizer',
                    '--disable-default-apps',
                    '--disable-sync',
                    '--disable-translate',
                    '--hide-scrollbars',
                    '--metrics-recording-only',
                    '--mute-audio',
                    '--no-first-run',
                    '--safebrowsing-disable-auto-update'
                ] if IS_SERVER else [
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-gpu'
                ]
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                accept_downloads=True
            )
            page = await context.new_page()

            # Go directly to the report page
            print("Navigating to GF Affiliate P&L report page...")
            await page.goto("https://goldie.vrio.app/report/run/106/171", wait_until="networkidle")

            # Login with retry logic
            login_success = False
            for login_attempt in range(3):
                try:
                    print(f"Login attempt {login_attempt + 1}...")
                    await page.get_by_placeholder("email").click()
                    await page.get_by_placeholder("email").fill("team123@team123proton.com")
                    await page.get_by_placeholder("password").click()
                    await page.get_by_placeholder("password").fill("GFTeam123!@")
                    await page.get_by_role("button", name="Login").click()
                    await page.wait_for_load_state("networkidle")
                    login_success = True
                    break
                except Exception as e:
                    print(f"Login attempt {login_attempt + 1} failed: {e}")
                    if login_attempt < 2:
                        await page.reload()
                        await page.wait_for_load_state("networkidle", timeout=10000)
            
            if not login_success:
                raise Exception("Failed to login after multiple attempts")

            # Ensure we're on the report page after login
            print("Ensuring we're on the report page after login...")
            await page.goto("https://goldie.vrio.app/report/run/106/171", wait_until="networkidle")
            
            # Wait for report to fully load with proper detection
            print("Waiting for report to load completely...")
            
            # Wait for More Options button to appear (indicates page is loaded)
            try:
                await page.get_by_role("button", name="More Options ").wait_for(state="visible", timeout=20000)
                print("✅ More Options button found - page structure loaded")
            except Exception as e:
                print(f"⚠️ More Options button not found: {e}")
            
            # Wait for any loading spinners to disappear
            loading_selectors = [
                ".loading", ".spinner", "[class*='loading']", "[class*='spinner']", ".fa-spinner",
                ".loading-overlay", ".progress", "[class*='progress']"
            ]
            for selector in loading_selectors:
                try:
                    await page.wait_for_selector(selector, state="hidden", timeout=3000)
                    print(f"✅ Loading indicator {selector} disappeared")
                except:
                    pass  # Loading indicator might not exist
            
            # Wait for report data elements to be visible with better detection
            print("Waiting for report data to appear...")
            data_selectors = [
                "table tbody tr", "table", ".report-table", ".data-table", 
                "[class*='table']", ".chart", "[class*='chart']", 
                ".report-content", "[class*='report']", ".data-row"
            ]
            
            data_found = False
            for selector in data_selectors:
                try:
                    await page.wait_for_selector(selector, state="visible", timeout=8000)
                    print(f"✅ Report data element found: {selector}")
                    data_found = True
                    break
                except:
                    continue
            
            if not data_found:
                print("⚠️ Warning: Could not find specific data elements, proceeding anyway...")
            
            # Wait for network to be idle (all requests completed)
            await page.wait_for_load_state("networkidle", timeout=10000)
            print("✅ Report loading complete")

            # --- Date Range Selection (Human-like) ---
            print(f"Selecting date range: {current_date}")
            try:
                # Look for date input field (common selectors)
                date_selectors = [
                    "#rb_date_range",
                    "input[placeholder*='date']",
                    "input[name*='date']",
                    ".date-input",
                    "[data-testid='date-input']"
                ]
                
                date_input_found = False
                for selector in date_selectors:
                    try:
                        date_input = page.locator(selector)
                        await date_input.wait_for(state="visible", timeout=5000)
                        await date_input.click()
                        await date_input.fill("")  # Clear the input field
                        await date_input.type(current_date, delay=100)  # Human-like typing
                        await date_input.press("Tab")  # Move focus away
                        
                        # Verify the date was actually set
                        try:
                            input_value = await date_input.input_value()
                            if current_date in input_value or input_value in current_date:
                                print(f"✅ Date input successfully filled: {input_value}")
                            else:
                                print(f"⚠️ Date may not have been set correctly. Expected: {current_date}, Got: {input_value}")
                        except:
                            print(f"✅ Date input filled with: {current_date}")
                        
                        date_input_found = True
                        break
                    except Exception as e:
                        print(f"Date selector {selector} failed: {e}")
                        continue
                
                if not date_input_found:
                    print("⚠️ Warning: Could not find date input field, proceeding with default date range")
                else:
                    # Wait for date processing and data refresh (only if date was changed)
                    print("Waiting for date selection to process...")
                    
                    # Wait for any loading indicators to appear and disappear after date change
                    try:
                        # Check if loading appears first
                        await page.wait_for_selector(".loading, .spinner, [class*='loading']", state="visible", timeout=2000)
                        print("🔄 Date processing detected")
                        # Then wait for it to disappear
                        await page.wait_for_selector(".loading, .spinner, [class*='loading']", state="hidden", timeout=10000)
                        print("✅ Date processing loading complete")
                    except:
                        # If no loading indicator, just wait for network idle
                        await asyncio.sleep(2)  # Brief wait for any processing to start
                    
                    # Wait for data to refresh after date change
                    await page.wait_for_load_state("networkidle", timeout=10000)
                    print("✅ Date processing complete")
                
            except Exception as e:
                print(f"⚠️ Date selection failed: {e}, proceeding with default range")

            # --- Final check before export ---
            print("Performing final checks before download...")
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            # --- Export the report ---
            print("Initiating download...")
            
            # Click More Options and wait for menu to appear
            await page.get_by_role("button", name="More Options ").click()
            
            # Wait for export option to be visible and clickable
            export_link = page.get_by_role("link", name="Export Report")
            await export_link.wait_for(state="visible", timeout=10000)
            
            # Ensure the export link is fully loaded and clickable
            await export_link.wait_for(state="attached", timeout=5000)
            
            async with page.expect_download(timeout=30000) as download_info:
                print("Clicking Export Report...")
                await export_link.click()
            
            download = await download_info.value
            await download.save_as(final_path)
            print(f"✅ File downloaded and saved as: {final_path}")
            
            # Verify file is not empty
            if os.path.exists(final_path):
                file_size = os.path.getsize(final_path)
                print(f"📊 Downloaded file size: {file_size} bytes")
                if file_size < 100:  # Very small file might indicate empty/error
                    print("⚠️ Warning: Downloaded file is very small, might be empty or contain errors")
                else:
                    print("✅ File appears to have data")
            else:
                print("❌ Warning: Downloaded file not found")

            print("✅ GF Affiliate P&L extraction completed successfully.")
            return final_path  # Success, exit the retry loop

        except Exception as e:
            print(f"Attempt {attempt} failed: {str(e)}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                print("All retry attempts failed")
                raise
        finally:
            if context:
                try:
                    await context.close()
                except:
                    pass
            if browser:
                try:
                    await browser.close()
                except:
                    pass

async def main():
    # Use specific test date range
    current_date = "06/13/2025 - 06/26/2025"
    
    print(f"🚀 Starting GF Affiliate P&L extraction for date: {current_date}")
    
    try:
        async with async_playwright() as playwright:
            downloaded_file = await Playwright_GF_Affiliate_PnL_async(playwright, current_date)
            print(f"✅ Successfully downloaded: {downloaded_file}")
    except Exception as e:
        print(f"❌ Failed to extract GF Affiliate P&L data: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 
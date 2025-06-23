import os
import time
import asyncio
from playwright.async_api import async_playwright
import platform

# Browser configuration for server environment
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

# Configuration
DOWNLOAD_DIR = os.getcwd()
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

IS_SERVER = platform.system() == "Linux"

if IS_SERVER:
    # Set virtual display for Playwright headless=False
    os.environ['DISPLAY'] = ':99'
    os.makedirs("logs", exist_ok=True)
    os.makedirs("downloads", exist_ok=True)
    print("✅ Server environment configured")
    print(f"✅ Display set to: {os.environ.get('DISPLAY')}")
    print(f"✅ Current directory: {os.getcwd()}")
else:
    print("🖥️ Running on local machine")

async def test_playwright_gf():
    from datetime import datetime
    import os
    import time

    max_retries = 3
    retry_delay = 5  # seconds

    filename = f"EOM_Fcast_{datetime.now().strftime('%Y-%m-%d')}.csv"
    final_path = os.path.join(DOWNLOAD_DIR, filename)

    print(f"🎯 Target file: {final_path}")

    for attempt in range(1, max_retries + 1):
        try:
            print(f"🟢 Attempt {attempt}: Starting EOM Playwright automation...")

            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=False,
                    args=BROWSER_ARGS
                )
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    accept_downloads=True
                )
                page = await context.new_page()

                # Go to login page
                print("Navigating to login page...")
                await page.goto("https://goldie.vrio.app/auth/login", timeout=30000)
                print("✅ Login page loaded")

                # Login with retries
                login_success = False
                for login_attempt in range(3):
                    try:
                        print(f"Login attempt {login_attempt + 1}...")
                        await page.get_by_placeholder("email").click(timeout=10000)
                        await page.get_by_placeholder("email").fill("team123@team123proton.com")
                        await page.get_by_placeholder("password").click(timeout=10000)
                        await page.get_by_placeholder("password").fill("GFTeam123!@")
                        await page.get_by_role("button", name="Login").click(timeout=10000)
                        await page.wait_for_load_state("networkidle", timeout=20000)
                        login_success = True
                        print("✅ Login successful")
                        break
                    except Exception as e:
                        print(f"❌ Login attempt {login_attempt + 1} failed: {e}")
                        if login_attempt < 2:
                            await page.reload()
                            time.sleep(2)
                if not login_success:
                    raise Exception("Failed to login after multiple attempts")

                # Navigate to Analytics
                print("Navigating to Analytics...")
                analytics_link = page.get_by_role("link", name=" Analytics")
                await analytics_link.wait_for(state="visible", timeout=10000)
                await analytics_link.click()
                await page.wait_for_load_state("networkidle", timeout=20000)
                print("✅ Analytics page loaded")

                # Go to Saved Reports tab
                print("Opening Saved Reports...")
                saved_reports_tab = page.get_by_role("tab", name="Saved Reports")
                await saved_reports_tab.wait_for(state="visible", timeout=10000)
                await saved_reports_tab.click()
                await page.wait_for_load_state("networkidle", timeout=20000)
                print("✅ Saved Reports tab opened")

                # Open EOM-View
                print("Opening EOM-View...")
                eom_view_link = page.get_by_role("link", name="EOM Fee Fcast")
                await eom_view_link.wait_for(state="visible", timeout=10000)
                await eom_view_link.click()
                await page.wait_for_load_state("networkidle", timeout=20000)
                print("✅ EOM Fee Fcast report opened")

                # Export the report
                print("Initiating download...")
                more_options = page.get_by_role("button", name="More Options ")
                await more_options.wait_for(state="visible", timeout=10000)
                await more_options.click()
                await page.wait_for_timeout(2000)
                print("✅ More Options clicked")

                async with page.expect_download(timeout=30000) as download_info:
                    print("Pressing Export Report...")
                    export_link = page.get_by_role("link", name="Export Report")
                    await export_link.wait_for(state="visible", timeout=10000)
                    await export_link.click()

                download = await download_info.value
                await download.save_as(final_path)
                print(f"✅ File downloaded and saved as: {final_path}")

                # Verify file exists
                if os.path.exists(final_path):
                    file_size = os.path.getsize(final_path)
                    print(f"✅ File verification: {final_path} exists, size: {file_size} bytes")
                else:
                    print(f"❌ File verification failed: {final_path} does not exist")

                await context.close()
                await browser.close()
                
                print("🎉 SUCCESS: Playwright automation completed successfully!")
                return True  # Success, exit the retry loop

        except Exception as e:
            print(f"❌ Attempt {attempt} failed: {str(e)}")
            if attempt < max_retries:
                print(f"⏳ Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("❌ All retry attempts failed")
                return False

if __name__ == "__main__":
    print("🚀 Starting Goldfinger Playwright Test...")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🖥️ Platform: {platform.system()}")
    
    # Run the async function
    result = asyncio.run(test_playwright_gf())
    
    if result:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!") 
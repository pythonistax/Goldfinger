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

DOWNLOAD_DIR = os.getcwd()
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

IS_SERVER = platform.system() == "Linux"

if IS_SERVER:
    os.environ['DISPLAY'] = ':99'
    os.makedirs("logs", exist_ok=True)
    os.makedirs("downloads", exist_ok=True)
    print("✅ Server environment configured")
    print(f"✅ Display set to: {os.environ.get('DISPLAY')}")
    print(f"✅ Current directory: {os.getcwd()}")
else:
    print("🖥️ Running on local machine")

async def test_playwright_gf_tv():
    from datetime import datetime
    import os
    import time

    max_retries = 3
    retry_delay = 5  # seconds

    filename = f"Project5_{datetime.now().strftime('%Y-%m-%d')}.csv"
    final_path = os.path.join(DOWNLOAD_DIR, filename)

    print(f"🎯 Target file: {final_path}")

    for attempt in range(1, max_retries + 1):
        try:
            print(f"🟢 Attempt {attempt}: Starting TV Playwright automation...")

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
                print("✅ Saved Reports tab loaded")

                # Open Traffic View 1
                print("Opening Traffic View 1...")
                traffic_view_selectors = [
                    page.get_by_role("link", name=" Traffic View 1"),
                    page.get_by_text("Traffic View 1"),
                    page.locator("text=Traffic View 1")
                ]
                traffic_view_found = False
                for selector in traffic_view_selectors:
                    try:
                        await selector.wait_for(state="visible", timeout=5000)
                        await selector.click()
                        traffic_view_found = True
                        break
                    except Exception as e:
                        print(f"Selector {selector} failed: {e}")
                        continue
                if not traffic_view_found:
                    raise Exception("Could not find Traffic View 1 element")
                await page.wait_for_load_state("networkidle")
                await page.wait_for_timeout(5000)
                print("✅ Traffic View 1 loaded")

                # Export the report
                print("Initiating download...")
                more_options = page.get_by_role("button", name="More Options ")
                await more_options.wait_for(state="visible", timeout=10000)
                await more_options.click()
                await page.wait_for_timeout(2000)
                async with page.expect_download(timeout=30000) as download_info:
                    print("Pressed Export Report")
                    export_link = page.get_by_role("link", name="Export Report")
                    await export_link.wait_for(state="visible", timeout=10000)
                    await export_link.click()
                download = await download_info.value
                await download.save_as(final_path)
                print(f"✅ File downloaded and saved as: {final_path}")
                await context.close()
                await browser.close()
                return  # Success, exit the retry loop
        except Exception as e:
            print(f"Attempt {attempt} failed: {str(e)}")
            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("All retry attempts failed")
                raise

if __name__ == "__main__":
    asyncio.run(test_playwright_gf_tv()) 
#!/usr/bin/env python3
"""
Test script for GF Project 6 Playwright functionality only
This script tests just the Playwright code to ensure it downloads the correct files
"""

import os
import time
import sys
import asyncio
from playwright.sync_api import sync_playwright

# Configuration
DOWNLOAD_DIR = "downloads"
BROWSER_ARGS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    '--disable-web-security',
    '--disable-extensions',
    '--disable-plugins',
    '--remote-debugging-port=9222',
    '--disable-features=VizDisplayCompositor'
]

def test_playwright_gf_project_6():
    """Test the Playwright function for GF Project 6"""
    print("🧪 Starting GF Project 6 Playwright Test...")
    
    # Define expected files
    filename1 = "S1R1A1.csv"
    final_path1 = os.path.join(DOWNLOAD_DIR, filename1)
    filename2 = "S1R2+A1.csv"
    final_path2 = os.path.join(DOWNLOAD_DIR, filename2) 
    filename3 = "S2R1A1.csv"
    final_path3 = os.path.join(DOWNLOAD_DIR, filename3)
    filename4 = "S2R2+A1.csv"
    final_path4 = os.path.join(DOWNLOAD_DIR, filename4)

    # Check if downloads directory exists
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        print(f"📁 Created downloads directory: {DOWNLOAD_DIR}")

    try:
        # Ensure event loop is running
        if not asyncio.get_event_loop().is_running():
            asyncio.set_event_loop(asyncio.new_event_loop())
            
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

            # --- First Report (S1R1A1) - GF URL ---
            print("Navigating to first report page (S1R1A1)...")
            page.goto("https://goldie.vrio.app/report/run/115/19", wait_until="networkidle")

            login_success = False
            for login_attempt in range(3):
                try:
                    print(f"Login attempt {login_attempt + 1}...")
                    page.get_by_placeholder("email").click()
                    page.get_by_placeholder("email").fill("team123@team123proton.com")
                    page.get_by_placeholder("password").click()
                    page.get_by_placeholder("password").fill("GFTeam123!@")
                    page.get_by_role("button", name="Login").click()
                    page.wait_for_load_state("networkidle")
                    login_success = True
                    break
                except Exception as e:
                    print(f"Login attempt {login_attempt + 1} failed: {e}")
                    if login_attempt < 2:
                        time.sleep(2)
            if not login_success:
                raise Exception("Failed to login after multiple attempts")

            # Ensure on report page after login
            print("Ensuring we are on the first report page after login...")
            page.goto("https://goldie.vrio.app/report/run/115/19", wait_until="networkidle")

            print("Waiting for 'More Options' button (S1R1A1)...")
            more_options = page.get_by_role("button", name="More Options ")
            more_options.wait_for(state="visible", timeout=10000)
            more_options.click()
            page.wait_for_timeout(2000)

            print("Initiating download for S1R1A1...")
            with page.expect_download(timeout=30000) as download_info:
                export_link = page.get_by_role("link", name="Export Report")
                export_link.wait_for(state="visible", timeout=10000)
                export_link.click()
            download = download_info.value
            download.save_as(final_path1)
            print(f"✅ File downloaded and saved as: {final_path1}")

            # --- Second Report (S1R2+A1) - GF URL ---
            print("Navigating to second report page (S1R2+A1)...")
            page.goto("https://goldie.vrio.app/report/run/116/19", wait_until="networkidle")

            print("Waiting for 'More Options' button (S1R2+A1)...")
            more_options = page.get_by_role("button", name="More Options ")
            more_options.wait_for(state="visible", timeout=10000)
            more_options.click()
            page.wait_for_timeout(2000)

            print("Initiating download for S1R2+A1...")
            with page.expect_download(timeout=30000) as download_info2:
                export_link = page.get_by_role("link", name="Export Report")
                export_link.wait_for(state="visible", timeout=10000)
                export_link.click()
            download2 = download_info2.value
            download2.save_as(final_path2)
            print(f"✅ File downloaded and saved as: {final_path2}")

            # --- Third Report (S2R1A1) - GF URL ---
            print("Navigating to third report page (S2R1A1)...")
            page.goto("https://goldie.vrio.app/report/run/117/19", wait_until="networkidle")

            print("Waiting for 'More Options' button (S2R1A1)...")
            more_options = page.get_by_role("button", name="More Options ")
            more_options.wait_for(state="visible", timeout=10000)
            more_options.click()
            page.wait_for_timeout(2000)

            print("Initiating download for S2R1A1...")
            with page.expect_download(timeout=30000) as download_info3:
                export_link = page.get_by_role("link", name="Export Report")
                export_link.wait_for(state="visible", timeout=10000)
                export_link.click()
            download3 = download_info3.value
            download3.save_as(final_path3)
            print(f"✅ File downloaded and saved as: {final_path3}")

            # --- Fourth Report (S2R2+A1) - GF URL ---
            print("Navigating to fourth report page (S2R2+A1)...")
            page.goto("https://goldie.vrio.app/report/run/118/19", wait_until="networkidle")

            print("Waiting for 'More Options' button (S2R2+A1)...")
            more_options = page.get_by_role("button", name="More Options ")
            more_options.wait_for(state="visible", timeout=10000)
            more_options.click()
            page.wait_for_timeout(2000)

            print("Initiating download for S2R2+A1...")
            with page.expect_download(timeout=30000) as download_info4:
                export_link = page.get_by_role("link", name="Export Report")
                export_link.wait_for(state="visible", timeout=10000)
                export_link.click()
            download4 = download_info4.value
            download4.save_as(final_path4)
            print(f"✅ File downloaded and saved as: {final_path4}")

            context.close()
            browser.close()
            return True

    except Exception as e:
        print(f"❌ Playwright test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 GF Project 6 Playwright Test Script")
    print("=" * 60)
    
    # Test Playwright functionality
    success = test_playwright_gf_project_6()
    
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"   Playwright Test: {'✅ PASSED' if success else '❌ FAILED'}")
    
    if success:
        print("\n🎉 All tests passed! Project 6 Playwright is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Please check the output above.")
        sys.exit(1)
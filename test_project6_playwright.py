#!/usr/bin/env python3
"""
Test script for GF Project 6 Playwright functionality
This script tests the Playwright code to ensure it downloads the correct files
"""

import os
import time
import sys
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
    expected_files = [
        "S1R1A1.csv",
        "S1R2+A1.csv", 
        "S2R1A1.csv",
        "S2R2+A1.csv"
    ]
    
    # Check if downloads directory exists
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        print(f"📁 Created downloads directory: {DOWNLOAD_DIR}")
    
    try:
        with sync_playwright() as playwright:
            print("🌐 Launching browser...")
            browser = playwright.chromium.launch(
                headless=False,  # Set to True for headless mode
                args=BROWSER_ARGS
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                accept_downloads=True
            )
            page = context.new_page()
            
            # Test URLs
            urls = [
                ("S1R1A1", "https://goldie.vrio.app/report/run/115/19"),
                ("S1R2+A1", "https://goldie.vrio.app/report/run/116/19"),
                ("S2R1A1", "https://goldie.vrio.app/report/run/117/19"),
                ("S2R2+A1", "https://goldie.vrio.app/report/run/118/19")
            ]
            
            for report_name, url in urls:
                print(f"\n📊 Testing {report_name}...")
                print(f"   URL: {url}")
                
                try:
                    # Navigate to the report page
                    print(f"   Navigating to {report_name}...")
                    page.goto(url, wait_until="networkidle")
                    
                    # Check if we need to login
                    try:
                        email_field = page.get_by_placeholder("email")
                        if email_field.is_visible(timeout=5000):
                            print(f"   Logging in for {report_name}...")
                            email_field.click()
                            email_field.fill("aibot123@autogmail.com")
                            page.get_by_placeholder("password").click()
                            page.get_by_placeholder("password").fill("Auto123!")
                            page.get_by_role("button", name="Login").click()
                            page.wait_for_load_state("networkidle")
                            
                            # Navigate back to the report page after login
                            page.goto(url, wait_until="networkidle")
                    except Exception as e:
                        print(f"   Login not required or failed: {e}")
                    
                    # Check for More Options button
                    try:
                        more_options = page.get_by_role("button", name="More Options ")
                        if more_options.is_visible(timeout=10000):
                            print(f"   ✅ More Options button found for {report_name}")
                        else:
                            print(f"   ⚠️ More Options button not found for {report_name}")
                    except Exception as e:
                        print(f"   ❌ Error finding More Options button: {e}")
                    
                    # Check for Export Report link
                    try:
                        export_link = page.get_by_role("link", name="Export Report")
                        if export_link.is_visible(timeout=5000):
                            print(f"   ✅ Export Report link found for {report_name}")
                        else:
                            print(f"   ⚠️ Export Report link not found for {report_name}")
                    except Exception as e:
                        print(f"   ❌ Error finding Export Report link: {e}")
                    
                    # Take a screenshot for debugging
                    screenshot_path = os.path.join(DOWNLOAD_DIR, f"{report_name}_screenshot.png")
                    page.screenshot(path=screenshot_path)
                    print(f"   📸 Screenshot saved: {screenshot_path}")
                    
                except Exception as e:
                    print(f"   ❌ Error processing {report_name}: {e}")
            
            context.close()
            browser.close()
            
    except Exception as e:
        print(f"❌ Playwright test failed: {e}")
        return False
    
    print("\n✅ Playwright test completed!")
    print("\n📁 Checking downloaded files...")
    
    # Check what files were actually downloaded
    downloaded_files = os.listdir(DOWNLOAD_DIR)
    print(f"Files in downloads directory: {downloaded_files}")
    
    # Check for expected files
    for expected_file in expected_files:
        file_path = os.path.join(DOWNLOAD_DIR, expected_file)
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {expected_file}: {file_size:,} bytes")
        else:
            print(f"❌ {expected_file}: Not found")
    
    return True

def test_notebook_processing():
    """Test the notebook processing functionality"""
    print("\n🧪 Testing notebook processing...")
    
    # Check if the notebook exists
    notebook_path = "GF_Project_6_serv.ipynb"
    if not os.path.exists(notebook_path):
        print(f"❌ Notebook not found: {notebook_path}")
        return False
    
    print(f"✅ Notebook found: {notebook_path}")
    
    # Check if required CSV files exist
    required_files = ["S1R1A1.csv", "S1R2+A1.csv", "S2R1A1.csv", "S2R2+A1.csv"]
    missing_files = []
    
    for file in required_files:
        file_path = os.path.join(DOWNLOAD_DIR, file)
        if os.path.exists(file_path):
            print(f"✅ {file}: Found")
        else:
            print(f"❌ {file}: Missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️ Missing files for notebook processing: {missing_files}")
        return False
    
    print("✅ All required files found for notebook processing")
    return True

if __name__ == "__main__":
    print("🚀 GF Project 6 Test Script")
    print("=" * 50)
    
    # Test Playwright functionality
    playwright_success = test_playwright_gf_project_6()
    
    # Test notebook processing
    notebook_success = test_notebook_processing()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Playwright Test: {'✅ PASSED' if playwright_success else '❌ FAILED'}")
    print(f"   Notebook Test: {'✅ PASSED' if notebook_success else '❌ FAILED'}")
    
    if playwright_success and notebook_success:
        print("\n🎉 All tests passed! Project 6 is ready to use.")
    else:
        print("\n⚠️ Some tests failed. Please check the output above.")
        sys.exit(1) 
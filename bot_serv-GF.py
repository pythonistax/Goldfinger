import os
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from telegram import Update, Bot
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
import shutil
import sys
import logging
from typing import Any
import papermill as pm
import re
import pytz
import datetime
import zipfile
import tempfile
import glob
import time
import asyncio
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
import requests
from playwright.sync_api import sync_playwright, Playwright
from playwright.async_api import async_playwright
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import traceback
import platform

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DOWNLOAD_DIR = os.getcwd()
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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

IS_SERVER = platform.system() == "Linux"

if IS_SERVER:
    # Set virtual display for Playwright headless=False
    os.environ['DISPLAY'] = ':99'
    os.makedirs("logs", exist_ok=True)
    os.makedirs("downloads", exist_ok=True)
    print("✅ Server environment configured")
    print(f"✅ Display set to: {os.environ.get('DISPLAY')}")
    print(f"✅ Current directory: {os.getcwd()}")

    # Add file handler for server logging
    file_handler = logging.FileHandler('logs/bot_server.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logging.getLogger().addHandler(file_handler)
    print("✅ Server logging configured")
else:
    print("🖥️ Running on local machine")

# ----------------------------------------------------------------- Configuration -------------------------------------------------------------------------------------------------------------
# Configure executors
executors = {
    'default': ThreadPoolExecutor(1)
}

# Create scheduler
scheduler = AsyncIOScheduler(executors=executors)

group_chats_allowed = [
    "bot test nocas",
    "EOM [GF]",
    "Valerius nocas",
    "TV [GF]",
    "AFF P/L [GF]",
    "DEPREC [GF]"
]

ORIGINAL_FILES = [
    '.git',
    'bot_serv-GF.py',
    'bot_serv-KT_GF_base.py',
    'convert_notebook.py',
    'downloads',
    'GF_EOM-Rubric.xlsx',
    'GF_Project_1.ipynb',
    'GF_Project_3.ipynb',
    'GF_Project_5.ipynb',
    'Goldie call',
    'logs',
    'GWID_local_GF.xlsx',
    'Master_Reconciliation_GF.xlsx',
    'NEF_Project_5_serv.ipynb',
    'README.md',
    'requirements.txt',
    'server_operations_guide.txt',
    'tv_database_gf.xlsx',
]

# ----------------------------------------------------------------- General Functions -------------------------------------------------------------------------------------------------------------
def delete_unwanted_files(current_dir, files_to_keep):
    """
    Deletes all files in the specified directory except those listed in files_to_keep.
    
    Args:
        current_dir (str): The directory path where files will be deleted
        files_to_keep (list): List of filenames to preserve
    """
    # Get a list of all files in the current directory
    try:
        all_files = os.listdir(current_dir)
    except Exception as e:
        print(f"⚠️ Error accessing directory {current_dir}: {e}")
        return
    
    # Count tracking variables
    deleted_count = 0
    error_count = 0
    
    # Loop through all files and delete them if they are not in the files_to_keep list
    for filename in all_files:
        file_path = os.path.join(current_dir, filename)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue
            
        # Delete file if not in the keep list
        if filename not in files_to_keep:
            try:
                os.remove(file_path)
                print(f"🧽 Deleted file: {filename}")
                deleted_count += 1
            except Exception as e:
                print(f"⚠️ Failed to delete file: {filename} - {e}")
                error_count += 1
    
    # Print summary
    print(f"\n✅ Cleanup complete: {deleted_count} files deleted, {error_count} errors occurred")
    print(f"🔒 Preserved files: {', '.join(files_to_keep)}")

# ----------------------------------------------------------------- GOLDFINGER PROJECT 1 (DEPREC) -------------------------------------------------------------------------------------------------------------

def clean_p1_message_gf(message: str) -> str:
    if message is None:
        return "No message to display"
        
    keywords = ["Report", "Repeat", "New", "From", "Deposited", "deposited"]
    lines = message.strip().split('\n')
    cleaned_lines = []

    for line in lines:
        if any(keyword in line for keyword in keywords):
            cleaned_lines.append(f"<b>{line}</b>")
        else:
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)

def run_gf_project_1_notebook():
    notebook_path = "GF_Project_1.ipynb"
    output_path = "GF_Project_1_serv_output.ipynb"

    # Add file existence check
    if not os.path.exists(notebook_path):
        error_msg = f"Notebook file {notebook_path} not found"
        print(f"❌ {error_msg}")
        return False, error_msg, None

    try:
        pm.execute_notebook(
            notebook_path,
            output_path,
            kernel_name="python3",
            cwd=os.getcwd()
        )
        print("✅ GF Project 1 notebook executed successfully.")

        # Extract the clean_message from the code cell that prints it
        message = None
        try:
            with open(output_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)

            for cell in nb['cells']:
                if cell['cell_type'] == 'code':
                    source = cell.get('source', '')
                    if 'print(clean_message)' in source or 'print("--- Filtered Message ---")' in source:
                        for output in cell.get('outputs', []):
                            if 'text' in output:
                                message = output['text'].strip()
                                break
                            elif 'data' in output and 'text/plain' in output['data']:
                                message = output['data']['text/plain'].strip()
                                break
                if message:
                    break

            if message:
                print(f"✅ Message extracted:\n{message}")
            else:
                print("⚠️ Warning: No clean_message found in any print cell.")
                message = "No message was generated from the notebook execution."

        except Exception as e:
            print(f"❌ Error extracting message from notebook: {str(e)}")
            message = f"Error extracting message: {str(e)}"

        return True, output_path, message

    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"❌ GF Project 1 notebook failed:\n{traceback_str}")
        return False, traceback_str, None

async def handle_Project_1_GF(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    file_name = update.message.document.file_name if update.message.document else None

    print(f"✅ Project 1 handler received file: {file_name}")

    try:
        # Create tmp directory if it doesn't exist
        os.makedirs("tmp", exist_ok=True)
        current_dir = os.getcwd()
        
        # Download the file
        file = await context.bot.get_file(update.message.document.file_id)
        file_path = os.path.join(current_dir, file_name)
        await file.download_to_drive(file_path)
        print(f"📥 File saved: {file_path}")

        # Extract if it's a ZIP file
        if file_name.lower().endswith('.zip'):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(current_dir)
            print(f"📦 ZIP extracted: {file_path}")

    except Exception as e:
        await update.message.reply_text(f"❌ Error processing file: {str(e)}")
        print(f"❌ Error processing file: {str(e)}")
        return

    # Track received files in chat_data
    if 'gf_files' not in context.chat_data:
        context.chat_data['gf_files'] = []

    context.chat_data['gf_files'].append(file_path)
    print(f"📁 Current GF files received: {context.chat_data['gf_files']}")

    # Check if both required files are present
    has_csv_xl = any((('deprec' in f.lower() or 'export' in f.lower()) and (f.endswith('.csv') or f.endswith('.xlsx') or f.endswith('.xls'))) for f in context.chat_data['gf_files'])
    has_zip = any(('gf' in f.lower() and 'zip' in f.lower()) for f in context.chat_data['gf_files'])

    print(f"📊 File status - CSV/XL: {has_csv_xl}, ZIP: {has_zip}")

    if not (has_csv_xl and has_zip):
        print("⏳ Waiting for both Reconciliation CSV and GF ZIP...")
        return

    # Send a processing message
    processing_message = await context.bot.send_message(
        chat_id=chat_id,
        text="⏳ Analyzing your files, please wait...",
        parse_mode="HTML"
    )

    print("✅ Both GF files received — running notebook.")
    context.chat_data["gf_files"] = []  # Clear buffer after using

    # Execute notebook
    success, result, message = run_gf_project_1_notebook()

    # Clean the message
    message = clean_p1_message_gf(message)

    if success:
        matching_files = glob.glob("GF_Reconciliation_tool_output*")
        if matching_files:
            file_to_send = matching_files[0]
            with open(file_to_send, "rb") as doc:
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=doc,
                    filename=os.path.basename(file_to_send),
                    caption="📊 Files analyzed, here´s the output for GF Reconciliation tool."
                )
            
            # Send the message report if it exists
            if message:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="HTML"
                )
        else:
            await update.message.reply_text("✅ Notebook ran, but no output file was found.")
    else:
        await update.message.reply_text("❌ GF Project 1 notebook failed silently — please check with the developer.")
        print(f"❌ Notebook error:\n{result}")
    
    # Delete unwanted files
    current_dir = os.getcwd()
    delete_unwanted_files(current_dir, ORIGINAL_FILES)

# ----------------------------------------------------------------- GOLDFINGER PROJECT 3 (EOM) -------------------------------------------------------------------------------------------------------------
async def Playwright_Vrio_GF_Project_3_async(playwright):
    from datetime import datetime
    import os
    import time

    max_retries = 3
    retry_delay = 5  # seconds

    filename = f"EOM_Fcast_{datetime.now().strftime('%Y-%m-%d')}.csv"
    final_path = os.path.join(DOWNLOAD_DIR, filename)

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🟢 Attempt {attempt}: Starting EOM Playwright automation...")

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
            logger.info("Navigating to login page...")
            await page.goto("https://goldie.vrio.app/auth/login", timeout=30000)

            # Login with retries
            login_success = False
            for login_attempt in range(3):
                try:
                    logger.info(f"Login attempt {login_attempt + 1}...")
                    await page.get_by_placeholder("email").click(timeout=10000)
                    await page.get_by_placeholder("email").fill("team123@team123proton.com")
                    await page.get_by_placeholder("password").click(timeout=10000)
                    await page.get_by_placeholder("password").fill("GFTeam123!@")
                    await page.get_by_role("button", name="Login").click(timeout=10000)
                    await page.wait_for_load_state("networkidle", timeout=20000)
                    login_success = True
                    break
                except Exception as e:
                    logger.error(f"Login attempt {login_attempt + 1} failed: {e}")
                    if login_attempt < 2:
                        await page.reload()
                        time.sleep(2)
            if not login_success:
                raise Exception("Failed to login after multiple attempts")

            # Navigate to Analytics
            logger.info("Navigating to Analytics...")
            analytics_link = page.get_by_role("link", name=" Analytics")
            await analytics_link.wait_for(state="visible", timeout=10000)
            await analytics_link.click()
            await page.wait_for_load_state("networkidle", timeout=20000)

            # Go to Saved Reports tab
            logger.info("Opening Saved Reports...")
            saved_reports_tab = page.get_by_role("tab", name="Saved Reports")
            await saved_reports_tab.wait_for(state="visible", timeout=10000)
            await saved_reports_tab.click()
            await page.wait_for_load_state("networkidle", timeout=20000)

            # Open EOM-View
            logger.info("Opening EOM-View...")
            eom_view_link = page.get_by_role("link", name="EOM Fee Fcast")
            await eom_view_link.wait_for(state="visible", timeout=10000)
            await eom_view_link.click()
            await page.wait_for_load_state("networkidle", timeout=20000)

            # Export the report
            logger.info("Initiating download...")
            more_options = page.get_by_role("button", name="More Options ")
            await more_options.wait_for(state="visible", timeout=10000)
            await more_options.click()
            await page.wait_for_timeout(2000)

            async with page.expect_download(timeout=30000) as download_info:
                logger.info("Pressed Export Report")
                export_link = page.get_by_role("link", name="Export Report")
                await export_link.wait_for(state="visible", timeout=10000)
                await export_link.click()

            download = await download_info.value
            await download.save_as(final_path)
            logger.info(f"✅ File downloaded and saved as: {final_path}")

            await context.close()
            await browser.close()
            return  # Success, exit the retry loop

        except Exception as e:
            logger.error(f"Attempt {attempt} failed: {str(e)}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All retry attempts failed")
                raise

def run_gf_project_notebook3():
    notebook_path = "GF_Project_3.ipynb"
    output_path = "GF_Project_3_output.ipynb"
    try:
        pm.execute_notebook(
            notebook_path,
            output_path,
            kernel_name="python3",
            cwd=os.getcwd()
        )
        print("✅ GF Project 3 notebook executed successfully.")
        message = None
        with open(output_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        for cell in nb['cells']:
            if cell['cell_type'] == 'code' and 'print(message_p3)' in cell.get('source', ''):
                for output in cell.get('outputs', []):
                    if 'text' in output:
                        message = output['text'].strip()
                        break
                    elif 'data' in output and 'text/plain' in output['data']:
                        message = output['data']['text/plain'].strip()
                        break
            if message:
                break
        if message:
            print(f"✅ Message extracted:\n{message}")
        else:
            print("⚠️ Warning: No message found in any print(message) cell.")
        return True, output_path, message
    except Exception as e:
        traceback_str = traceback.format_exc()
        print(f"❌ GF notebook failed:\n{traceback_str}")
        return False, traceback_str, None

def output_format_gf3(text):
    for line in text.split('\n'):
        if "EOM" in line or "Total" in line:
            text = text.replace(line, f"<b>{line}</b>")
    return text

async def handle_Project_3_GF(update, context):
    chat_id = update.message.chat_id
    group_chat_name = update.message.chat.title if update.message.chat else None
    tmessage = update.message.caption if update.message.caption else update.message.text if update.message.text else ""
    if group_chat_name not in group_chats_allowed:
        print("❌ Bot not allowed in this chat")
        return
    try:
        file = await context.bot.get_file(update.message.document.file_id)
        file_name = update.message.document.file_name
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, file_name)
        print(f"📂 Current directory: {current_dir}")
        print(f"📄 Attempting to save file to: {file_path}")
        if not os.access(current_dir, os.W_OK):
            print(f"⚠️ Warning: Directory {current_dir} is not writable")
            await context.bot.send_message(
                chat_id=chat_id,
                text="⚠️ Bot doesn't have permission to save files in its directory."
            )
            return
        await file.download_to_drive(file_path)
        if not os.path.exists(file_path):
            print(f"❌ File not found after download attempt: {file_path}")
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Failed to save the file. Please try again."
            )
            return
        print(f"✅ File successfully saved: {file_path}")
        result, output_path, message = run_gf_project_notebook3()
        message = output_format_gf3(message)
        if result:
            if message:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="HTML"
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="✅ Notebook executed successfully, but no message found."
                )
            if "include" in tmessage or "file" in tmessage or "excel" in tmessage:
                excel_file_path = "EOM_Report.xlsx"
                if os.path.exists(excel_file_path):
                    with open(excel_file_path, "rb") as excel_file:
                        await context.bot.send_document(
                            chat_id=chat_id,
                            document=excel_file,
                            filename=os.path.basename(excel_file_path),
                            caption="📊 Here is the requested Excel file."
                        )
                else:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text="⚠️ Excel file not found."
                    )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ Failed to execute the notebook: {output_path}"
            )
        current_dir = os.getcwd()
        delete_unwanted_files(current_dir, ORIGINAL_FILES)
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ An error occurred while processing the file: {e}"
        )

async def call_Project_3_GF(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🔍 Calling Project 3 GF")
    print(update)
    chat_id = update.message.chat_id
    group_chat_name = update.message.chat.title if update.message.chat else None

    if group_chat_name not in group_chats_allowed:
        print("❌ Bot not allowed in this chat")
        return

    # Send initial processing message
    processing_msg = await context.bot.send_message(
        chat_id=chat_id,
        text="⏳ Fetching the EOM View report, please wait..."
    )
    try:
        async with async_playwright() as playwright:
            await Playwright_Vrio_GF_Project_3_async(playwright)
        await processing_msg.edit_text("✅ EOM View report fetched successfully.")

        # Run the notebook
        success, result, message = run_gf_project_notebook3()

        # Get the message in bold as wanted
        message = output_format_gf3(message)

        if success:
            if message:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="HTML"
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="✅ Notebook executed successfully, but no message found."
                )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ Failed to execute the notebook: {result}"
            )

        # Clean up files
        current_dir = os.getcwd()
        delete_unwanted_files(current_dir, ORIGINAL_FILES)

    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ An error occurred: {e}"
        )

# ----------------------------------------------------------------- GOLDFINGER PROJECT 5 (TV) -------------------------------------------------------------------------------------------------------------

def Playwright_GF_Project_5(playwright):
    from datetime import datetime
    import os
    import time

    max_retries = 3
    retry_delay = 5  # seconds

    filename = f"Project5_{datetime.now().strftime('%Y-%m-%d')}.csv"
    final_path = os.path.join(DOWNLOAD_DIR, filename)

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"🟢 Attempt {attempt}: Starting TV Playwright automation...")

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
            page.goto("https://goldie.vrio.app/auth/login", wait_until="networkidle")

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
            analytics_link = page.get_by_role("link", name=" Analytics")
            analytics_link.wait_for(state="visible", timeout=10000)
            analytics_link.click()
            page.wait_for_load_state("networkidle")

            # Go to Saved Reports tab
            logger.info("Opening Saved Reports...")
            saved_reports_tab = page.get_by_role("tab", name="Saved Reports")
            saved_reports_tab.wait_for(state="visible", timeout=10000)
            saved_reports_tab.click()
            page.wait_for_load_state("networkidle")

            # Open Traffic View 1 (GF-specific)
            logger.info("Opening Traffic View 1...")
            traffic_view_selectors = [
                page.get_by_role("link", name=" Traffic View 1"),
                page.get_by_text("Traffic View 1"),
                page.locator("text=Traffic View 1")
            ]
            traffic_view_found = False
            for selector in traffic_view_selectors:
                try:
                    selector.wait_for(state="visible", timeout=5000)
                    selector.click()
                    traffic_view_found = True
                    break
                except Exception as e:
                    logger.info(f"Selector {selector} failed: {e}")
                    continue
            if not traffic_view_found:
                raise Exception("Could not find Traffic View 1 element")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000)

            # Export the report
            logger.info("Initiating download...")
            more_options = page.get_by_role("button", name="More Options ")
            more_options.wait_for(state="visible", timeout=10000)
            more_options.click()
            page.wait_for_timeout(2000)
            with page.expect_download(timeout=30000) as download_info:
                logger.info("Pressed Export Report")
                export_link = page.get_by_role("link", name="Export Report")
                export_link.wait_for(state="visible", timeout=10000)
                export_link.click()
            download = download_info.value
            download.save_as(final_path)
            logger.info(f"✅ File downloaded and saved as: {final_path}")
            context.close()
            browser.close()
            return  # Success, exit the retry loop
        except Exception as e:
            logger.error(f"Attempt {attempt} failed: {str(e)}")
            if attempt < max_retries:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All retry attempts failed")
                raise


def run_gf_project_5_notebook():
    notebook_path = "GF_Project_5.ipynb"
    output_path = "GF_Project_5_serv_output.ipynb"
    try:
        pm.execute_notebook(
            notebook_path,
            output_path,
            kernel_name="python3",
            cwd=os.getcwd()
        )
        print("✅ GF Project 5 notebook executed successfully.")
        message = None
        with open(output_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        for cell in nb['cells']:
            if cell['cell_type'] == 'code' and 'print(output_message)' in cell.get('source', ''):
                for output in cell.get('outputs', []):
                    if 'text' in output:
                        message = output['text'].strip()
                        break
                    elif 'data' in output and 'text/plain' in output['data']:
                        message = output['data']['text/plain'].strip()
                        break
            if message:
                break
        if message:
            print(f"✅ Project 5 output_message extracted:\n{message}")
        else:
            print("⚠️ Warning: No output_message found in any print cell.")
        return True, output_path, message
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"❌ GF Project 5 notebook failed:\n{traceback_str}")
        return False, traceback_str, None

def output_format_gf5(text):
    if not text:
        return text
    lines = text.split('\n')
    formatted_lines = []
    for i, line in enumerate(lines):
        if i == 0 or ('alert' in line.lower()):
            formatted_lines.append(f"<b>{line}</b>")
        else:
            formatted_lines.append(line)
    return '\n'.join(formatted_lines)

def send_TV_message_Project_5(chat_id, text, token):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    print(response.text)


def main_function_Project_5():
    max_retries = 3
    retry_delay = 10  # seconds
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🟢 Attempt {attempt}: Triggered Playwright function for Project 5")
            with sync_playwright() as playwright:
                Playwright_GF_Project_5(playwright)
                success, output_path, message = run_gf_project_5_notebook()
                if success and message:
                    formatted_message = output_format_gf5(message)
                    print(f"🚨 Project 5 output_message:\n{formatted_message}")
                    try:
                        # TODO: Replace with your actual GF group chat ID and token
                        send_TV_message_Project_5("-4873260773", formatted_message, "7710441269:AAFLxf_A5Qjmr02-IzNCo4AbnMRdiUNBr0A")
                    except Exception as e:
                        print(f"❌ Failed to send message to Telegram: {e}")
                else:
                    print("❌ Failed to get output_message from Project 5 notebook.")
                    raise Exception("No output message from notebook")
            print("✅ Project 5 completed")
            break  # Success, exit the retry loop
        except Exception as e:
            print(f"❌ Error in attempt {attempt}: {str(e)}")
            import traceback
            traceback.print_exc()
            if attempt < max_retries:
                print(f"🔄 Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("❌ All retry attempts failed")
                raise
    # Clean up files
    current_dir = os.getcwd()
    delete_unwanted_files(current_dir, ORIGINAL_FILES)
scheduler.add_job(main_function_Project_5, 'cron', hour='14-23, 0-4', minute='*/30', misfire_grace_time=120, timezone=pytz.timezone('Europe/Lisbon'))


def send_TV_message_Project_6(chat_id, text, token):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, data=data)
    print(response.text)

def main_function_Project_6():
    max_retries = 3
    retry_delay = 10  # seconds
    for attempt in range(1, max_retries + 1):
        try:
            print(f"🟢 Attempt {attempt}: Triggered Playwright function for Project 6")
            with sync_playwright() as playwright:
                Playwright_GF_Project_6(playwright)
                success, output_path, message = run_gf_project_6_notebook()
                if success and message:
                    formatted_message = output_format_gf6(message)
                    print(f"🚨 Project 6 output_message:\n{formatted_message}")
                    try:
                        # TODO: Replace with your actual GF group chat ID and token for Project 6
                        send_TV_message_Project_6("-4933759782", formatted_message, "7710441269:AAFLxf_A5Qjmr02-IzNCo4AbnMRdiUNBr0A")
                    except Exception as e:
                        print(f"❌ Failed to send message to Telegram: {e}")
                else:
                    print("❌ Failed to get output_message from Project 6 notebook.")
                    raise Exception("No output message from notebook")
            print("✅ Project 6 completed")
            break  # Success, exit the retry loop
        except Exception as e:
            print(f"❌ Error in attempt {attempt}: {str(e)}")
            import traceback
            traceback.print_exc()
            if attempt < max_retries:
                print(f"🔄 Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("❌ All retry attempts failed")
                raise
    # Clean up files
    current_dir = os.getcwd()
    delete_unwanted_files(current_dir, ORIGINAL_FILES)

# ----------------------------------------------------------   GF PROJECT 6  -------------------------------------------------------------------------------------------------------------
def Playwright_GF_Project_6(playwright: Playwright) -> None:
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            filename1 = "S1R1A1.csv"
            final_path1 = os.path.join(DOWNLOAD_DIR, filename1)
            filename2 = "S1R2+A1.csv"
            final_path2 = os.path.join(DOWNLOAD_DIR, filename2)
            filename3 = "S2R1A1.csv"
            final_path3 = os.path.join(DOWNLOAD_DIR, filename3)
            filename4 = "S2R2+A1.csv"
            final_path4 = os.path.join(DOWNLOAD_DIR, filename4)

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
            return
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("All retry attempts failed")
                raise

def run_gf_project_6_notebook():
    notebook_path = "GF_Project_6_serv.ipynb"
    output_path = "GF_Project_6_serv_output.ipynb"
    try:
        pm.execute_notebook(
            notebook_path,
            output_path,
            kernel_name="python3",
            cwd=os.getcwd()
        )
        print("✅ GF 6 notebook executed successfully.")
        message = None
        with open(output_path, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, as_version=4)
        for cell in nb['cells']:
            if cell['cell_type'] == 'code' and 'print(message)' in cell.get('source', ''):
                for output in cell.get('outputs', []):
                    if 'text' in output:
                        message = output['text'].strip()
                        break
                    elif 'data' in output and 'text/plain' in output['data']:
                        message = output['data']['text/plain'].strip()
                        break
            if message:
                break
        if message:
            print(f"✅ Project 6 message extracted:\n{message}")
        else:
            print("⚠️ Warning: No message found in any print cell.")
        return True, output_path, message
    except Exception as e:
        traceback_str = traceback.format_exc()
        print(f"❌ GF 6 notebook failed:\n{traceback_str}")
        return False, traceback_str, None

def output_format_gf6(text):
    """
    - First line is bold
    - All numbers, parentheses, and percent signs are bolded
    - If a line contains any of the file_names, that line is NOT bolded at all (even numbers etc)
    """
    if not text:
        return text

    file_names = ["S1R1A1", "S1R2+A1", "S2R1A1", "S2R2+A1"]

    lines = text.split('\n')
    formatted_lines = []

    # Regex for numbers (integers, decimals, negatives)
    number_pattern = re.compile(r'(-?\d+(?:\.\d+)?)')

    for i, line in enumerate(lines):
        if i == 0:
            formatted_lines.append(f"<b>{line}</b>")
        else:
            # If line contains any file_name, leave it as normal (no bold at all)
            if any(fn in line for fn in file_names):
                formatted_lines.append(line)
            else:
                # Bold numbers
                line = number_pattern.sub(r"<b>\1</b>", line)
                # Bold parentheses
                line = line.replace('(', '<b>(</b>').replace(')', '<b>)</b>')
                # Bold percent signs
                line = line.replace('%', '<b>%</b>')
                formatted_lines.append(line)

    return '\n'.join(formatted_lines)

async def handle_Project_6_GF(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Project 6 processing."""
    try:
        chat_id = update.message.chat_id
        group_chat_name = update.message.chat.title if update.message.chat else None
        
        if group_chat_name not in group_chats_allowed:
            logger.warning(f"❌ Bot not allowed in chat: {group_chat_name}")
            return

        logger.info("🔄 Starting Project 6 processing...")
        await context.bot.send_message(chat_id=chat_id, text="🔄 Starting Project 6 processing...")

        # Run Playwright to download files
        with sync_playwright() as playwright:
            Playwright_GF_Project_6(playwright)
            
        # Run the notebook
        success, output_path, message = run_gf_project_6_notebook()
        
        if success and message:
            formatted_message = output_format_gf6(message)
            await context.bot.send_message(
                chat_id=chat_id,
                text=formatted_message,
                parse_mode='HTML'
            )
            logger.info("✅ Project 6 completed successfully")
        else:
            error_msg = "❌ Failed to process Project 6 data"
            await context.bot.send_message(chat_id=chat_id, text=error_msg)
            logger.error("❌ Project 6 processing failed")

    except Exception as e:
        import traceback
        error_msg = f"❌ Error in Project 6:\n{str(e)}\n\n{traceback.format_exc()}"
        logger.error(error_msg)
        await context.bot.send_message(chat_id=chat_id, text=error_msg)

# ----------------------------------------------------------------- Message Handlers -------------------------------------------------------------------------------------------------------------
async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """This function will be called for every non-command text message"""
    try:
        chat_id = update.message.chat_id
        message_text = update.message.text or ""
        bot_username = context.bot.username
        
        # Check if bot was mentioned
        if f"@{bot_username}" in message_text:
            # Store the mention time for document processing
            if 'recent_mentions' not in context.chat_data:
                context.chat_data['recent_mentions'] = {}
            context.chat_data['recent_mentions'][chat_id] = datetime.now()
            logger.info(f"🤖 Bot mentioned in chat {chat_id}")
            
    except Exception as e:
        logger.error(f"Error in handle_all_messages: {e}")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document messages."""
    try:
        logger.info("🔄 Document handler triggered")
        
        # Get basic file info
        file = update.message.document
        file_name = file.file_name
        chat_id = update.message.chat_id
        group_chat_name = update.message.chat.title if update.message.chat else None
        
        logger.info(f"📄 Received document: {file_name}")
        logger.info(f"💬 In chat: {group_chat_name}")
        
        if group_chat_name not in group_chats_allowed:
            logger.warning(f"❌ Bot not allowed in chat: {group_chat_name}")
            return
        
        # Check for bot mention in caption
        caption = update.message.caption or ""
        bot_username = context.bot.username
        caption_mentions_bot = f"@{bot_username}" in caption
        
        # Check if bot was recently mentioned
        was_recently_mentioned = False
        if 'recent_mentions' in context.chat_data and chat_id in context.chat_data['recent_mentions']:
            now = datetime.now()
            mention_time = context.chat_data['recent_mentions'][chat_id]
            was_recently_mentioned = (now - mention_time).total_seconds() < 300  # 5 minutes
        
        logger.info(f"🤖 Bot mention status - Caption: {caption_mentions_bot}, Recent: {was_recently_mentioned}")
        
        # Skip processing if bot wasn't mentioned
        if not (caption_mentions_bot or was_recently_mentioned):
            await update.message.reply_text(f"Please mention me with @{bot_username} before uploading files for processing.")
            logger.warning("❌ Bot not mentioned in caption or recently")
            return

        # Handle GF Project 1 (DEPREC)
        if any(keyword in file_name.lower() for keyword in ["gf", "deprec", "reconciliation"]):
            logger.info("✅ Detected Project 1 file")
            await handle_Project_1_GF(update, context)
            return

        # Handle GF Project 3
        elif "eom" in file_name.lower() and "view" in file_name.lower():
            logger.info("✅ Detected Project 3 file")
            await handle_Project_3_GF(update, context)
            return

        else:
            logger.warning(f"❌ File doesn't match any known project: {file_name}")
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ File doesn't match any known project: {file_name}"
            )
            
    except Exception as e:
        import traceback
        error_msg = f"❌ Error processing file:\n{str(e)}\n\n{traceback.format_exc()}"
        logger.error(error_msg)
        await context.bot.send_message(
            chat_id=chat_id,
            text=error_msg
        )

# --- Main bot setup ---
if __name__ == "__main__":
    # Get configuration from environment variables
    BOT_TOKEN = os.getenv('BOT_TOKEN', '7710441269:AAFLxf_A5Qjmr02-IzNCo4AbnMRdiUNBr0A')
    if not BOT_TOKEN:
        try:
            with open("config.txt", "r") as f:
                BOT_TOKEN = f.read().strip()
        except FileNotFoundError:
            logger.error("⚠️ No BOT_TOKEN found in environment or config.txt file!")
            exit(1)

    # Configure application
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    logger.info(f"🔐 BOT_TOKEN loaded successfully.")
    
    # Add handlers
    # 1. Text handler (for capturing recent mentions)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))
    
    # 2. Command handlers
    app.add_handler(CommandHandler("eomfees", call_Project_3_GF))
    
    # 3. Document handler (the main entry point for files)
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    logger.info("🤖 Goldfinger Bot is running... Drop a file with a mention to start processing.")
    app.run_polling()

# Start the scheduler for Project 6 - runs at :01 and :31
scheduler.add_job(main_function_Project_6, 'cron', hour='14-23, 0-4', minute='1,31', misfire_grace_time=120, timezone=pytz.timezone('Europe/Lisbon'))
scheduler.start() 
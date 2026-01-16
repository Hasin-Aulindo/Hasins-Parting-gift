import re
from playwright.async_api import Page, expect, async_playwright
import asyncio
import random
from datetime import datetime, timedelta
import os
import pandas as pd  # Add this
import glob  # Add this

""" ECW_LOGIN_URL = 'https://ilafalapp.eclinicalweb.com/mobiledoc/jsp/webemr/login/newLogin.jsp' # <<< IMPORTANT: Replace with your actual eCW login URL
USERNAME = 'appadmin' # <<< IMPORTANT: Replace with your eCW username
PASSWORD = 'Athelas2025!' # <<< IMPORTANT: Replace with your eCW password """

""" #sunlife
ECW_LOGIN_URL = 'https://azslhcapp.ecwcloud.com/mobiledoc/jsp/webemr/login/newLogin.jsp?isLogout=yes' # <<< IMPORTANT: Replace with your actual eCW login URL
USERNAME = 'billing.team2' # <<< IMPORTANT: Replace with your eCW username
PASSWORD = 'Athelas1!' # <<< IMPORTANT: Replace with your eCW password """

#BP
""" ECW_LOGIN_URL = 'https://schopeapp.ecwcloud.com/mobiledoc/jsp/webemr/login/newLogin.jsp?isLogout=yes' # <<< IMPORTANT: Replace with your actual eCW login URL
USERNAME = 'commureb1' # <<< IMPORTANT: Replace with your eCW username
PASSWORD = 'Hopehealth*1#' # <<< IMPORTANT: Replace with your eCW password """

#All
ECW_LOGIN_URL = 'https://gaaakmapp.ecwcloud.com/mobiledoc/jsp/webemr/login/newLogin.jsp'
USERNAME = 'Billingtfc2'
PASSWORD = 'Athelas1!'

# --- Global variable to store the generated first name ---
# This variable will hold the generated first name once it's created,
# making it accessible throughout the script's execution.
GENERATED_FIRST_NAME = ""

# Global date variables
PAST_DATE = None
FUTURE_DATE = None

def get_date_input():
    """Get exact date input from user and validate it"""
    global PAST_DATE, FUTURE_DATE
    
    while True:
        try:
            print("\nEnter dates in MM/DD/YYYY format")
            start_date_str = input("Enter start date (e.g., 09/15/2023): ")
            end_date_str = input("Enter end date (e.g., 09/30/2023): ")
            
            # Convert string inputs to datetime objects using datetime.strptime
            PAST_DATE = datetime.strptime(start_date_str, '%m/%d/%Y')
            FUTURE_DATE = datetime.strptime(end_date_str, '%m/%d/%Y')
            
            if FUTURE_DATE <= PAST_DATE:
                print("Error: End date must be after start date!")
                continue
                
            print(f"\nDate range set: {PAST_DATE.strftime('%m/%d/%Y')} to {FUTURE_DATE.strftime('%m/%d/%Y')}")
            break
            
        except ValueError as e:
            print("Error: Please enter valid dates in MM/DD/YYYY format!")

async def process_provider_batch(page, start_index, batch_size=10):
    """Handle one batch of providers"""
    global PAST_DATE, FUTURE_DATE
    
    try:
        # Set dates using global variables
        from_date = page.locator('#printFromDate')
        to_date = page.locator('#printToDate')
        
        await from_date.fill(PAST_DATE.strftime('%m/%d/%Y'))
        await to_date.fill(FUTURE_DATE.strftime('%m/%d/%Y'))
        await page.wait_for_timeout(9000)
        
        print(f'Set date range: {PAST_DATE.strftime("%m/%d/%Y")} to {FUTURE_DATE.strftime("%m/%d/%Y")}')

        # Click the resource dropdown

        # Comment this segment out if it is already selected as 'ALL'
        facility_dropdown = page.locator('#displayFacilities')
        await expect(facility_dropdown).to_be_visible(timeout=9000)

        # Use select_option method to select "All" (value "0")
        await facility_dropdown.select_option('0')
        await page.wait_for_timeout(5000)
        print('Selected "All" from facility dropdown')

        facility_element = page.locator('label.col-sm-12:has-text("Display Providers & Resources at Facility")')
        await expect(facility_element).to_be_visible(timeout=9000)
        await facility_element.click()
        print('Clicked facility selection element')
        await page.wait_for_timeout(5000)
         # Comment this segment out if it is already selected as 'ALL'
        # Click expand button for providers
        expand_provider_button = page.locator('div.ms-parent.ng-pristine.ng-untouched.ng-valid.ng-scope.ng-isolate-scope')
        await expect(expand_provider_button).to_be_visible(timeout=5000)
        await expand_provider_button.click(force=True)
        await page.wait_for_timeout(1000)
        print('Expanded provider list')

        # Select providers in current batch
        providers_selected = 0
        providers_not_found = 0
        for i in range(start_index, start_index + batch_size):
            checkbox = page.locator(f'//*[@id="printProvidersDiv"]/div/div/div/div/ul/li[{i}]/label/input')
            try:
                await expect(checkbox).to_be_visible(timeout=8000)
                await checkbox.click()
                providers_selected += 1
                print(f'Selected provider {i}')
            except:
                providers_not_found += 1
                print(f'No more providers found at index {i}')
                # Don't break immediately, continue checking next indexes
                if providers_not_found >= 3:  # If 3 consecutive providers not found, then break
                    break
        
        facility_element = page.locator('label.col-sm-12:has-text("Display Providers & Resources at Facility")')
        await expect(facility_element).to_be_visible(timeout=9000)
        await facility_element.click()
        print('Clicked facility selection element')
        await page.wait_for_timeout(5000)

        # Process even if we have at least one provider
        if providers_selected > 0:
            # Click the facility selection element
            facility_element = page.locator('label.col-sm-12:has-text("Display Providers & Resources at Facility")')
            await expect(facility_element).to_be_visible(timeout=1000)
            await facility_element.click()
            print('Clicked facility selection element')
            await page.wait_for_timeout(5000)
            
            # Set up download handling
            download_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
            os.makedirs(download_path, exist_ok=True)

            # Handle export and download
            async with page.expect_download(timeout=90000) as download_info:
                export_button = page.locator('button#printScheduleBtn3.btn.btn-lgrey.pull-left.btn-sm.btn-xs')
                await expect(export_button).to_be_visible(timeout=1000)
                await export_button.click()
                print('Clicked export button')

                # Save downloaded file with meaningful name
                download = await download_info.value
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"schedule_export_batch_{start_index}_{timestamp}.csv"
                filepath = os.path.join(download_path, filename)
                await download.save_as(filepath)
                print(f'Downloaded and saved as: {filepath}')
            
            await page.wait_for_timeout(8000)
            # Return False only if we found less than batch_size providers
            return providers_selected >= batch_size
        
        return False

    except Exception as e:
        print(f"Error processing batch starting at index {start_index}: {e}")
        return False

async def run_ecw_login_test():
    """
    Automates the ECW login and report generation process with batch processing of providers
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            print('Navigating to login page...')
            await page.goto(ECW_LOGIN_URL)
            await page.wait_for_selector('input[name="doctorID"]', state='visible')

            # Username step
            await page.fill('input[name="doctorID"]', USERNAME)
            await page.click('input[type="submit"]')

            # Password step
            await page.fill('input[name="passwordField"]', PASSWORD)
            async with page.expect_navigation(timeout=200000):
                await page.click('input[type="submit"]')
            print('Login successful')

            try:
                # Wait a short time for popup title
                popup_title = page.locator('h4.modal-title', has_text="License Alert")
                if await popup_title.is_visible(timeout=3000):  # 3-second wait
                    print("Popup detected - closing...")
                    close_button = page.locator('//html/body/div[3]/div[3]/div[10]/div/div/div/div/div[1]/button')
                    await close_button.click()
                    await page.wait_for_timeout(500)  # short pause after close
                else:
                    print("No popup detected")
            except Exception as e:
                print(f"No popup appeared or error handling popup: {e}")

            # Initialize batch processing
            start_index = 2  # Starting from li[2]
            batch_count = 0

            while True:
                try:
                    print(f"\n--- Processing Batch #{batch_count + 1} (starting at index {start_index}) ---")
                    
                    # Right-click schedule cell
                    target_schedule_cell = page.locator('td.fc-widget-content.resourceSchedule').first
                    await expect(target_schedule_cell).to_be_visible(timeout=200000)
                    await target_schedule_cell.hover()
                    await target_schedule_cell.click(button='right')
                    print('Right-clicked schedule cell')

                    menu_item = page.locator('li.context-menu-item.context-menu-icon.context-menu-icon-print')
                    await expect(menu_item).to_be_visible(timeout=2000)
                    await menu_item.click()
                    print('Clicked Print Schedule menu item')                    

                    # Process current batch
                    has_more = await process_provider_batch(page, start_index)
                    
                    if not has_more:
                        print("No more providers to process - completing automation")
                        break
                    
                    start_index += 10
                    batch_count += 1
                    print(f"Completed batch #{batch_count}")
                    
                    # Optional: Add delay between batches
                    await page.wait_for_timeout(2000)

                except Exception as e:
                    print(f"Error processing batch #{batch_count + 1}: {e}")
                    await page.screenshot(path=f'batch_{batch_count + 1}_error.png')
                    if batch_count == 0:  # If first batch fails, stop execution
                        raise e
                    break  # For other batches, stop gracefully

            print(f"\nAutomation completed. Processed {batch_count} batches of providers")
            
        except Exception as e:
            print(f"Critical error in automation: {e}")
            await page.screenshot(path='critical_error.png')
        finally:
            # Keep browser open for inspection
            print('Automation finished - browser paused for inspection')
            
            # Add CSV combining functionality
            try:
                import pandas as pd
                print("\nStarting CSV file merge process...")
                
                # Get all CSV files in downloads directory
                download_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
                csv_files = glob.glob(os.path.join(download_path, "schedule_export_batch_*.csv"))
                
                if csv_files:
                    # Sort files by batch number to maintain order
                    csv_files.sort()
                    print(f"Found {len(csv_files)} CSV files to merge")
                    
                    # Read and combine all CSV files
                    dfs = []
                    for csv_file in csv_files:
                        try:
                            df = pd.read_csv(csv_file)
                            dfs.append(df)
                            print(f"Processed: {os.path.basename(csv_file)}")
                        except Exception as e:
                            print(f"Error processing {csv_file}: {e}")
                    
                    # Concatenate all dataframes
                    if dfs:
                        combined_df = pd.concat(dfs, ignore_index=True)
                        
                        # Save combined CSV
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        output_file = os.path.join(download_path, f"combined_schedule_export_{timestamp}.csv")
                        combined_df.to_csv(output_file, index=False)
                        print(f"\nSuccessfully merged all CSV files into: {output_file}")
                        
                        # Optionally remove individual batch files
                        for csv_file in csv_files:
                            os.remove(csv_file)
                        print("Removed individual batch files")
                    else:
                        print("No valid CSV data found to merge")
                else:
                    print("No CSV files found to merge")
                    
            except Exception as e:
                print(f"Error during CSV merge process: {e}")

# Run the script
if __name__ == '__main__':
    get_date_input()  # Get user input for dates before running the script
    asyncio.run(run_ecw_login_test())


""" Actual login flow
print('Navigating to login page...')
            await page.goto(ECW_LOGIN_URL)
            await page.wait_for_selector('input[name="doctorID"]', state='visible')

            # Username step
            await page.fill('input[name="doctorID"]', USERNAME)
            await page.click('input[type="submit"]')

            # Password step
            await page.fill('input[name="passwordField"]', PASSWORD)
            async with page.expect_navigation(timeout=200000):
                await page.click('input[type="submit"]')
            print('Login successful') """


""" Brevrard Health
print('Navigating to login page...')
            await page.goto(ECW_LOGIN_URL)
            await page.wait_for_selector('input[name="loginfmt"]', state='visible')
            # Username step
            await page.fill('input[name="loginfmt"]', USERNAME)
            await page.click('input[type="submit"]')
            # Password step
            await page.fill('input[name="passwd"]', PASSWORD)
            async with page.expect_navigation(timeout=200000):
                await page.click('input[type="submit"]')
            print('Login successful') """
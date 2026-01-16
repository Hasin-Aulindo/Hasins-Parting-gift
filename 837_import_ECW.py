import re 
from playwright.async_api import Page, expect, async_playwright
import asyncio
import random
from datetime import datetime, timedelta
import os
import pandas as pd
import glob

# --- Credentials and URL ---
ECW_LOGIN_URL = 'https://moaosmapp.ecwcloud.com/mobiledoc/jsp/webemr/login/newLogin.jsp'
USERNAME = 'MikeSmith'
PASSWORD = 'Athelas@2025'

async def run_ecw_claim_report_navigation():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            executable_path="C:/Program Files/Google/Chrome/Application/chrome.exe"
        )
        page = await browser.new_page()
        
        from datetime import datetime, timedelta

            # --- Get Date Range from User Input ---
        sfrom_input = input("Enter start date (MM/DD/YYYY): ")
        sto_input = input("Enter end date (MM/DD/YYYY): ")

        try:
                sfrom_date = datetime.strptime(sfrom_input, '%m/%d/%Y')
                sto_date = datetime.strptime(sto_input, '%m/%d/%Y')
        except ValueError:
                print("Invalid date format. Please use MM/DD/YYYY.")
                exit()

        try:
            # --- Login ---
            print('Navigating to login page...')
            await page.goto(ECW_LOGIN_URL)
            await page.wait_for_selector('input[name="doctorID"]', state='visible')
            await page.fill('input[name="doctorID"]', USERNAME)
            await page.click('input[type="submit"]')

            await page.fill('input[name="passwordField"]', PASSWORD)
            async with page.expect_navigation(timeout=200000):
                await page.click('input[type="submit"]')
            print('Login successful')
            
            

            print('Opening main menu...')
            menu_button = page.locator('#jellybean-panelLink4')  # Using ID selector
            await expect(menu_button).to_be_visible(timeout=20000)
            await menu_button.click()
            print('Clicked on the nav')

            print('Clicking on Billing menu...')
            billing_click = page.locator('#Billing_menu a.cursor')
            await expect(billing_click).to_be_visible(timeout=30000)
            await billing_click.hover()
            await billing_click.dblclick() 
            print('Double-clicked on Billing')
            
            """ await page.pause() """

            # Click on Batches
            batches_click = page.locator('#BATCHES_BILLING')
            await expect(batches_click).to_be_visible(timeout=30000)
            await page.wait_for_timeout(2000)
            await batches_click.click()
            print('Clicked on Batches')

            # --- Fill Date Fields in Page ---
            from_date = page.locator('//*[@id="from"]')
            to_date = page.locator('//*[@id="to"]')

            await from_date.fill(sfrom_date.strftime('%m/%d/%Y'))
            await to_date.fill(sto_date.strftime('%m/%d/%Y'))
            print(f'Set date range: {sfrom_date.strftime("%m/%d/%Y")} to {sto_date.strftime("%m/%d/%Y")}')

            

            # --- Click Lookup Button ---
            lookup_button = page.locator('#batchLookupBtn2')
            await expect(lookup_button).to_be_visible(timeout=50000)
            await lookup_button.click()
            print('Clicked on Lookup button')

            

            await page.wait_for_timeout(5000)

            # --- Set dropdown to 200 ---
            """ batch_lookup_dropdown = page.locator('#batchLookupSel2')
            await expect(batch_lookup_dropdown).to_be_visible(timeout=5000)
            await batch_lookup_dropdown.select_option('200')
            print('Selected 200 from batch lookup dropdown') """

            await page.wait_for_timeout(2000)

            """ await page.pause() """

            # --- Set up download directory ---
            download_path = os.path.join(os.path.expanduser('~'), 'Downloads', '837')
            os.makedirs(download_path, exist_ok=True)
            print(f'Download directory set to: {download_path}')

            # --- Loop through batch rows and click each one, with Next button pagination ---
            row_index = 1
            rows_processed = 0
            last_row_not_found = 0
            next_button_fails = 0

            while True:
                try:
                    batch_cell = page.locator(f'#batchLookUpTable > tbody > tr:nth-child({row_index}) > td:nth-child(1)')
                    await expect(batch_cell).to_be_visible(timeout=5000)
                    await batch_cell.click()
                    print(f'Clicked on batch row {row_index}')
                    rows_processed += 1
                    last_row_not_found = 0  # Reset counter on successful click
                    next_button_fails = 0  # Reset next button fail counter
                    
                    # --- Click download button and handle download ---
                    try:
                        async with page.expect_download(timeout=60000) as download_info:
                            download_button = page.locator('#batchLookupBtn6')
                            await expect(download_button).to_be_visible(timeout=3000)
                            await download_button.click()
                            print(f'Clicked download button for row {row_index}')
                            
                            download = await download_info.value
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            original_filename = download.suggested_filename
                            filename = f"batch_{row_index}_{timestamp}_{original_filename}"
                            filepath = os.path.join(download_path, filename)
                            await download.save_as(filepath)
                            await page.wait_for_timeout(2000)
                            print(f'Downloaded and saved as: {filename}')
                        
                        # --- Close any popups that appear after download ---
                        await page.wait_for_timeout(3000)
                        await page.keyboard.press('Escape')
                        await page.wait_for_timeout(500)
                        await page.keyboard.press('Escape')
                        await page.wait_for_timeout(500)
                        print('Pressed Escape twice to close popups')
                    except Exception as e:
                        print(f'Error downloading file for row {row_index}: {e}')
                    
                    await page.wait_for_timeout(500)
                    row_index += 1
                except:
                    last_row_not_found += 1
                    print(f'Row {row_index} not found (attempt {last_row_not_found}/3)')
                    
                    if last_row_not_found >= 3:  # If last row not found 3 times, try next page
                        # Try to click Next button to go to next page
                        try:
                            next_button = page.locator('xpath=/html/body/div[3]/div[5]/section/div/div/div[2]/section/div[3]/div/div[5]/div[2]/div-pagination-control/div[1]/button[3]')
                            await expect(next_button).to_be_visible(timeout=5000)
                            await next_button.click()
                            await page.wait_for_timeout(2000)
                            print('Clicked Next button - moving to next page')
                            
                            # Reset row index for new page
                            row_index = 1
                            last_row_not_found = 0
                            next_button_fails = 0
                        except:
                            next_button_fails += 1
                            print(f'Failed to click Next button (attempt {next_button_fails}/3)')
                            
                            if next_button_fails >= 3:  # If we can't click Next button 3 times, we're done
                                print('\n✓ SUCCESS: All batch rows have been processed!')
                                print(f'Total rows processed: {rows_processed}')
                                print(f'All files saved to: {download_path}')
                                break
                    else:
                        row_index += 1


        

        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            await browser.close()
            
            

# Run the script
asyncio.run(run_ecw_claim_report_navigation())
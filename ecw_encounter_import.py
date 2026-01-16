import re 
from playwright.async_api import Page, expect, async_playwright
import asyncio
import random
from datetime import datetime, timedelta
import os
import pandas as pd
import glob

# --- Credentials and URL ---
ECW_LOGIN_URL = 'https://txmpsdjlfrap3ahoreapp.ecwcloud.com/mobiledoc/jsp/webemr/login/newLogin.jsp#/mobiledoc/jsp/webemr/scheduling/resourceSchedule.jsp'
USERNAME = 'Billing1'
PASSWORD = '!Athelas131'

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
            
            # Handle optional popup after login
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
            

            # Click on Claims
            #claims_click = page.locator('/html/body/div[3]/div[5]/div[1]/nav[1]/ul/li[8]/div/div[1]/ul/li[3]/a')
            claims_click = page.locator('#CLAIMS_BILLING')
            await expect(claims_click).to_be_visible(timeout=200000)
            await billing_click.hover()
            await claims_click.click()
            
            
            print('Arrived at Claim page.')
            


            # --- Fill Date Fields in Page ---
            from_date = page.locator('#fromdate')
            to_date = page.locator('#todate')

            await from_date.fill(sfrom_date.strftime('%m/%d/%Y'))
            await to_date.fill(sto_date.strftime('%m/%d/%Y'))
            print(f'Set date range: {sfrom_date.strftime("%m/%d/%Y")} to {sto_date.strftime("%m/%d/%Y")}')


            # --- Click Neutral Field to Close Date Picker ---
            await page.keyboard.press('Escape')  # This closes any open calendar popups
            await page.wait_for_timeout(500)

            # --- Select Claim Status ---
            claim_status_dropdown = page.locator('#claimStatusCodeId')
            await expect(claim_status_dropdown).to_be_visible(timeout=3000)
            await claim_status_dropdown.click()
            
            # Select "Insurance Accepted"
            await page.wait_for_timeout(300)
            await claim_status_dropdown.select_option('INA')
            print('Selected claim status: Insurance Accepted')
            # --- Select Balance Status ---
            balance_dropdown = page.locator('#claimLookupSel6 > option:nth-child(1)')

            # Wait until dropdown is visible
            await expect(balance_dropdown).to_be_visible(timeout=80000)

            # Select the blank option (empty string as value)
            await balance_dropdown.select_option(index=0)
            print('Selected blank option from Balance dropdown')
            
            # --- Click Lookup Button ---
            lookup_button = page.locator('#btnclaimlookup')
            await expect(lookup_button).to_be_visible(timeout=50000)
            await lookup_button.click()
            print('Clicked on Lookup button')

            # --- Wait for Results to Load ---
            await page.wait_for_timeout(5000)  # Optional buffer before next interaction

            # --- Click Billing Button to Open Dropdown ---
            billing_button = page.locator('xpath=/html/body/div[3]/div[5]/section/div/div[2]/div[2]/section/div[3]/div/div[2]/div/div[3]/button')
            await expect(billing_button).to_be_visible(timeout=50000)
            await billing_button.click()
            print('Clicked on Billing button')

            # --- Click "View Claims Report" ---
            view_claims_report = page.locator('xpath=/html/body/div[3]/div[5]/section/div/div[2]/div[2]/section/div[3]/div/div[2]/div/div[3]/ul/li[13]/button')
            await expect(view_claims_report).to_be_visible(timeout=50000)
            await view_claims_report.hover()
            print('Clicked on View Claims Report')

            # --- Click "CSV" Option ---
            csv_option = page.locator('xpath=/html/body/div[3]/div[5]/section/div/div[2]/div[2]/section/div[3]/div/div[2]/div/div[3]/ul/li[13]/ul/li[2]/button')
            await expect(csv_option).to_be_visible(timeout=50000)
            await csv_option.click()
            print('Clicked on CSV download')

            
            # You can now add steps to select report parameters and download the report
            # Wait for the download to start
            # Wait for the download to start
            download = await page.wait_for_event('download', timeout=50000)

            # Get current user's Downloads folder
            downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')

            # Ensure the folder exists
            os.makedirs(downloads_folder, exist_ok=True)

            # Define full path to save the file
            custom_path = os.path.join(downloads_folder, 'claims-report.csv')

            # Save the file
            await download.save_as(custom_path)
            print(f'Report downloaded to: {custom_path}')


            
            await page.pause()

        

        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            await browser.close()
            
            

# Run the script
asyncio.run(run_ecw_claim_report_navigation())

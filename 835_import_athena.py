import re 
from playwright.async_api import Page, expect, async_playwright
import asyncio
import random
from datetime import datetime, timedelta
import os
import pandas as pd
import glob

# --- Credentials and URL ---
ATHENA_LOGIN_URL = 'https://identity.athenahealth.com/oauth2/auset0ja9xZ2Hniep296/v1/authorize?client%5Fid=0oaet0rfjNzyKCiQQ296&idp=&login%5Fhint=ANETUSERNAME&nonce=a51e755482ef3c7fc869f4cba7a91627107bb6a7947ba2ec04e51fef0dc7594d&prompt=login&redirect%5Furi=https%3A%2F%2Fathenanet%2Eathenahealth%2Ecom%2F1%2F1%2Flogin%2Foidc%2Eesp&response%5Fmode=form%5Fpost&response%5Ftype=code&scope=openid%20profile%20offline%5Faccess%20&sessionToken=&state=eyJGTEFHUyI6eyJDT0RFUEFTU1RIUk9VR0giOm51bGwsIkFORVRNRkFTSElNV0lER0VUIjoiIiwiTk9GUkFNRVNFVCI6bnVsbCwiREVQQVJUTUVOVElEIjpudWxsLCJERUVQTElOSyI6bnVsbH0sIkxPR0lOTUVUQURBVEEiOnsiVVNFUkFVVEhOVFlQRSI6Ik5PTlNTTyIsIkJBTk5FUlRZUEUiOiJsaXZlX2xvZ2luIn0sIkNTUkYiOiI0ZGU4MWVmZjdhNmM3YTNhMDBiOWYxN2IxMzBjYmQwYiIsIlRBUkdFVFVSTCI6bnVsbH0'  # Update with actual Athena login URL
USERNAME = 'bteamii'
PASSWORD = 'Athelas1!!' 

async def run_athena_claim_report_navigation():
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
            print('Navigating to Athena login page...')
            await page.goto(ATHENA_LOGIN_URL)
            
            await page.wait_for_selector('#athena-username', state='visible')
            await page.fill('#athena-username', USERNAME)
            await page.fill('#athena-password', PASSWORD)
            async with page.expect_navigation(timeout=200000):
                await page.click('#athena-o-form-button-bar > div.fe_c_root.fe_f_all > div > button > div > span')

            
            await page.pause()


            
            print('Login successful')
            await page.wait_for_timeout(3000)
            
            await page.wait_for_selector('#loginbutton', state='visible')
            await page.click('#loginbutton')
            print('Clicked login button')
            
            await page.locator("#GlobalNav").content_frame.get_by_title("Settings").locator("div").click()
            print('Clicked settings menu')
            
            await page.get_by_text("Practice Manager").click()
            print('Clicked Practice Manager')
            
            await page.locator("#GlobalWrapper").content_frame.locator("#frameContent").content_frame.locator("iframe[name=\"frScheduleNav\"]").content_frame.get_by_role("link", name="ERA File Search").click()
            print('Clicked ERA File Search')
            
            # Wait for page to load
            await page.wait_for_timeout(2000)
            
            # Fill in start date
            await page.locator("#GlobalWrapper").content_frame.locator("#frameContent").content_frame.locator("iframe[name=\"frMain\"]").content_frame.locator("input[name=\"FINDSTARTDATE\"]").click()
            await page.locator("#GlobalWrapper").content_frame.locator("#frameContent").content_frame.locator("iframe[name=\"frMain\"]").content_frame.locator("input[name=\"FINDSTARTDATE\"]").fill(sfrom_date.strftime('%m/%d/%Y'))
            print(f'Filled start date: {sfrom_date.strftime("%m/%d/%Y")}')
            
            # Fill in end date
            await page.locator("#GlobalWrapper").content_frame.locator("#frameContent").content_frame.locator("iframe[name=\"frMain\"]").content_frame.locator("input[name=\"FINDENDDATE\"]").click()
            await page.locator("#GlobalWrapper").content_frame.locator("#frameContent").content_frame.locator("iframe[name=\"frMain\"]").content_frame.locator("input[name=\"FINDENDDATE\"]").fill(sto_date.strftime('%m/%d/%Y'))
            print(f'Filled end date: {sto_date.strftime("%m/%d/%Y")}')
            
            # Click Show Filtered ERA Batches button
            await page.locator("#GlobalWrapper").content_frame.locator("#frameContent").content_frame.locator("iframe[name=\"frMain\"]").content_frame.get_by_role("button", name="Show Filtered ERA Batches").click()
            print('Clicked Show Filtered ERA Batches button')
            
            # Wait for results to load
            await page.wait_for_timeout(2000)
            
            # Loop through and select ERA files (5 at a time)
            i = 2
            selected_count = 0
            
            while selected_count < 5:
                row_xpath = f'/html/body/form[2]/table/tbody/tr[{i}]/td[1]/input'
                row_element = page.locator("#GlobalWrapper").content_frame.locator("#frameContent").content_frame.locator("iframe[name=\"frMain\"]").content_frame.locator(f'xpath={row_xpath}')
                
                # Check if row exists
                if await row_element.count() == 0:
                    print(f'No more rows found at index {i}')
                    break
                
                # Click the checkbox
                await row_element.click()
                print(f'Selected row {i}')
                selected_count += 1
                
                i += 1
            
            print(f'Selected {selected_count} ERA files')
            
            # Wait before clicking claim menu
            await page.wait_for_timeout(9000)
            
            
            

            
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            await browser.close()

# Run the script
if __name__ == "__main__":
    asyncio.run(run_athena_claim_report_navigation())

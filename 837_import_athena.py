import re 
from playwright.async_api import Page, expect, async_playwright
import asyncio
import random
from datetime import datetime, timedelta
import os
import pandas as pd
import glob

# --- Credentials and URL ---
ATHENA_LOGIN_URL = 'https://identity.athenahealth.com/oauth2/auset0ja9xZ2Hniep296/v1/authorize?BANNERARGS=eyJhbGciOiJSUzI1NiIsImtpZCI6IjI5MjA3OTBkLTgzODEtNDUyMC04ZGViLWI0YWVkNjEzZGFkYyJ9%2EeyJhdWQiOiJodHRwczpcL1wvaWRlbnRpdHkuYXRoZW5haGVhbHRoLmNvbSIsImNpZCI6IjBvYWV0MHJmak56eUtDaVFRMjk2IiwiZGF0YSI6eyJCQU5ORVJUWVBFIjoiTE9HT1VUIiwiS0VZIjoiREVGQVVMVCJ9LCJleHAiOjE3Njc2NDcwODEsImlhdCI6MTc2NzY0Njc4MSwiaXNzIjoiaHR0cHM6XC9cL2F0aGVuYW5ldC5hdGhlbmFoZWFsdGguY29tIiwianRpIjoiYVZ3bVBRckFDemNBQ0tYa0FBQUVyQSJ9%2EW3WFOI7X8vPRRJl%5FI%2DwG8rWZGP1QezlvJyHdSEi5ZNpxRSNNKiqS1Ub5oqmXZVfO%5FFGvKX5fEX6A%2DMlX7KUCaE2FYWq8jPzcZvH9jZswWmaaexTsY%5F5Tvu2TziPgNVMGCyAEeAQcUVKsD5mjJglZiYKW6d0Z1e3m3u1CixLfmGkyEf0FQNJCTJPvO56aipsjrGp%2DvBzyRvlz8Sn1kC%2DDpD2TcDzQafo8aHLxcT1YVQD0GDc6Ujc65aQIUFcSnKctMH8fNM8rWhl%5FuKwNNmtYTXNZvPdbCHu6e7eX%5F%2DPjkQaBaWlaXoHd6eLE%5FWmxtuoLbAXgqlxL4TuiZqRYuLtIRdFpvRu2t8OkEEo%5FzscGPG134WakKHyjJBTHDyjvXR282gUVrjllnXwgIB3aFNWo%5Fnnh4524eIcVKPs3nq2Z%5F%5FgFpWQJTlOxfvP%2DI0bQZsC8nAyIAA8MD%2DsyOQCCR8eeLTD0b8iYqFw82OeV%2Ds2d3yPIGxogeep91Z1wyMqxCclQn%5F5%5Fy6GS3N328uW4YENJPVpeRHCCAH%5FBIx6lIeUwW05CKBBIGyzsr6Qo7B20jVf5b%5FfKQHYdvj4W3OWY3zru2Kq3evUl1cCOa8PbvrB364K2TrZEc3UBlpzvthnCawHcmSUu%2DAkvocxPJ4hVM49sHFfXyws%2D9VUiEsTAaQwHOFw&BANNERTIME=1767646781&SHOWBANNER=LOGOUT&client%5Fid=0oaet0rfjNzyKCiQQ296&idp=&login%5Fhint=&nonce=6b5a567eb3a6035c3216bc5602973968b72459f406bc53e925ba5a88c9f2227b&prompt=login&redirect%5Furi=https%3A%2F%2Fathenanet%2Eathenahealth%2Ecom%2F1%2F1%2Flogin%2Foidc%2Eesp&response%5Fmode=form%5Fpost&response%5Ftype=code&scope=openid%20profile%20offline%5Faccess%20&sessionToken=&state=eyJGTEFHUyI6eyJDT0RFUEFTU1RIUk9VR0giOm51bGwsIkFORVRNRkFTSElNV0lER0VUIjoiIiwiTk9GUkFNRVNFVCI6bnVsbCwiREVQQVJUTUVOVElEIjpudWxsLCJERUVQTElOSyI6bnVsbH0sIkxPR0lOTUVUQURBVEEiOnsiVVNFUkFVVEhOVFlQRSI6Ik5PTlNTTyIsIkJBTk5FUlRZUEUiOiJMT0dPVVQifSwiQ1NSRiI6ImZhMmUyYWRiODViMzBmMzlmMmQ0YzM4MDg2YjFhM2FiIiwiVEFSR0VUVVJMIjpudWxsfQ'  # Update with actual Athena login URL
USERNAME = 'cjones2488'
PASSWORD = 'Athelas2025!' 

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
            
            """ # Wait before clicking claim menu
            await page.wait_for_timeout(9000) """
            
            # Click claim menu
            frame = page.frame_locator('#GlobalNav')
            claims_button = frame.locator("text='Claims'")
            await page.wait_for_timeout(7000)
            await claims_button.wait_for(state='visible')
            await claims_button.click()
            print('Clicked claims menu')


            await page.wait_for_timeout(7000)
            # Click track billing bathces
            await page.click('//*[@id="b521b1dfb1ecde43cd570485d231de66"]')
            print('Clicked billing batch element')

            # Select ANSI837 batch format
            await page.frame_locator('#GlobalWrapper').frame_locator('#frameContent').frame_locator('iframe[name="frMain"]').locator('select[name="BATCHFORMAT"]').select_option('ANSI837')
            print('Selected ANSI837 batch format')
            
            # --- Split date range into 30-day batches ---
            current_start = sfrom_date
            while current_start < sto_date:
                # Calculate end date (30 days later or end date, whichever is earlier)
                current_end = min(current_start + timedelta(days=29), sto_date)
                
                # Format dates as MM/DD/YYYY
                start_date_str = current_start.strftime('%m/%d/%Y')
                end_date_str = current_end.strftime('%m/%d/%Y')
                
                print(f'Processing batch: {start_date_str} to {end_date_str}')
                
                # Fill in start date
                await page.frame_locator('#GlobalWrapper').frame_locator('#frameContent').frame_locator('iframe[name="frMain"]').locator('input[name="FINDSTARTDATE"]').click()
                await page.frame_locator('#GlobalWrapper').frame_locator('#frameContent').frame_locator('iframe[name="frMain"]').locator('input[name="FINDSTARTDATE"]').fill(start_date_str)
                print(f'Filled start date: {start_date_str}')
                
                # Fill in end date
                await page.frame_locator('#GlobalWrapper').frame_locator('#frameContent').frame_locator('iframe[name="frMain"]').locator('input[name="FINDENDDATE"]').click()
                await page.frame_locator('#GlobalWrapper').frame_locator('#frameContent').frame_locator('iframe[name="frMain"]').locator('input[name="FINDENDDATE"]').fill(end_date_str)
                print(f'Filled end date: {end_date_str}')
                
                # Click Filter Batches button
                await page.frame_locator('#GlobalWrapper').frame_locator('#frameContent').frame_locator('iframe[name="frMain"]').get_by_role('button', name='Filter Batches').click()
                print('Clicked Filter Batches button')
                
                # Wait for results to load
                await page.wait_for_timeout(2000)
                
                # Loop through batch rows and click them
                i = 2
                while True:
                    row_xpath = f'/html/body/div[2]/table/tbody/tr[{i}]/td[1]/a'
                    row_element = page.frame_locator('#GlobalWrapper').frame_locator('#frameContent').frame_locator('iframe[name="frMain"]').locator(f'xpath={row_xpath}')
                    
                    # Check if row exists
                    if await row_element.count() == 0:
                        print(f'No more rows found at index {i}')
                        break
                    
                    # Click the row
                    await row_element.click()
                    print(f'Clicked row {i}')
                    
                    # Wait for modal/page to appear
                    await page.wait_for_timeout(1000)
                    
                    # Click on the form field to trigger download
                    async with page.expect_download() as download_info:
                        await page.frame_locator('#GlobalWrapper').frame_locator('#frameContent').frame_locator('iframe[name="frMain"]').get_by_role('link', name=re.compile(r'\.zip')).click()
                        print(f'Clicked field input for row {i}')
                    
                    # Get the download and save it
                    download = await download_info.value
                    download_dir = os.path.join(os.path.dirname(__file__), 'athena_837')
                    os.makedirs(download_dir, exist_ok=True)
                    download_path = os.path.join(download_dir, download.suggested_filename)
                    await download.save_as(download_path)
                    print(f'Downloaded file: {download_path}')
                    
                    # Click cancel button
                    await page.frame_locator('#GlobalWrapper').frame_locator('#frameContent').frame_locator('iframe[name="frMain"]').get_by_role('button', name='Cancel').click()
                    print(f'Clicked cancel for row {i}')
                    
                    # Wait before next row
                    await page.wait_for_timeout(5000)
                    
                    
                    i += 1
                
                # Move to next 30-day batch
                current_start = current_end + timedelta(days=1)
            
            print('All date batches processed')
            

            
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            await browser.close()

# Run the script
asyncio.run(run_athena_claim_report_navigation())

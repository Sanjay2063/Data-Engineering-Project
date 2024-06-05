from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import logging

logging.basicConfig(filename='scrapingLogStore.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

chrome_driver_path = '..\\..\\..\\chromedriver-win32\\chromedriver.exe'
service = Service(executable_path=chrome_driver_path)
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # Disabling images

driver = webdriver.Chrome(service=service, options=chrome_options)

url = "https://www.lenskart.com/stores"

driver.get(url)

store_urls = []
city_names = []

try:
    state_container = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "AvailableStates_stateContainer__1_HiQ"))
    )

    anchor_tags = state_container.find_elements(By.TAG_NAME, 'a')

    for anchor in anchor_tags:
        store_urls.append(anchor.get_attribute('href'))
        city_name_element = anchor.find_element(By.TAG_NAME, 'b')
        city_names.append(city_name_element.text)

    store_info = []

    for store_url, city_name in zip(store_urls, city_names):
            driver.get(store_url)
            
            WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "StoreCard_storeCard__3lKXu"))
            )

            store_cards = driver.find_elements(By.CLASS_NAME, "StoreCard_storeCard__3lKXu")
           
            for store_card in store_cards:             
                store_name_element = store_card.find_element(By.CLASS_NAME, 'StoreCard_name__mrTXJ')
                store_name = store_name_element.text
                
                address_element = store_card.find_element(By.CLASS_NAME, 'StoreCard_storeAddress__PfC_v')
                address = address_element.text
                
                hours_element = store_card.find_element(By.XPATH, '//div[contains(@class, "StoreCard_storeAddress__PfC_v") and contains(@class, "StoreCard_cursor_pointer___SGuZ")]')
                hours = hours_element.text[6:]
            
                phone_parent_div = store_card.find_element(By.CLASS_NAME, 'StoreCard_wrapper__xhJ0A')
                phone_element = phone_parent_div.find_element(By.TAG_NAME, 'a')
                phone = phone_element.get_attribute('href').split(':')[1]
                
                store_info.append({
                    'Store Name': store_name,
                    'City': city_name,
                    'Address': address,
                    'Time': hours,
                    'Phone': phone
                })

                logging.info(f"Store Name: {store_name}, City Name: {city_name}, Address: {address}, Time: {hours}, Phone: {phone}")

finally:
    driver.quit()

df = pd.DataFrame(store_info)

excel_file_path = 'store_info.xlsx'
df.to_excel(excel_file_path, index=False)
logging.info(f"Data saved to Excel file: {excel_file_path}")

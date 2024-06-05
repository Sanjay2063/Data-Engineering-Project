from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import logging
import time 
import os

logging.basicConfig(filename='scrapingLogProduct.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

chrome_driver_path = '..\\..\\..\\chromedriver-win64\\chromedriver.exe'
service = Service(executable_path=chrome_driver_path)
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})  # Disabling images
# chrome_options.add_argument("--headless=new")
driver = webdriver.Chrome(service=service, options=chrome_options)

SCROLL_PAUSE_TIME = 5

url = 'https://www.lenskart.com/eyeglasses.html'

inner_pages = []
data = []
try:    
    driver.get(url)
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, (document.body.scrollHeight-2400));")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        # print(new_height, last_height)
        if new_height == last_height:
            break
        last_height = new_height

    product_containers = WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.CLASS_NAME, 'ProductContainer--1h5el3b.bIsubZ'))
    )
    ratings = []
    for product_container in product_containers:
        product_url = product_container.find_element(By.TAG_NAME, 'a').get_attribute('href')
        product_ratings_element = product_container.find_element(By.CLASS_NAME, "NumberedRatingSpan--kts3v6.fXcXid")
        product_ratings = product_ratings_element.text
        ratings.append(product_ratings)
        data.append({"Product Rating": product_ratings})
        inner_pages.append(product_url)

# Save URLs to an Excel file to ensure that if an error occurs during data fetching, 
# the scraping process can resume without needing to re-scrape all URLs.
    
    # # dfURL = pd.DataFrame(inner_pages, data)
    # # excel_file_path = 'product_url.xlsx'
    # # dfURL.to_excel(excel_file_path, index=False)
    # # print("Data saved to Excel file:", excel_file_path)
    

    # # url_file_path = 'product_url.xlsx'
    # # dfexist = pd.read_excel(url_file_path)
    # # inner_pages = dfexist['URL'].tolist()
    # # ratings = dfexist['Product Rating'].tolist()


    for rating in ratings:
        data.append({"Product Rating": rating})     

    index = 0
    for page in inner_pages:
        try:
            logging.info(f"URL: {page}")
            driver.get(page)
            data[index].update({
                'Product URL': page,
            })
            WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'TechInfoVal--jmyd3g')))
                
            # Product Title
            try:
                product_title_element = driver.find_element(By.CLASS_NAME, 'Title--mnzriy')
            except Exception:
                try:
                    product_title_element = driver.find_element(By.CLASS_NAME, 'basicDetailsstyles__Title-sc-2nv0zt-1')
                except Exception:
                    product_title_element = None
            product_title = product_title_element.get_attribute('innerText') if product_title_element else None

            # Extract product id
            product_id_element = driver.find_element(By.CLASS_NAME, "TechInfoVal--jmyd3g")
            product_id = product_id_element.text   

            # Extract product cost
            product_cost_element = driver.find_element(By.CLASS_NAME, 'SpecialPriceSpan--1mh26ry')
            product_cost = product_cost_element.get_attribute('innerText')

            data[index].update({
                'Product Id': product_id,
                'Product Title': product_title,
                'Product cost': product_cost[1:],
            })

            show_all_element = driver.find_element(By.CLASS_NAME, 'TechInfoLink--1b082xk')
            show_all_element.click()
            
            WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, 'ItemKey--1syx3ni')))
            items = driver.find_elements(By.CLASS_NAME, 'TechnicalInfostyles__ItemContainer-sc-j03lii-4')
            print(len(items))
            
            for item in items:
                name_element = item.find_element(By.CLASS_NAME, 'ItemKey--1syx3ni')
                try:
                    value_element = item.find_element(By.CLASS_NAME, 'ItemValueSpan--1dnd1l8')
                except Exception:
                    try:
                        value_element = item.find_element(By.CLASS_NAME, 'ItemValue--xmlemn')
                    except Exception:
                        value_element = None
                    
                name = name_element.get_attribute('innerText')
                value = value_element.get_attribute('innerText') if value_element else None
                if name in ['Model No.', 'Brand Name', 'Product Type', 'Frame Type', 'Frame Shape', 'Frame Size', 'Frame Width', 'Frame colour']:
                    data[index].update({name: value if '?' not in value else value[:-1]})

            logging.info(f"Data added: {data[index]}")

            index += 1

        except Exception as e:
            logging.error(f"Error processing URL {page}: {str(e)}")
            logging.info(f"Data added: {data[index]}")
            index += 1
            continue
 
except Exception as e:
    logging.error(f"Error occurred: {e}")

finally:
    driver.quit()

excel_file_path = 'product_info.xlsx'

df_new = pd.DataFrame(data)

if os.path.exists(excel_file_path):
    existing_df = pd.read_excel(excel_file_path)
    df_combined = pd.concat([existing_df, df_new], ignore_index=True)
else:
    df_combined = df_new

with pd.ExcelWriter(excel_file_path, mode='a', engine='openpyxl', if_sheet_exists='replace') as writer:
    df_combined.to_excel(writer, index=False)

print("Data added to Excel file:", excel_file_path)


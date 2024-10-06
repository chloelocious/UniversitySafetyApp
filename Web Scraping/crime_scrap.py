import requests
import csv
from bs4 import BeautifulSoup
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import csv

filtered_data_path = './Crime_uptodate/filtered_data_top.csv'
output_data_path = './Crime_uptodate/crime_info_top.csv'

with open(output_data_path, 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Type', 'Date', 'Description', 'Address', 'Latitude', 'Longitude'])
    
    
df = pd.read_csv(filtered_data_path)


latlong_list = df[['Latitude', 'Longitude']].drop_duplicates().values


driver = webdriver.Chrome() 

for lat, lon in latlong_list:
    url = f'https://spotcrime.com/map?lat={lat}&lon={lon}'

    driver.get(url)

    time.sleep(5)

    try:
        button = driver.find_element(By.ID, 'map-page__crime-list__view-btn')
        time.sleep(5)
        driver.execute_script("arguments[0].scrollIntoView(true);", button)
        time.sleep(5)
        button.click()

        time.sleep(5)

        ele = driver.find_elements(By.TAG_NAME, 'a')
        all_crime_url = []
        for e in ele:
            href = e.get_attribute('href')
            if href and "https://spotcrime.com/crime/" in href:
                all_crime_url.append(href)

        crime_info = []
        for crime_url in all_crime_url:
            response = requests.get(crime_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            all_p = soup.find_all('p')

            try:
                crime_info.append([
                    all_p[0].text.split(": ")[1],  # Type
                    all_p[1].text.split(": ")[1],  # Date
                    all_p[2].text.split(": ")[1],  # Description
                    all_p[3].text.split(": ")[1],  # Address
                    lat,
                    lon
                ])
            except IndexError:
                pass

        with open(output_data_path, 'a') as f:
            writer = csv.writer(f)
            writer.writerows(crime_info)

    except Exception as e:
        print(f"Error occurred for lat={lat}, lon={lon}: {e}")

driver.quit()
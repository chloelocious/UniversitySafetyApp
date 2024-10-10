import os
import pandas as pd
import csv
import time
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import university_latlong
from global_vars import stop_scraping_event, current_lat_lon

# function to scrape crime info from SpotCrime
def scrape_spotcrime(top = True):
    global stop_scraping_event, current_lat_lon

    if top:
        filtered_data_path = './Crime_uptodate/filtered_data_top.csv'
        output_data_path = './Crime_uptodate/crime_info_top.csv'
        university_latlong.get_top_universities_latlong(filtered_data_path)
    else:
        filtered_data_path = './Crime_uptodate/filtered_data.csv'
        output_data_path = './Crime_uptodate/crime_info.csv'
        university_latlong.get_universities_latlong(filtered_data_path)

    # load the filtered university data
    df = pd.read_csv(filtered_data_path)

    # check if the crime_info_top.csv already exists and has data
    if os.path.exists(output_data_path):
        existing_data = pd.read_csv(output_data_path)
        if not existing_data.empty:
            # keep track of already scraped Latitude and Longitude pairs to avoid duplicates
            existing_latlongs = existing_data[['Latitude', 'Longitude']].drop_duplicates().values
        else:
            existing_latlongs = []
    else:
        with open(output_data_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Type', 'Date', 'Description', 'Address', 'Latitude', 'Longitude'])
        existing_latlongs = []

    latlong_list = df[['Latitude', 'Longitude']].drop_duplicates().values

    # web driver for scraping
    driver = webdriver.Chrome()  

    for lat, lon in latlong_list:
        if stop_scraping_event.is_set():
            print("Stopping scraping as requested...")
            break
        
        # check if this lat/lon has already been scraped
        if [lat, lon] in existing_latlongs:
            print(f"Skipping already scraped lat={lat}, lon={lon}")
            continue
            
        current_lat_lon = (lat, lon)

        # scraping data for new coordinates
        url = f'https://spotcrime.com/map?lat={lat}&lon={lon}'
        driver.get(url)
        time.sleep(3) 

        try:
            button = driver.find_element(By.ID, 'map-page__crime-list__view-btn')
            time.sleep(2)
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(2)
            button.click()
            time.sleep(2)

            # extract crime information
            ele = driver.find_elements(By.TAG_NAME, 'a')
            all_crime_url = [e.get_attribute('href') for e in ele if e.get_attribute('href') and "https://spotcrime.com/crime/" in e.get_attribute('href')]

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
    current_lat_lon = None
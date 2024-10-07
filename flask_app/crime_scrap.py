import os
import pandas as pd
import csv
import time
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By

def scrape_spotcrime():
    # Paths to files
    filtered_data_path = './Crime_uptodate/filtered_data_top.csv'
    output_data_path = './Crime_uptodate/crime_info_top.csv'

    # Load the filtered university data
    df = pd.read_csv(filtered_data_path)

    # Check if the crime_info_top.csv already exists and has data
    if os.path.exists(output_data_path):
        existing_data = pd.read_csv(output_data_path)
        if not existing_data.empty:
            # Keep track of already scraped Latitude and Longitude pairs to avoid duplicates
            existing_latlongs = existing_data[['Latitude', 'Longitude']].drop_duplicates().values
        else:
            existing_latlongs = []
    else:
        # If the file doesn't exist, create it and add the header
        with open(output_data_path, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Type', 'Date', 'Description', 'Address', 'Latitude', 'Longitude'])
        existing_latlongs = []

    # Get the unique Latitude and Longitude values from the filtered university data
    latlong_list = df[['Latitude', 'Longitude']].drop_duplicates().values

    # Open the web driver ONCE for scraping
    driver = webdriver.Chrome()  

    for lat, lon in latlong_list:
        # Check if this lat/lon has already been scraped
        if [lat, lon] in existing_latlongs:
            print(f"Skipping already scraped lat={lat}, lon={lon}")
            continue

        # Scraping data for new coordinates
        url = f'https://spotcrime.com/map?lat={lat}&lon={lon}'
        driver.get(url)
        time.sleep(5)  # Wait for page to load

        try:
            button = driver.find_element(By.ID, 'map-page__crime-list__view-btn')
            time.sleep(5)
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(5)
            button.click()
            time.sleep(5)

            # Extract crime information
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

            # Append the newly scraped data to the file
            with open(output_data_path, 'a') as f:
                writer = csv.writer(f)
                writer.writerows(crime_info)

        except Exception as e:
            print(f"Error occurred for lat={lat}, lon={lon}: {e}")

    # Close the web driver when done
    driver.quit()
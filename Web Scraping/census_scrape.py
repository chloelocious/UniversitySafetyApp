import pandas as pd
import requests
from bs4 import BeautifulSoup

# Function to create the DataUSA URL for a given city and state
def construct_datausa_url(city, state):
    city = city.lower().replace(' ', '-')
    state = state.lower()
    return f"https://datausa.io/profile/geo/{city}-{state}"

# Function to extract median household income from DataUSA
def get_median_household_income(city, state):
    url = construct_datausa_url(city, state)
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching data for {city}, {state}. Status code: {response.status_code}")
            return None

        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the 2022 median household income
        stat_title = soup.find('div', class_='stat-title', string="2022 Median Household Income")
        if stat_title:
            stat_value = stat_title.find_next('div', class_='stat-value')
            if stat_value:
                income = stat_value.text.strip()
                print(f"Median household income for {city}, {state}: {income}")
                return income
            else:
                print(f"No median household income value found for {city}, {state}.")
                return None
        else:
            print(f"Median household income not found for {city}, {state}.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {city}, {state}: {e}")
        return None

# Function to extract city and state from the address
def extract_city_and_state(address):
    try:
        address_parts = address.split(",")
        if len(address_parts) >= 3:
            city = address_parts[-2].strip()
            state = address_parts[-1].strip().split()[0]
            return city, state
        else:
            return None, None
    except Exception as e:
        print(f"Error extracting city and state from address '{address}': {e}")
        return None, None

# Load the CSV data
file_path = './Crime_uptodate/crime_info.csv'  # Update with your CSV file path
df = pd.read_csv(file_path)

# Prepare to collect results
results = []

# Process each row to get city, state, and median household income
for index, row in df.iterrows():
    address = row['Address']
    city, state = extract_city_and_state(address)
    
    if city and state:
        # Get the median household income
        income = get_median_household_income(city, state)
        results.append({
            'Address': address,
            'City': city,
            'State': state,
            'Median Household Income': income
        })
    else:
        print(f"Could not extract city or state from address: {address}")
        results.append({
            'Address': address,
            'City': None,
            'State': None,
            'Median Household Income': None
        })

# Convert the results to a DataFrame and save to CSV
results_df = pd.DataFrame(results)
results_df.to_csv('median_hhld_income_data.csv', index=False)
print("Results saved to income_results_datausa.csv")

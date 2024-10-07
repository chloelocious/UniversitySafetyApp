import os
import pandas as pd
import requests
import numpy as np
import time
import re

# Directory where your files are located
directory = '/Users/chloelocious/Documents/GitHub/DataPython9588/UniversitySafetyApp/Crime2023EXCEL'
file_prefix = 'filtered'

# RapidAPI setup (replace with your own API key)
RAPIDAPI_KEY = "5cf408b1a9msh01f8afda749d858p1662f7jsnb9b5f1c963d2"
api_url = "https://us-zip-code-to-income.p.rapidapi.com/getincome"

# Function to validate and clean ZIP codes
def is_valid_zip(zip_code):
    """Check if the ZIP code is valid (5 digits) and ensure it's a string."""
    zip_code = str(zip_code).zfill(5).strip()  # Convert to string and pad leading zeros if necessary
    return re.match(r'^\d{5}$', zip_code) is not None

# Function to fetch median income data for a given ZIP code
def get_income_data(zip_code):
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "us-zip-code-to-income.p.rapidapi.com"
    }

    zip_code = str(zip_code).zfill(5).strip()  # Ensure ZIP is a valid 5-digit string with leading zeros

    params = {"zipcode": zip_code}

    try:
        # Send the GET request to the API
        response = requests.get(api_url, headers=headers, params=params)
        
        # Check the response status code
        if response.status_code == 429:
            print(f"Rate limit exceeded. Sleeping for 60 seconds...")
            time.sleep(5)  # Sleep for 60 seconds and retry the request
            return get_income_data(zip_code)  # Retry after delay
        
        elif response.status_code == 404:
            print(f"ZIP code {zip_code} not found.")
            return None  # Return None if ZIP code not found
        
        response.raise_for_status()  # Raise an exception for other errors

        # Parse the JSON response
        data = response.json()

        # Extract the median income from the response
        if data and 'median_income' in data:
            return data['median_income']
        else:
            print(f"No income data found for ZIP {zip_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching income data for ZIP {zip_code}: {e}")
        return None

# Process all CSV files starting with 'filtered'
def process_files(directory, file_prefix):
    # Function to check if a file starts with the given prefix and is a CSV file
    def is_filtered_file(file_name, prefix):
        return file_name.startswith(prefix) and file_name.endswith('.csv')
    
    # List all files in the directory that start with the prefix
    filtered_files = [file for file in os.listdir(directory) if is_filtered_file(file, file_prefix)]
    
    # Process each file
    for file in filtered_files:
        file_path = os.path.join(directory, file)
        print(f"Processing file: {file}")
        
        # Load the dataset with crime data
        data = pd.read_csv(file_path, dtype={'ZIP': str})  # Ensure ZIP is read as a string

        # Check if 'ZIP' column exists
        if 'ZIP' in data.columns:
            print(f"Found ZIP column in file: {file}")
            
            # Create a list to store income data
            income_list = []

            # Fetch income data for each valid ZIP code
            for zip_code in data['ZIP']:
                if pd.notna(zip_code) and is_valid_zip(zip_code):  # Only query valid 5-digit ZIP codes
                    income = get_income_data(zip_code)
                    income_list.append(income)
                else:
                    print(f"Skipping invalid or missing ZIP code: {zip_code}")
                    income_list.append(np.nan)  # Append NaN if ZIP code is invalid or missing

            # Add the income data to the DataFrame
            data['Median_Income'] = income_list
            
            # Save the updated data to a new CSV file with 'processed_' prefix
            new_file_path = os.path.join(directory, f'processed_{file}')
            data.to_csv(new_file_path, index=False)
            print(f"Processed and saved: {new_file_path}")
        else:
            print(f"Skipped: {file} (No ZIP column)")

# Run the process
process_files(directory, file_prefix)

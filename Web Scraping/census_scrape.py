import os
import pandas as pd
import requests
import numpy as np

# Directory where your files are located
directory = '/Users/chloelocious/Documents/GitHub/DataPython9588/UniversitySafetyApp/Crime2023EXCEL'
file_prefix = 'filtered'

# Census API setup (replace with your actual API key)
API_KEY = "7e8fd5904e6cce12a5d523b8a222aa4eaafaed45"

# Function to get census demographic data using ZCTA (ZIP Code Tabulation Area)
def get_income_data(zcta):
    if pd.isna(zcta):
        print(f"Skipping empty ZCTA value.")
        return None  # Skip if ZCTA is missing
    
    try:
        # Ensure ZIP code is valid by stripping spaces and ensuring it has 5 digits
        zcta = str(zcta).strip()[:5]
        print(f"Fetching data for ZCTA: {zcta}")

        # Construct the API URL for ZCTA data
        url = f"https://api.census.gov/data/2019/acs/acs5?get=B19013_001E&for=zip%20code%20tabulation%20area:{zcta}&key={API_KEY}"
        
        # Send the request
        response = requests.get(url)
        data = response.json()

        # Print full response for debugging
        print(f"Census API response for ZCTA {zcta}: {data}")
        
        # Check if data is present in the response
        if data and len(data) > 1:
            income_data = data[1][0]  # The actual data starts at index 1
            if income_data is not None:
                print(f"Income data for ZCTA {zcta}: {income_data}")
                return income_data
            else:
                print(f"Income data not found for ZCTA {zcta}")
                return None
        else:
            print(f"No income data returned from Census API for ZCTA {zcta}")
            return None
    except Exception as e:
        print(f"Error retrieving income data for ZCTA {zcta} -> {e}")
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
        data = pd.read_csv(file_path)
        
        # Check if 'ZIP' column exists
        if 'ZIP' in data.columns:
            print(f"Found ZIP column in file: {file}")
            
            # Apply the function to each row, skipping rows with NaN ZIP
            data['Income_Data'] = data.apply(lambda row: get_income_data(row['ZIP']) if not pd.isna(row['ZIP']) else np.nan, axis=1)
            
            # Check if the 'Income_Data' column was added successfully
            if 'Income_Data' in data.columns:
                print(f"'Income_Data' column added successfully for {file}.")
            else:
                print(f"Failed to add 'Income_Data' column for {file}.")
            
            # Save the final dataset with 'processed_' prefix
            new_file_path = os.path.join(directory, f'processed_{file}')
            data.to_csv(new_file_path, index=False)
            print(f"Processed and saved: {new_file_path}")
        else:
            print(f"Skipped: {file} (No ZIP columns)")

# Run the process
process_files(directory, file_prefix)

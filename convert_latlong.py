import pandas as pd
from geopy.geocoders import Nominatim
import os
import ssl
import certifi
import time

# Directory where the files are located
directory = 'Crime2023EXCEL'

# Geocoding function with SSL context for secure requests
ctx = ssl.create_default_context(cafile=certifi.where())
geolocator = Nominatim(user_agent="UniversitySafetyApp (chloc748@gmail.com)", ssl_context=ctx)

def get_lat_lon(address):
    """Returns latitude and longitude for a given address with rate-limiting"""
    try:
        location = geolocator.geocode(address)
        time.sleep(1)  # Add a 1-second delay between requests to avoid rate-limiting
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except Exception as e:
        print(f"Error geocoding address {address}: {e}")
        return None, None

# Filter for files that include 'arrest' or 'crime' in the filename
relevant_files = [file for file in os.listdir(directory) if ('arrest' in file.lower() or 'crime' in file.lower()) and (file.endswith('.xls') or file.endswith('.xlsx'))]

# Process each relevant file
for file in relevant_files:
    filepath = os.path.join(directory, file)
    print(f"Processing file: {file}")
    
    # Load the Excel file into a DataFrame
    try:
        data = pd.read_excel(filepath)
    except Exception as e:
        print(f"Error loading {file}: {e}")
        continue
    
    # Ensure that the address column exists
    if 'Address' in data.columns:
        # Apply the geocoding function to get latitude and longitude for each address
        data['Latitude'], data['Longitude'] = zip(*data['Address'].apply(get_lat_lon))
        
        # Save the updated DataFrame to a new CSV file
        output_filename = f"geocoded_{file.replace('.xls', '.csv').replace('.xlsx', '.csv')}"
        output_filepath = os.path.join(directory, output_filename)
        try:
            data.to_csv(output_filepath, index=False)
            print(f"Saved geocoded data to {output_filename}")
        except Exception as e:
            print(f"Error saving {output_filename}: {e}")
    else:
        print(f"Address column not found in {file}")

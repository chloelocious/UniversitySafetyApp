import pandas as pd
from geopy.geocoders import Nominatim
import ssl
import certifi
import time
import os

directory = 'Crime2023EXCEL'
log_file_path = 'geocoding_errors.log'

# geocoding function
ctx = ssl.create_default_context(cafile=certifi.where())
geolocator = Nominatim(user_agent="UniversitySafetyApp (chloc748@gmail.com)", ssl_context=ctx)

def log_address(full_address):
    """Logs addresses that return None for geocoding"""
    with open(log_file_path, 'a') as log_file:
        log_file.write(f"Address returned None: {full_address}\n")

def get_lat_lon(full_address):
    """Returns latitude and longitude for a given full address"""
    try:
        location = geolocator.geocode(full_address)
        time.sleep(1)  
        if location:
            print(location.latitude, location.longitude)
            return location.latitude, location.longitude
        else:
            log_address(full_address)
            return None, None
    except Exception as e:
        print(f"Error geocoding address {full_address}: {e}")
        return None, None

relevant_files = [file for file in os.listdir(directory) if ('arrest' in file.lower() or 'crime' in file.lower()) and (file.endswith('.xls') or file.endswith('.xlsx'))]
for file in relevant_files:
    filepath = os.path.join(directory, file)
    print(f"Processing file: {file}")
    
    # Load the Excel file into a DataFrame
    try:
        data = pd.read_excel(filepath)
    except Exception as e:
        print(f"Error loading {file}: {e}")
        continue
    
    if all(col in data.columns for col in ['Address', 'City', 'State', 'ZIP']):
        data['Full_Address'] = data['Address'] + ', ' + data['City'] + ', ' + data['State'] + ' ' + data['ZIP'].astype(str)
        
        # apply the geocoding function to get latitude and longitude for each full address
        data['Latitude'], data['Longitude'] = zip(*data['Full_Address'].apply(get_lat_lon))
        
        # save as new CSV file
        output_filename = f"geocoded_{file.replace('.xls', '.csv').replace('.xlsx', '.csv')}"
        output_filepath = os.path.join(directory, output_filename)
        try:
            data.to_csv(output_filepath, index=False)
            print(f"Saved geocoded data to {output_filename}")
        except Exception as e:
            print(f"Error saving {output_filename}: {e}")
    else:
        print(f"Address-related columns not found in {file}")

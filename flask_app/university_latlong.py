import requests
import pandas as pd
import os
import glob

def get_top_universities_latlong(csv_path = './Crime_uptodate/filtered_data_top.csv'):
    url = 'https://andyreiter.com/wp-content/uploads/2024/09/US-News-National-University-Rankings-Top-150-Through-2025.xlsx'
    file_path = "./Crime_uptodate/US-News-National-University-Rankings-Top-150-Through-2025.xlsx"
    
    if os.path.exists(file_path):
        os.remove(file_path)
    
    response = requests.get(url)
    
    with open(file_path, 'wb') as file:
        file.write(response.content)
        
    print(f"File downloaded successfully: {file_path}")
    xls = pd.ExcelFile(file_path)
    print(xls.sheet_names)
    
    df = pd.read_excel(file_path, sheet_name='Top 150 National Universities')
    school_names = df['University Name']
    print(school_names)
    

    folder_path = './Crime2023EXCEL'

    filtered_files = glob.glob(os.path.join(folder_path, 'filtered*.csv'))
    print(filtered_files)
    data_list = []


    for file in filtered_files:
        df = pd.read_csv(file)
        
        if 'UNITID_P' in df.columns and 'Latitude' in df.columns and 'Latitude' in df.columns and 'Longitude' in df.columns:
            selected_data = df[['UNITID_P', 'INSTNM', 'Latitude', 'Longitude']]
            selected_data = selected_data[selected_data['INSTNM'].isin(school_names)]
            data_list.append(selected_data)

    result_df = pd.concat(data_list, ignore_index=True)
    result_df = result_df.drop_duplicates()

    result_df.to_csv(csv_path, index=False)

def get_universities_latlong(csv_path = './Crime_uptodate/filtered_data.csv'):

    folder_path = './Crime2023EXCEL'

    filtered_files = glob.glob(os.path.join(folder_path, 'filtered*.csv'))
    print(filtered_files)
    data_list = []


    for file in filtered_files:
        df = pd.read_csv(file)
        
        if 'UNITID_P' in df.columns and 'Latitude' in df.columns and 'Latitude' in df.columns and 'Longitude' in df.columns:
            selected_data = df[['UNITID_P', 'INSTNM', 'Latitude', 'Longitude']]
            data_list.append(selected_data)

    result_df = pd.concat(data_list, ignore_index=True)
    result_df = result_df.drop_duplicates()

    result_df.to_csv(csv_path, index=False)
    

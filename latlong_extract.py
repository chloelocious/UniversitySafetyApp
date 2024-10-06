import os
import pandas as pd
import glob


# Provide the local path to your file
file_path = "./Crime_uptodate/US-News-National-University-Rankings-Top-150-Through-2025.xlsx"

# Load the Excel file
xls = pd.ExcelFile(file_path)

# Load the relevant sheet that contains the top 150 national universities
df = pd.read_excel(file_path, sheet_name='Top 150 National Universities')

# Extract the 'University Name' column
school_names = df['University Name']

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

result_df.to_csv('./Crime_uptodate/filtered_data_top.csv', index=False)

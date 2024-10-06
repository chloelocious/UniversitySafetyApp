import os
import pandas as pd
import glob


folder_path = './Crime2023EXCEL'

filtered_files = glob.glob(os.path.join(folder_path, 'filtered*.csv'))
print(filtered_files)
data_list = []

for file in filtered_files:
    
    df = pd.read_csv(file)
    
    if 'UNITID_P' in df.columns and 'Latitude' in df.columns and 'Longitude' in df.columns:
        selected_data = df[['UNITID_P', 'Latitude', 'Longitude']]
        data_list.append(selected_data)

result_df = pd.concat(data_list, ignore_index=True)
result_df = result_df.drop_duplicates()

result_df.to_csv('./Crime_uptodate/filtered_data.csv', index=False)

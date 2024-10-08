# 读取 ./Crime2023EXCEL 中所有以 filtered_geocoded 开头的csv文件
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import glob

def merge_csv_files(file_paths):
    # Initialize an empty DataFrame
    merged_df = pd.DataFrame()
    
    # Iterate over each file in file_paths
    for file in file_paths:
        # Read each CSV file into a DataFrame, read first line as column names
        df = pd.read_csv(file, header=0)
        # if df only has one row, skip it
        if len(df) == 1:
            
            continue
        
        # Merge the DataFrame based on the columns UNITID_P, INSTNM, OPEID
        if merged_df.empty:
            merged_df = df
        else:
            # Find common columns except the key columns
            common_columns = set(merged_df.columns).intersection(df.columns) - {'UNITID_P', 'INSTNM', 'OPEID'}
            
            merged_df = pd.merge(merged_df, df, on=['UNITID_P', 'INSTNM', 'OPEID'], how='outer', suffixes=('', '_dup'))

            # For the common columns, fill NaN values in the original column with values from the duplicated column
            for col in common_columns:
                merged_df.fillna({col: merged_df.pop(f'{col}_dup')}, inplace=True)


    return merged_df

def get_dataframe():
    files = os.listdir('./Crime2023EXCEL')
    file_paths = [f'./Crime2023EXCEL/{file}' for file in files if file.startswith('filtered_geocoded')]

    merged_df = merge_csv_files(file_paths)
    return merged_df

def create_bar_chart(school_data, year):
    matplotlib.use('Agg')
    
    data = {}
    for school in school_data:
        for key in school:
            if year in key:
                field_name = key[:-2]  
                if field_name not in data:
                    data[field_name] = []
                data[field_name].append(school[key]) 

    school_names = [school['INSTNM'] for school in school_data]  
    df = pd.DataFrame(data, index=school_names)

    ax = df.T.plot(kind='bar', figsize=(10, 6))
    plt.title(f'Comparison for Year 20{year} between Selected Schools')
    plt.ylabel('Number of Incidents')
    plt.xlabel('Incident Type')

    image_path = os.path.join('./flask_app/static', f'bar_chart.png')
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close()

    return f'bar_chart.png'

import pandas as pd

# function to clean address data
def clean_address_data(input_file, output_file):
    df = pd.read_csv(input_file)

    # standardize address to lowercase and remove duplicates
    df['Address_Clean'] = df['Address'].str.lower().str.strip()
    df = df.drop_duplicates(subset=['Address_Clean'])

    # remove rows with missing median household income
    df = df.dropna(subset=['Median Household Income'])

    # save the cleaned data to a new CSV file
    df.to_csv(output_file, index=False)
    print(f"Cleaned data saved to {output_file}")

income_data_path = './Crime_uptodate/median_hhld_income_data_cleaned.csv'
crime_data_path = './Crime_uptodate/crime_info.csv'

# function to load and merge datasets
def load_and_merge_data():
    income_df = pd.read_csv(income_data_path)
    crime_df = pd.read_csv(crime_data_path)

    # merge on address
    merged_df = pd.merge(crime_df, income_df, on='Address', how='inner')
    
    return merged_df

if __name__ == "__main__":
    merged_df = load_and_merge_data()
    print(merged_df.head())

    merged_output_file = './Crime_uptodate/merged_crime_income_data.csv'
    merged_df.to_csv(merged_output_file, index=False)
    print(f"Merged data saved to {merged_output_file}")
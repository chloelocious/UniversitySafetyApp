import pandas as pd

# Provide the local path to your file
file_path = "./Crime_uptodate/US-News-National-University-Rankings-Top-150-Through-2025.xlsx"

# Load the Excel file
xls = pd.ExcelFile(file_path)

# Load the relevant sheet that contains the top 150 national universities
df = pd.read_excel(file_path, sheet_name='Top 150 National Universities')

# Extract the 'University Name' column
school_names = df['University Name']

# based on the scool_names, extract 
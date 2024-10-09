import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

csv_file = "./Crime_uptodate/merged_crime_income_data.csv"
data = pd.read_csv(csv_file)

data_filtered = data[['City', 'Median Household Income']].dropna()
data_filtered['Median Household Income'] = data_filtered['Median Household Income'].replace({'\$': '', ',': ''}, regex=True).astype(float) / 1000

crime_count = data_filtered['City'].value_counts().reset_index()
crime_count.columns = ['City', 'Crime Count']

merged_data = pd.merge(crime_count, data_filtered[['City', 'Median Household Income']].drop_duplicates(), on='City')

print(merged_data)
plt.figure(figsize=(10, 6))
plt.scatter(merged_data['Median Household Income'], merged_data['Crime Count'], alpha=0.5)
plt.title('Crime Count vs Median Household Income')
plt.xlabel('Median Household Income($K)')
plt.ylabel('Crime Count')
plt.grid(True)

z = np.polyfit(merged_data['Median Household Income'], merged_data['Crime Count'], 1)
p = np.poly1d(z)
plt.plot(merged_data['Median Household Income'], p(merged_data['Median Household Income']), "r--")


plt.show()
print("趋势线方程: y = {:.3f}x + {:.3f}".format(z[0], z[1]))

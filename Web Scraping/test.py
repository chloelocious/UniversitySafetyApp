import pandas as pd

# 读取 CSV 文件

filtered_data_path = './Crime_uptodate/filtered_data_top.csv'
df = pd.read_csv(filtered_data_path)
latlong_list = df[['Latitude', 'Longitude']].drop_duplicates().values


# 查找 Latitude 和 Longitude 为特定值的行
latitude, longitude = "38.90333125", "-77.05413178036927"
for i,(lat, lon) in enumerate(latlong_list):
    if lat == latitude and lon == longitude:
        print(f"Latitude: {lat}, Longitude: {lon}",i)
        break   
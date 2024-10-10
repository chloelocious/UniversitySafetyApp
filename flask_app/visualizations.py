import os
import pandas as pd
import folium
import plotly.express as px
from folium.plugins import HeatMap, MarkerCluster, FeatureGroupSubGroup
import plotly.graph_objs as go
import re
import numpy as np

static_dir = 'flask_app/static'
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

combined_data_path = './Crime_uptodate/crime_info.csv'

def plot_layered_crime_map(file_paths):
    marker_colors = ['red', 'green', 'blue']
    legend_labels = [
        'On-Campus Arrests',
        'Non-Campus Crimes',
        'Public Property Arrests'
    ]  

    # intitalizing map
    layered_map = folium.Map(location=[40.7128, -74.0060], zoom_start=5)

    # create a base feature group
    base_feature_group = folium.FeatureGroup(name='Crime Locations', control=False).add_to(layered_map)

    # add datasets as different layers
    for idx, file_path in enumerate(file_paths):
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            print(f"File {file_path} loaded successfully")

            df.columns = df.columns.str.strip()

            if 'Latitude' not in df.columns or 'Longitude' not in df.columns or 'Full_Address' not in df.columns:
                print(f"Skipping file {file_path} due to missing Latitude, Longitude, or Full_Address columns.")
                continue

            feature_group = folium.FeatureGroup(name=legend_labels[idx])

            for _, row in df.iterrows():
                address = row.get('Full_Address', 'No Address Provided')

                # create a popup that includes the crime type (label) and address
                popup_content = f"<b>Type:</b> {legend_labels[idx]}<br><b>Address:</b> {address}"
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=5,  # Smaller size
                    color=marker_colors[idx],
                    fill=True,
                    fill_opacity=0.7,
                    popup=popup_content
                ).add_to(feature_group)
            
            # add feature group to the map
            feature_group.add_to(base_feature_group)
        else:
            print(f"File {file_path} not found.")

    # user can toggle between datasets
    folium.LayerControl().add_to(layered_map)

    map_path = os.path.join(static_dir, 'layered_crime_map_with_legend.html')
    layered_map.save(map_path)
    return map_path

# function to generate a heatmap for crime intensity based on geographical concentration (using Folium)
def plot_crime_heatmap(file_paths):
    heat_data = []

    for file_path in file_paths:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            if 'Latitude' in df.columns and 'Longitude' in df.columns:
                heat_data.extend([[row['Latitude'], row['Longitude']] for _, row in df.iterrows()])
        else:
            print(f"File {file_path} not found.")

    # initialize the heatmap
    heatmap = folium.Map(location=[40.7128, -74.0060], zoom_start=5)  # Example center (New York)
    HeatMap(heat_data).add_to(heatmap)

    heatmap_path = os.path.join(static_dir, 'crime_heatmap.html')
    heatmap.save(heatmap_path)
    return heatmap_path

# generates a bar chart crime trend analysis plot, showing total number of crimes for each type (using Plotly)
def plot_trend_analysis(df):
    # group data by crime type and count occurrences
    crime_counts = df['Type'].value_counts().reset_index()
    crime_counts.columns = ['Type', 'Number of Crimes']

    # bar chart for the number of crimes per type
    fig = px.bar(crime_counts, x='Type', y='Number of Crimes', title='Crime Total by Type')
    fig.update_layout(
        xaxis_title='Crime Type',
        yaxis_title='Number of Crimes',
        xaxis_tickangle=-45,  # Rotate x-axis labels for readability
        height=500,
        width=800
    )
    return fig.to_html(full_html=False)

# group similar crime descriptions (e.g., all "Larceny" types)
def simplify_crime_type(description):
    if re.search(r"larceny|theft", description, re.IGNORECASE):
        return "Larceny/Theft"
    elif re.search(r"vandalism|damage", description, re.IGNORECASE):
        return "Vandalism"
    elif re.search(r"assault|battery", description, re.IGNORECASE):
        return "Assault"
    elif re.search(r"burglary|break-in", description, re.IGNORECASE):
        return "Burglary"
    else:
        return "Other"

# function to generate a crime category distribution (using Plotly) using a pie chart
# to show the distribution of different crime types across all records
def plot_crime_distribution(df):
    # simplify categories by searching for major crime keywords
    df['Simplified Type'] = df['Type'].apply(lambda x: 
                                             'Theft' if 'theft' in x.lower() or 'larceny' in x.lower() else
                                             'Assault' if 'assault' in x.lower() else
                                             'Vandalism' if 'vandalism' in x.lower() else
                                             'Burglary' if 'burglary' in x.lower() else
                                             'Other')
    
    # count occurrences of each simplified type
    crime_counts = df['Simplified Type'].value_counts().reset_index()
    crime_counts.columns = ['Crime Type', 'Number of Crimes']

    # make a pie chart
    fig = px.pie(crime_counts, values='Number of Crimes', names='Crime Type', title='Crime Category Distribution (Simplified)',
                 hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)

    fig.update_traces(textposition='inside', textinfo='percent+label')

    fig.update_layout(
        height=500,
        width=700,
        showlegend=True
    )

    return fig.to_html(full_html=False)


# generates a line chart trend analysis over time (using Plotly)
def trend_analysis_over_time(df):
    df['Date'] = pd.to_datetime(df['Date'])

    # group data by Date and count occurrences
    crime_trend = df.groupby(df['Date'].dt.date).size().reset_index(name='Number of Crimes')

    fig = px.line(crime_trend, x='Date', y='Number of Crimes', title='Crime Trend Over Time')
    
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Number of Crimes',
        height=500,
        width=800
    )
    return fig.to_html(full_html=False)

# function to remove non-numeric characters (e.g., degree symbols) from latitude and longitude columns
def clean_coordinates(df, column_name):
    df[column_name] = df[column_name].apply(lambda x: re.sub(r'[^\d.-]', '', str(x)))
    df[column_name] = df[column_name].astype(float)
    return df

# function to generate an interactive map with crime data for top universities using crime_info_top.csv
def plot_top_universities_crime_info():
    crime_file_path = './Crime_uptodate/crime_info_top.csv'
    university_file_path = './Crime_uptodate/filtered_data_top.csv' 
    
    crime_df = pd.read_csv(crime_file_path)
    university_df = pd.read_csv(university_file_path)

    # clean lat and Longitlongude columns
    crime_df = clean_coordinates(crime_df, 'Latitude')
    crime_df = clean_coordinates(crime_df, 'Longitude')
    university_df = clean_coordinates(university_df, 'Latitude')
    university_df = clean_coordinates(university_df, 'Longitude')

    # merge crime data with university data based on lat and long
    merged_df = pd.merge(crime_df, university_df, on=['Latitude', 'Longitude'], how='left')

    # initialize map
    crime_map = folium.Map(location=[39.8283, -98.5795], zoom_start=4)  # USA center
    
    for _, row in merged_df.iterrows():
        university_name = row['INSTNM'] if pd.notna(row['INSTNM']) else 'Unknown University'
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=(
                f"<b>University:</b> {university_name}<br>"
                f"<b>Crime Type:</b> {row['Type']}<br>"
                f"<b>Description:</b> {row['Description']}"
            ),
            icon=folium.Icon(color='blue')
        ).add_to(crime_map)

    map_path = os.path.join(static_dir, 'crime_info_top_map.html')
    crime_map.save(map_path)
    return map_path

# function to make a bar chart showing the total number of crimes for top universities.
def plot_trend_analysis_top():
    file_path = './Crime_uptodate/crime_info_top.csv'
    df = pd.read_csv(file_path)

    # group by crime type and count occurrences
    crime_counts = df['Type'].value_counts().reset_index()
    crime_counts.columns = ['Crime Type', 'Number of Crimes']

    # make a bar chart
    fig = px.bar(crime_counts, x='Crime Type', y='Number of Crimes', title='Crime Trend Analysis for Top Universities')
    fig.update_layout(
        xaxis_title='Crime Type',
        yaxis_title='Number of Crimes',
        height=500,
        width=800
    )

    return fig.to_html(full_html=False)

# function to make a pie chart showing the distribution of crime categories for top universities.
def plot_crime_distribution_top():
    file_path = './Crime_uptodate/crime_info_top.csv'
    df = pd.read_csv(file_path)

    crime_distribution = df['Type'].value_counts().reset_index()
    crime_distribution.columns = ['Crime Type', 'Number of Crimes']

    # make a pie chart
    fig = px.pie(crime_distribution, names='Crime Type', values='Number of Crimes', title='Crime Category Distribution for Top Universities')
    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig.to_html(full_html=False)

# function to make a bar chart showing the total number of crimes for each university,
# with a slider to select a university.
def plot_crime_by_top_university():
    crime_file_path = './Crime_uptodate/crime_info_top.csv'
    university_file_path = './Crime_uptodate/filtered_data_top.csv'
    
    crime_df = pd.read_csv(crime_file_path)
    university_df = pd.read_csv(university_file_path)
    
    # clean lat and long columns for both dataframes
    crime_df = clean_coordinates(crime_df, 'Latitude')
    crime_df = clean_coordinates(crime_df, 'Longitude')
    university_df = clean_coordinates(university_df, 'Latitude')
    university_df = clean_coordinates(university_df, 'Longitude')

    # merge the crime data with university data on lat and long
    merged_df = pd.merge(crime_df, university_df, on=['Latitude', 'Longitude'], how='left')

    # group data by university and crime type
    crime_by_university = merged_df.groupby(['INSTNM', 'Type']).size().reset_index(name='Number of Crimes')

    # make bar chart with a slider to filter by university
    fig = px.bar(
        crime_by_university,
        x='Type', 
        y='Number of Crimes', 
        color='INSTNM',
        title='Crimes by Top University (Slider)',
        animation_frame='INSTNM',
        height=500,
        width=800
    )
    
    fig.update_layout(
        xaxis_title='Crime Type',
        yaxis_title='Number of Crimes',
        margin=dict(l=50, r=50, t=100, b=50),
        height=600,
    )
    
    return fig.to_html(full_html=False)

# function to create a box plot showing the distribution of median household income for 
# different crime types
def plot_crime_vs_income(df):
    # ensure numeric data type
    df['Median Household Income'] = df['Median Household Income'].replace({'\$': '', ',': ''}, regex=True).astype(float)

    # make box plot 
    fig = px.box(df, x='Type', y='Median Household Income', color='Type',
                 title='Distribution of Median Household Income by Crime Type',
                 points='all', 
                 labels={'Type': 'Crime Type', 'Median Household Income': 'Income (USD)'},
                 template='plotly_white')  

    fig.update_layout(
        xaxis_title='Crime Type',
        yaxis_title='Median Household Income (USD)',
        height=600,  
        width=900,
        showlegend=False, 
    )

    return fig.to_html(full_html=False)

# function to create a map with crime locations and median household income showing crime concentration and income information.
def plot_income_crime_map(df):
    # clean the income column and remove duplicates
    df['Median Household Income'] = df['Median Household Income'].replace({'\$': '', ',': ''}, regex=True).astype(float)
    df = df.drop_duplicates(subset=['Latitude', 'Longitude', 'Median Household Income'])

    # normalize median household income to a range between 0 and 1 for heatmap weight (Source: ChatGPT)
    df['Income_Normalized'] = (df['Median Household Income'] - df['Median Household Income'].min()) / (df['Median Household Income'].max() - df['Median Household Income'].min())

    # initialize the map 
    crime_income_map = folium.Map(location=[39.8283, -98.5795], zoom_start=5)  # Center map on USA
    heat_data = [[row['Latitude'], row['Longitude'], row['Income_Normalized']] for _, row in df.iterrows()]

    # check if there are enough points for the heatmap, otherwise use markers
    if len(heat_data) > 0:
        HeatMap(heat_data, radius=10, blur=15, max_zoom=1).add_to(crime_income_map)
    else:
        print("No valid data for heatmap generation. Using markers instead.")

    # init marker cluster for locations
    marker_cluster = MarkerCluster().add_to(crime_income_map)

    # add markers for each crime type with popup showing crime and income data
    for _, row in df.iterrows():
        crime_type = row['Type']
        income = row['Median Household Income']
        address = row['Address']

        popup_content = (
            f"<b>Crime Type:</b> {crime_type}<br>"
            f"<b>Address:</b> {address}<br>"
            f"<b>Median Household Income:</b> ${income:,.2f}"
        )
        
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=popup_content,
            icon=folium.Icon(color='blue' if income > 60000 else 'red') 
        ).add_to(marker_cluster)

    map_path = os.path.join(static_dir, 'crime_income_heatmap.html')
    crime_income_map.save(map_path)
    print(f"Map saved at {map_path}")
    return map_path

# function to create a scatter plot for City Crime Count vs. Median Household Income in HTML format
def plot_crime_amount_vs_income(df):
    df['Median Household Income'] = df['Median Household Income'].replace({'\$': '', ',': ''}, regex=True).astype(float) /1000 # Convert to K USD
    
    # calculate crime count per city
    crime_count = df['City'].value_counts().reset_index()
    crime_count.columns = ['City', 'Crime Count']
    
    # merge crime count and median household income
    merged_data = pd.merge(crime_count, df[['City', 'Median Household Income']].drop_duplicates(), on='City')
    
    # scatter plot
    fig = px.scatter(merged_data, x='Median Household Income', y='Crime Count', 
                     title='Crime Count vs Median Household Income by City',
                     labels={'Median Household Income': 'Median Household Income (K USD)', 
                             'Crime Count': 'Crime Count'},
                     template='plotly_white')
    
    # calculate the trend line using numpy's polyfit
    z = np.polyfit(merged_data['Median Household Income'], merged_data['Crime Count'], 1)
    p = np.poly1d(z)
    trendline_eq = f"y = {z[0]:.3f}x + {z[1]:.3f}"
    
    fig.add_trace(go.Scatter(
        x=merged_data['Median Household Income'],
        y=p(merged_data['Median Household Income']),
        mode='lines',
        name='Trend Line',
        line=dict(color='red', dash='dash') 
    ))
    
    fig.add_annotation(
        x=max(merged_data['Median Household Income']), 
        y=p(max(merged_data['Median Household Income'])),
        text=trendline_eq,  
        showarrow=False,  
        font=dict(size=12, color="red"),
        xanchor="right",  
        yanchor="bottom"
    )
    
    fig.update_layout(
        xaxis_title='Median Household Income (K USD)', 
        yaxis_title='Crime Count',
        height=600,
        width=900,
    )
    
    return fig.to_html(full_html=False)

# main method for visualizations
if __name__ == "__main__":
    print("Generating visualizations...")

    df = pd.read_csv(combined_data_path)

    # generate trend analysis and crime distribution HTML files (to be rendered in Flask later)
    trend_analysis_html = plot_trend_analysis(df)
    crime_distribution_html = plot_crime_distribution(df)

    with open(os.path.join(static_dir, "trend_analysis.html"), 'w') as f:
        f.write(trend_analysis_html)

    with open(os.path.join(static_dir, "crime_distribution.html"), 'w') as f:
        f.write(crime_distribution_html)

    crime_vs_income_html = plot_crime_vs_income(df)
    income_crime_map_path = plot_income_crime_map(df)

    with open(os.path.join(static_dir, "crime_vs_income.html"), 'w') as f:
        f.write(crime_vs_income_html)

    print("Visualizations generated successfully.")
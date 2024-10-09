import os
import pandas as pd
import folium
import plotly.express as px
from folium.plugins import HeatMap, MarkerCluster
import plotly.graph_objs as go
import re
import numpy as np

# Ensure the static directory exists
static_dir = 'flask_app/static'
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Path to the combined dataset
combined_data_path = './Crime_uptodate/crime_info.csv'  # Update with your actual path

# Function to generate a layered crime map (using Folium)
import folium
import os
import pandas as pd
from folium.plugins import FeatureGroupSubGroup

import folium
import os
import pandas as pd

def plot_layered_crime_map(file_paths):
    # Define marker colors and labels for each dataset
    marker_colors = ['red', 'green', 'blue']
    legend_labels = [
        'On-Campus Arrests',
        'Non-Campus Crimes',
        'Public Property Arrests'
    ]  # Labels based on file_paths order

    layered_map = folium.Map(location=[40.7128, -74.0060], zoom_start=5)  # Center map at New York

    # Create a base feature group
    base_feature_group = folium.FeatureGroup(name='Crime Locations', control=False).add_to(layered_map)

    # Iterate through the datasets and add them as different layers
    for idx, file_path in enumerate(file_paths):
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            print(f"File {file_path} loaded successfully")

            # If needed, clean column names by stripping whitespace
            df.columns = df.columns.str.strip()

            if 'Latitude' not in df.columns or 'Longitude' not in df.columns or 'Full_Address' not in df.columns:
                print(f"Skipping file {file_path} due to missing Latitude, Longitude, or Full_Address columns.")
                continue

            # Create a feature group for the current dataset
            feature_group = folium.FeatureGroup(name=legend_labels[idx])

            # Add points for each crime location in the dataset
            for _, row in df.iterrows():
                address = row.get('Full_Address', 'No Address Provided')

                # Create a popup that includes the crime type (label) and address
                popup_content = f"<b>Type:</b> {legend_labels[idx]}<br><b>Address:</b> {address}"

                # Add CircleMarker for each point
                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=5,  # Smaller size
                    color=marker_colors[idx],
                    fill=True,
                    fill_opacity=0.7,
                    popup=popup_content
                ).add_to(feature_group)
            
            # Add the feature group to the map
            feature_group.add_to(base_feature_group)
        else:
            print(f"File {file_path} not found.")

    # Add layer control for the user to toggle between datasets
    folium.LayerControl().add_to(layered_map)

    # Save the layered map
    map_path = os.path.join(static_dir, 'layered_crime_map_with_legend.html')
    layered_map.save(map_path)
    return map_path

# Function to generate a heatmap for crime intensity (using Folium)
def plot_crime_heatmap(file_paths):
    """
    Generates a heatmap based on the geographical concentration of crime locations.
    """
    heat_data = []

    for file_path in file_paths:
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            # Check if latitude and longitude columns exist
            if 'Latitude' in df.columns and 'Longitude' in df.columns:
                heat_data.extend([[row['Latitude'], row['Longitude']] for _, row in df.iterrows()])
        else:
            print(f"File {file_path} not found.")

    # Initialize the heatmap
    heatmap = folium.Map(location=[40.7128, -74.0060], zoom_start=5)  # Example center (New York)
    
    # Add heatmap layer
    HeatMap(heat_data).add_to(heatmap)

    # Save the heatmap
    heatmap_path = os.path.join(static_dir, 'crime_heatmap.html')
    heatmap.save(heatmap_path)
    return heatmap_path

# Function to generate a crime trend analysis plot (using Plotly)
def plot_trend_analysis(df):
    """
    Generates a bar chart showing the total number of crimes for each type.
    """
    # Group data by crime type and count occurrences
    crime_counts = df['Type'].value_counts().reset_index()
    crime_counts.columns = ['Type', 'Number of Crimes']

    # Create a bar chart for the number of crimes per type
    fig = px.bar(crime_counts, x='Type', y='Number of Crimes', title='Crime Total by Type')
    fig.update_layout(
        xaxis_title='Crime Type',
        yaxis_title='Number of Crimes',
        xaxis_tickangle=-45,  # Rotate x-axis labels for readability
        height=500,
        width=800
    )
    return fig.to_html(full_html=False)

# Function to group similar crime descriptions (e.g., all "Larceny" types)
def simplify_crime_type(description):
    # Define major categories based on keywords
    if re.search(r"larceny|theft", description, re.IGNORECASE):
        return "Larceny/Theft"
    elif re.search(r"vandalism|damage", description, re.IGNORECASE):
        return "Vandalism"
    elif re.search(r"assault|battery", description, re.IGNORECASE):
        return "Assault"
    elif re.search(r"burglary|break-in", description, re.IGNORECASE):
        return "Burglary"
    # Add more patterns as needed
    else:
        return "Other"

# Function to generate a crime category distribution (using Plotly) with more granularity
def plot_crime_distribution(df):
    """
    Generates a pie chart showing the distribution of different crime types across all records.
    This version simplifies the categories and displays them in a pie chart.
    """
    # Simplify categories by searching for major crime keywords
    df['Simplified Type'] = df['Type'].apply(lambda x: 
                                             'Theft' if 'theft' in x.lower() or 'larceny' in x.lower() else
                                             'Assault' if 'assault' in x.lower() else
                                             'Vandalism' if 'vandalism' in x.lower() else
                                             'Burglary' if 'burglary' in x.lower() else
                                             'Other')
    
    # Count occurrences of each simplified type
    crime_counts = df['Simplified Type'].value_counts().reset_index()
    crime_counts.columns = ['Crime Type', 'Number of Crimes']

    # Create a pie chart instead of a bar chart
    fig = px.pie(crime_counts, values='Number of Crimes', names='Crime Type', title='Crime Category Distribution (Simplified)',
                 hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)

    fig.update_traces(textposition='inside', textinfo='percent+label')

    fig.update_layout(
        height=500,
        width=700,
        showlegend=True
    )

    return fig.to_html(full_html=False)


# Function to generate a trend analysis over time (using Plotly)
def trend_analysis_over_time(df):
    """
    Generates a line chart showing the number of crimes over time.
    """
    # Convert Date column to datetime format
    df['Date'] = pd.to_datetime(df['Date'])

    # Group data by Date and count occurrences
    crime_trend = df.groupby(df['Date'].dt.date).size().reset_index(name='Number of Crimes')

    # Create a line chart for crime occurrences over time
    fig = px.line(crime_trend, x='Date', y='Number of Crimes', title='Crime Trend Over Time')
    
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Number of Crimes',
        height=500,
        width=800
    )
    return fig.to_html(full_html=False)

def clean_coordinates(df, column_name):
    """
    Removes non-numeric characters (e.g., degree symbols) from latitude and longitude columns.
    """
    df[column_name] = df[column_name].apply(lambda x: re.sub(r'[^\d.-]', '', str(x)))
    df[column_name] = df[column_name].astype(float)
    return df

def plot_top_universities_crime_info():
    """
    Generates an interactive map with crime data for top universities using crime_info_top.csv.
    """
    crime_file_path = '../Crime_uptodate/crime_info_top.csv'  # Path to crime data
    university_file_path = '../Crime_uptodate/filtered_data_top.csv'  # Path to university info
    
    # Load the CSV files
    crime_df = pd.read_csv(crime_file_path)
    university_df = pd.read_csv(university_file_path)

    # Clean Latitude and Longitude columns
    crime_df = clean_coordinates(crime_df, 'Latitude')
    crime_df = clean_coordinates(crime_df, 'Longitude')
    university_df = clean_coordinates(university_df, 'Latitude')
    university_df = clean_coordinates(university_df, 'Longitude')

    # Merge crime data with university data based on Latitude and Longitude
    merged_df = pd.merge(crime_df, university_df, on=['Latitude', 'Longitude'], how='left')

    # Initialize the map at a default location
    crime_map = folium.Map(location=[39.8283, -98.5795], zoom_start=4)  # USA center
    
    # Add crime markers for top universities
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

    # Save the map
    map_path = os.path.join(static_dir, 'crime_info_top_map.html')
    crime_map.save(map_path)
    return map_path

def plot_trend_analysis_top():
    """
    Generates a bar chart showing the total number of crimes for top universities.
    """
    # Load the dataset
    file_path = './Crime_uptodate/crime_info_top.csv'
    df = pd.read_csv(file_path)

    # Group by crime type and count occurrences
    crime_counts = df['Type'].value_counts().reset_index()
    crime_counts.columns = ['Crime Type', 'Number of Crimes']

    # Create a bar chart
    fig = px.bar(crime_counts, x='Crime Type', y='Number of Crimes', title='Crime Trend Analysis for Top Universities')
    fig.update_layout(
        xaxis_title='Crime Type',
        yaxis_title='Number of Crimes',
        height=500,
        width=800
    )

    return fig.to_html(full_html=False)

def plot_crime_distribution_top():
    """
    Generates a pie chart showing the distribution of crime categories for top universities.
    """
    # Load the dataset
    file_path = '../Crime_uptodate/crime_info_top.csv'
    df = pd.read_csv(file_path)

    # Group by crime type and count occurrences
    crime_distribution = df['Type'].value_counts().reset_index()
    crime_distribution.columns = ['Crime Type', 'Number of Crimes']

    # Create a pie chart
    fig = px.pie(crime_distribution, names='Crime Type', values='Number of Crimes', title='Crime Category Distribution for Top Universities')
    fig.update_traces(textposition='inside', textinfo='percent+label')

    return fig.to_html(full_html=False)

def plot_crime_by_top_university():
    """
    Generates a bar chart showing the total number of crimes for each university,
    with a slider to select a university.
    """
    # Load the datasets
    crime_file_path = './Crime_uptodate/crime_info_top.csv'
    university_file_path = './Crime_uptodate/filtered_data_top.csv'
    
    crime_df = pd.read_csv(crime_file_path)
    university_df = pd.read_csv(university_file_path)
    
    # Clean Latitude and Longitude columns for both dataframes
    crime_df = clean_coordinates(crime_df, 'Latitude')
    crime_df = clean_coordinates(crime_df, 'Longitude')
    university_df = clean_coordinates(university_df, 'Latitude')
    university_df = clean_coordinates(university_df, 'Longitude')

    # Merge the crime data with university data on Latitude and Longitude
    merged_df = pd.merge(crime_df, university_df, on=['Latitude', 'Longitude'], how='left')

    # Group data by university and crime type
    crime_by_university = merged_df.groupby(['INSTNM', 'Type']).size().reset_index(name='Number of Crimes')

    # Create the bar chart with a slider to filter by university
    fig = px.bar(
        crime_by_university,
        x='Type', 
        y='Number of Crimes', 
        color='INSTNM',
        title='Crimes by Top University (Slider)',
        animation_frame='INSTNM',  # Slider changes based on selected university
        height=500,
        width=800
    )
    
    # Adjust layout to avoid overlapping elements and remove dropdown
    fig.update_layout(
        xaxis_title='Crime Type',
        yaxis_title='Number of Crimes',
        margin=dict(l=50, r=50, t=100, b=50),  # Adjust margins to prevent overlap
        height=600,  # Adjust height for better view
    )
    
    return fig.to_html(full_html=False)

# Function to create a bar chart for Crime Type vs. Median Household Income
def plot_crime_vs_income(df):
    """
    Generates a box plot showing the distribution of median household income for different crime types.
    This version will highlight the median, quartiles, and outliers.
    """
    # Ensure the "Median Household Income" column is numeric
    df['Median Household Income'] = df['Median Household Income'].replace({'\$': '', ',': ''}, regex=True).astype(float)

    # Create a box plot with detailed information
    fig = px.box(df, x='Type', y='Median Household Income', color='Type',
                 title='Distribution of Median Household Income by Crime Type',
                 points='all',  # Display all data points including outliers
                 labels={'Type': 'Crime Type', 'Median Household Income': 'Income (USD)'},
                 template='plotly_white')  # Use a clean white template for better readability
    
    # Update layout for better appearance
    fig.update_layout(
        xaxis_title='Crime Type',
        yaxis_title='Median Household Income (USD)',
        height=600,  # Increase height for better view of the box plot
        width=900,
        showlegend=False,  # Disable legend since color-coding is redundant for box plot
    )

    return fig.to_html(full_html=False)

# Function to create a map with crime locations and median household income
def plot_income_crime_map(df):
    """
    Generates a Folium heatmap showing crime concentration and income information.
    Also removes duplicate points and normalizes the income values for better visualization.
    """
    # Clean up the income column
    df['Median Household Income'] = df['Median Household Income'].replace({'\$': '', ',': ''}, regex=True).astype(float)

    # Remove duplicate coordinates with the same income values
    df = df.drop_duplicates(subset=['Latitude', 'Longitude', 'Median Household Income'])

    # Normalize median household income to a range between 0 and 1 for heatmap weight
    df['Income_Normalized'] = (df['Median Household Income'] - df['Median Household Income'].min()) / (df['Median Household Income'].max() - df['Median Household Income'].min())

    # Initialize the map at a default location (USA center)
    crime_income_map = folium.Map(location=[39.8283, -98.5795], zoom_start=5)  # Center map on USA

    # Prepare heatmap data: [latitude, longitude, normalized income]
    heat_data = [[row['Latitude'], row['Longitude'], row['Income_Normalized']] for _, row in df.iterrows()]

    # Check if there are enough points for the heatmap, otherwise use markers
    if len(heat_data) > 0:
        # Add heatmap layer based on crime locations and weighted by normalized median household income
        HeatMap(heat_data, radius=10, blur=15, max_zoom=1).add_to(crime_income_map)
    else:
        print("No valid data for heatmap generation. Using markers instead.")

    # Initialize marker cluster for locations
    marker_cluster = MarkerCluster().add_to(crime_income_map)

    # Add markers for each crime type with popup showing crime and income data
    for _, row in df.iterrows():
        crime_type = row['Type']
        income = row['Median Household Income']
        address = row['Address']

        # Popup content with crime type and income information
        popup_content = (
            f"<b>Crime Type:</b> {crime_type}<br>"
            f"<b>Address:</b> {address}<br>"
            f"<b>Median Household Income:</b> ${income:,.2f}"
        )
        
        # Add marker to the marker cluster
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=popup_content,
            icon=folium.Icon(color='blue' if income > 60000 else 'red')  # Color based on income threshold
        ).add_to(marker_cluster)

    # Save the map
    map_path = os.path.join(static_dir, 'crime_income_heatmap.html')
    crime_income_map.save(map_path)
    print(f"Map saved at {map_path}")
    return map_path

if __name__ == "__main__":
    print("Generating visualizations...")

    # Load your data from a CSV
    df = pd.read_csv('./Crime_uptodate/merged_crime_income_data.csv')

    # Generate the crime map with income data
    income_crime_map_path = plot_income_crime_map(df)

    print("Visualizations generated successfully.")

if __name__ == "__main__":
    print("Generating visualizations...")

    # Load data from the combined dataset (merge crime data and income data)
    df = pd.read_csv(combined_data_path)

    # Generate trend analysis and crime distribution HTML files (to be rendered in Flask later)
    trend_analysis_html = plot_trend_analysis(df)
    crime_distribution_html = plot_crime_distribution(df)

    # Save the generated HTML files for testing
    with open(os.path.join(static_dir, "trend_analysis.html"), 'w') as f:
        f.write(trend_analysis_html)

    with open(os.path.join(static_dir, "crime_distribution.html"), 'w') as f:
        f.write(crime_distribution_html)

    # New visualizations
    crime_vs_income_html = plot_crime_vs_income(df)
    income_crime_map_path = plot_income_crime_map(df)

    # Save the new HTML files for testing
    with open(os.path.join(static_dir, "crime_vs_income.html"), 'w') as f:
        f.write(crime_vs_income_html)

    print("Visualizations generated successfully.")

# Function to create a scatter plot for City Crime Count vs. Median Household Income in HTML format
def plot_crime_amount_vs_income(df):
    """
    Generates an interactive scatter plot showing the relationship between crime count per city
    and median household income, along with a trend line. The result can be embedded in HTML.
    
    Parameters:
    df (DataFrame): The input DataFrame must contain 'City' and 'Median Household Income' columns.
    
    Returns:
    str: HTML string of the plot.
    """
    # Ensure the "Median Household Income" column is numeric
    df['Median Household Income'] = df['Median Household Income'].replace({'\$': '', ',': ''}, regex=True).astype(float) /1000 # Convert to K USD
    
    # Calculate crime count per city
    crime_count = df['City'].value_counts().reset_index()
    crime_count.columns = ['City', 'Crime Count']
    
    # Merge crime count and median household income
    merged_data = pd.merge(crime_count, df[['City', 'Median Household Income']].drop_duplicates(), on='City')
    
    # Create scatter plot
    fig = px.scatter(merged_data, x='Median Household Income', y='Crime Count', 
                     title='Crime Count vs Median Household Income by City',
                     labels={'Median Household Income': 'Median Household Income (K USD)', 
                             'Crime Count': 'Crime Count'},
                     template='plotly_white')
    
    # Calculate the trend line manually using numpy's polyfit
    z = np.polyfit(merged_data['Median Household Income'], merged_data['Crime Count'], 1)
    p = np.poly1d(z)
    trendline_eq = f"y = {z[0]:.3f}x + {z[1]:.3f}"
    
    fig.add_trace(go.Scatter(
        x=merged_data['Median Household Income'],
        y=p(merged_data['Median Household Income']),
        mode='lines',
        name='Trend Line',
        line=dict(color='red', dash='dash')  # Set the trend line to be red and dashed
    ))
    
    # Add the trend line formula as annotation on the plot
    fig.add_annotation(
        x=max(merged_data['Median Household Income']),  # Position the annotation on the right side of the plot
        y=p(max(merged_data['Median Household Income'])),
        text=trendline_eq,  # Display the equation
        showarrow=False,  # No arrow
        font=dict(size=12, color="red"),
        xanchor="right",  # Align text to the right
        yanchor="bottom"
    )
    
    # Customize the layout
    fig.update_layout(
        xaxis_title='Median Household Income (K USD)', 
        yaxis_title='Crime Count',
        height=600,
        width=900,
    )
    
    # Return the plot as an HTML string
    return fig.to_html(full_html=False)

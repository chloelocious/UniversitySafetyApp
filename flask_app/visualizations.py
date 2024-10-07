import os
import pandas as pd
import folium
import plotly.express as px
from folium.plugins import HeatMap

# Ensure the static directory exists
static_dir = 'flask_app/static'
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Path to the combined dataset
combined_data_path = './Crime_uptodate/crime_info.csv'  # Update with your actual path

# Function to generate a layered crime map (using Folium)
def plot_layered_crime_map(file_paths):
    """
    Generates an interactive map with crime data points from multiple datasets using Folium.
    """
    marker_colors = ['red', 'blue', 'green', 'purple', 'orange']  # Define marker colors for each dataset
    
    # Initialize the map at a default location
    layered_map = folium.Map(location=[40.7128, -74.0060], zoom_start=5)  # Example center (New York)

    for idx, file_path in enumerate(file_paths):
        print(f"Processing file: {file_path}")
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            print(f"File {file_path} loaded successfully")
            
            # Check if latitude and longitude columns exist
            if 'Latitude' not in df.columns or 'Longitude' not in df.columns:
                print(f"Skipping file {file_path} due to missing Latitude or Longitude columns.")
                continue
            
            # Add points for each crime location in the dataset
            for _, row in df.iterrows():
                crime_type = row.get('Type', 'Unknown')  # Use 'Unknown' if 'Type' is missing
                description = row.get('Description', 'No Description')  # Use 'No Description' if missing
                
                folium.Marker(
                    location=[row['Latitude'], row['Longitude']],
                    popup=f"Crime Type: {crime_type} - Description: {description}",
                    icon=folium.Icon(color=marker_colors[idx % len(marker_colors)])
                ).add_to(layered_map)
        else:
            print(f"File {file_path} not found.")
    
    print("Finished processing files. Now saving the map.")
    
    # Save the layered map
    try:
        map_path = os.path.join(static_dir, 'layered_crime_map.html')
        layered_map.save(map_path)
        print(f"Map saved successfully to {map_path}")
    except Exception as e:
        print(f"Error saving map: {e}")
    
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

import re  # Import regex for pattern matching

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

# Example usage in a Flask app:
if __name__ == "__main__":
    print("Generating visualizations...")

    # Load data from the combined dataset
    df = pd.read_csv(combined_data_path)

    # Generate trend analysis and crime distribution HTML files (to be rendered in Flask later)
    trend_analysis_html = plot_trend_analysis(df)
    crime_distribution_html = plot_crime_distribution(df)

    # Save the generated HTML files for testing
    with open(os.path.join(static_dir, "trend_analysis.html"), 'w') as f:
        f.write(trend_analysis_html)

    with open(os.path.join(static_dir, "crime_distribution.html"), 'w') as f:
        f.write(crime_distribution_html)

    print("Visualizations generated successfully.")
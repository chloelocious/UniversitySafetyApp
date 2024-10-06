from flask import Flask, render_template, send_from_directory
import os
import pandas as pd
from visualizations import plot_layered_crime_map, plot_crime_heatmap, plot_trend_analysis, plot_crime_distribution, trend_analysis_over_time

app = Flask(__name__)

# Define paths to your datasets
file_paths = [
    '/Users/chloelocious/Documents/GitHub/DataPython9588/UniversitySafetyApp/Crime2023EXCEL/filtered_geocoded_Oncampusarrest202122.csv',
    '/Users/chloelocious/Documents/GitHub/DataPython9588/UniversitySafetyApp/Crime2023EXCEL/filtered_geocoded_Noncampuscrime202122.csv',
    '/Users/chloelocious/Documents/GitHub/DataPython9588/UniversitySafetyApp/Crime2023EXCEL/filtered_geocoded_Publicpropertycrime202122.csv',
]

crime_info_path = '/Users/chloelocious/Documents/GitHub/DataPython9588/UniversitySafetyApp/Crime_uptodate/crime_info.csv'


static_dir = 'static'

# Home route that shows options for different visualizations
@app.route('/')
def index():
    return render_template('home.html')

# Route to show the layered crime map
@app.route('/crime_map')
def crime_map():
    crime_map_path = plot_layered_crime_map(file_paths)  # Pass file_paths as argument
    return render_template('map.html', map_file=os.path.basename(crime_map_path))

# Route to show the crime heatmap
@app.route('/crime_heatmap')
def crime_heatmap():
    heatmap_path = plot_crime_heatmap(file_paths)  # Pass file_paths as argument
    return render_template('map.html', map_file=os.path.basename(heatmap_path))

# Route to show trend analysis
@app.route('/trend_analysis')
def trend_analysis():
    df = pd.read_csv(crime_info_path)
    trend_html = plot_trend_analysis(df)
    return render_template('visualization.html', chart_html=trend_html, title="Crime Trend Analysis")

@app.route('/trend_analysis_over_time')
def trend_analysis_over_time_view():
    df = pd.read_csv(crime_info_path)
    trend_over_time_html = trend_analysis_over_time(df)
    return render_template('visualization.html', chart_html=trend_over_time_html, title="Crime Trend Analysis Over Time")

# Route to show crime distribution
@app.route('/crime_distribution')
def crime_distribution():
    df = pd.read_csv(crime_info_path)
    distribution_html = plot_crime_distribution(df)
    return render_template('visualization.html', chart_html=distribution_html, title="Crime Category Distribution")

# Route to serve static files (like crime_map.html, heatmap.html)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(static_dir, filename)

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, send_from_directory, session, redirect, url_for
import os
import threading
import pandas as pd
from visualizations import plot_layered_crime_map, plot_crime_heatmap, plot_trend_analysis, plot_crime_distribution, trend_analysis_over_time, plot_top_universities_crime_info, plot_crime_distribution_top, plot_crime_by_top_university, clean_coordinates
from crime_scrap import scrape_spotcrime
from global_vars import stop_scraping_event, current_lat_lon
from university_latlong import get_top_universities_latlong
from get_dataframe import get_dataframe, create_bar_chart

app = Flask(__name__)
scrape_thread = None
app.secret_key = 'PythonProject'

# Define paths to your datasets
file_paths = [
    './Crime2023EXCEL/filtered_geocoded_Oncampusarrest202122.csv',
    './Crime2023EXCEL/filtered_geocoded_Noncampuscrime202122.csv',
    './Crime2023EXCEL/filtered_geocoded_Publicpropertyarrest202122.csv',
]

crime_info_path = './Crime_uptodate/crime_info.csv'


static_dir = 'static'

# Home route that shows options for different visualizations
@app.route('/')
def index():
    return render_template('home.html')

# Route to show the layered crime map
@app.route('/crime_map')
def crime_map():
    title = "University Crime Map"
    crime_map_path = plot_layered_crime_map(file_paths)  # Pass file_paths as argument
    return render_template('map.html', map_file=os.path.basename(crime_map_path), page_title = title)

# Route to show the crime heatmap
@app.route('/crime_heatmap')
def crime_heatmap():
    title = "University Crime Heatmap"
    heatmap_path = plot_crime_heatmap(file_paths)  # Pass file_paths as argument
    return render_template('map.html', map_file=os.path.basename(heatmap_path), page_title = title)

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

@app.route('/crime_map_top')
def crime_map_top():
    title = "Top University Crime Map"
    crime_map_path = plot_top_universities_crime_info()  # Correct function for top universities map
    return render_template('map.html', map_file=os.path.basename(crime_map_path), page_title = title)

# Route for Crime by University with Dropdown
@app.route('/trend_analysis_top')
def trend_analysis_top():
    trend_analysis_html = plot_crime_by_top_university()
    return render_template('visualization.html', chart_html=trend_analysis_html, title="Crimes by Top Universities")

@app.route('/crime_distribution_top')
def crime_distribution_top():
    crime_distribution_html = plot_crime_distribution_top()
    return render_template('visualization.html', chart_html=crime_distribution_html, title="Crime Category Distribution of Top Universities")


@app.route('/raw_data')
def display_raw_data_all():
    """
    Displays raw data for all universities in a table format.
    """
    # Load the dataset for all universities
    all_universities_file = './Crime_uptodate/crime_info.csv'
    df = pd.read_csv(all_universities_file)

    # Convert the DataFrame to HTML table
    table_html = df.to_html(index=False, classes='table table-striped')

    # Render the raw data in a template
    return render_template('raw_data.html', table=table_html, title="Raw Data: All Universities")

@app.route('/raw_data_top')
def display_raw_data_top():
    """
    Displays raw data for top universities in a table format, including university names.
    """
    # Load the datasets
    crime_file = './Crime_uptodate/crime_info_top.csv'
    university_file = './Crime_uptodate/filtered_data_top.csv'
    print(os.path.exists(crime_file))  # Should return True if the file exists

    crime_df = pd.read_csv(crime_file)
    university_df = pd.read_csv(university_file)
    print(crime_df.head())  # Ensure the data is loaded correctly

    # Clean the Latitude and Longitude columns in both datasets
    crime_df = clean_coordinates(crime_df, 'Latitude')
    crime_df = clean_coordinates(crime_df, 'Longitude')
    university_df = clean_coordinates(university_df, 'Latitude')
    university_df = clean_coordinates(university_df, 'Longitude')
    
    print(crime_df.head())
    print(university_df.head())
    print("Crime Data Shape:", crime_df.shape)
    print("University Data Shape:", university_df.shape)

    # Merge on Latitude and Longitude to include university names
    merged_df = pd.merge(crime_df, university_df, on=['Latitude', 'Longitude'], how='left')

    # Debugging: print the first few rows to see if the merge worked
    print(merged_df.head())

    # Check if merged_df is empty
    if merged_df.empty:
        print("The merged DataFrame is empty!")

    # Convert the merged DataFrame to an HTML table
    table_html = merged_df.to_html(index=False, classes='table table-striped')

    # Render the raw data in a template
    return render_template('raw_data.html', table=table_html, title="Raw Data: Top Universities")

@app.route('/scrape_spotcrime')
def scrape_spotcrime_route():
    global scrape_thread, stop_scraping_event

    # Check if the scraping thread is already running
    if scrape_thread is not None and scrape_thread.is_alive():
        return render_template('scrape_status.html', message="Scraping is already in progress.")

    # Reset the stop event in case it was set before
    stop_scraping_event.clear()

    # Start the scraping in a background thread
    scrape_thread = threading.Thread(target=scrape_spotcrime, kwargs={'top': False})
    scrape_thread.start()

    # Inform the user that scraping has started
    return render_template('scrape_status.html', message="SpotCrime data scraping has started.")

@app.route('/compare_school')
def compare_school():
    return render_template('compare_school.html')

@app.route('/compare_school_after', methods=['GET', 'POST'])
def compare_school_after():
    if request.method == 'POST':
        schools = []
        for key in request.form:
            if "school" in key:
                schools.append(request.form[key].lower())

        df = get_dataframe() 

        school_data = []
        for school_name in schools:
            school = next((school for index, school in df.iterrows() if school_name in school['INSTNM'].lower()), None)
            if school is not None:
                school_data.append(school.to_dict())

        if school_data:
            session['school_data'] = school_data 
            return redirect(url_for('compare_school_after'))  
        else:
            error_msg = "No schools were found. Please try again."
            return render_template('compare_school_after.html', error=error_msg)
    else:
        school_data = session.get('school_data', [])
        year = request.args.get('year','20')
        if school_data:
            image_path = create_bar_chart(school_data, year)
            return render_template('compare_school_after.html', school_data=school_data, year=year, image_file=image_path)
        else:
            return redirect(url_for('home'))
        

@app.route('/scrape_spotcrime_top')
def scrape_spotcrime_top_route():
    global scrape_thread, stop_scraping_event

    # Check if the scraping thread is already running
    if scrape_thread is not None and scrape_thread.is_alive():
        return render_template('scrape_status.html', message="Scraping is already in progress.")

    # Reset the stop event in case it was set before
    stop_scraping_event.clear()

    # Start the scraping in a background thread
    scrape_thread = threading.Thread(target=scrape_spotcrime, kwargs={'top': True})
    scrape_thread.start()

    # Inform the user that scraping has started
    return render_template('scrape_status.html', message="Top University SpotCrime data scraping has started.")

# Route to scrape latitude and longitude for top universities
@app.route('/scrape_latitude_and_longitude')
def scrape_latitude_and_longitude():
    global scrape_thread

    # Check if the thread is already running
    if scrape_thread is not None and scrape_thread.is_alive():
        return render_template('scrape_status.html', message="Latitude and Longitude scraping is already in progress.")
    
    # Start the scraping in a background thread
    scrape_thread = threading.Thread(target=get_top_universities_latlong)
    scrape_thread.start()

    # Inform the user that scraping has started
    return render_template('scrape_status.html', message="Latitude and Longitude scraping has started.")


@app.route('/stop_scraping')
def stop_scraping():
    global stop_scraping_event

    # Set the stop flag to signal the thread to stop
    stop_scraping_event.set()

    # Inform the user that scraping will stop
    return render_template('scrape_status.html', message="SpotCrime data scraping is stopping...")
    
# Route to serve static files (like crime_map.html, heatmap.html)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(static_dir, filename)

if __name__ == "__main__":
    app.run(debug=True)

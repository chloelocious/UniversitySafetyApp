from flask import Flask, render_template, request, send_from_directory, session, redirect, url_for
import os
import threading
import pandas as pd
from visualizations import plot_layered_crime_map, plot_crime_heatmap, plot_trend_analysis, plot_crime_distribution, trend_analysis_over_time, plot_top_universities_crime_info, plot_crime_distribution_top, plot_crime_by_top_university, clean_coordinates, plot_crime_vs_income, plot_income_crime_map, plot_crime_amount_vs_income
from crime_scrap import scrape_spotcrime
from global_vars import stop_scraping_event, current_lat_lon
from get_dataframe import get_dataframe, create_bar_chart, create_bar_chart_state
from university_latlong import get_top_universities_latlong

app = Flask(__name__)
scrape_thread = None
app.secret_key = 'PythonProject'

# paths to datasets for crime mapping
file_paths = [
    './Crime2023EXCEL/filtered_geocoded_Oncampusarrest202122.csv',
    './Crime2023EXCEL/filtered_geocoded_Noncampuscrime202122.csv',
    './Crime2023EXCEL/filtered_geocoded_Publicpropertyarrest202122.csv',
]

crime_info_path = './Crime_uptodate/crime_info.csv'
static_dir = 'static'

# home route -- shows menu options
@app.route('/')
def index():
    return render_template('home.html')

# route to show the layered crime map
@app.route('/crime_map')
def crime_map():
    crime_map_path = plot_layered_crime_map(file_paths) 
    return render_template('map.html', map_file=os.path.basename(crime_map_path), title = "University Crime Map (On Campus Arrests, Non Campus Crimes, Public Property Arrests)")

# route to show the crime heatmap
@app.route('/crime_heatmap')
def crime_heatmap():
    heatmap_path = plot_crime_heatmap(file_paths)
    return render_template('map.html', map_file=os.path.basename(heatmap_path), title = "University Crime Heatmap")

# route to show trend analysis
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

# route to show crime distribution
@app.route('/crime_distribution')
def crime_distribution():
    df = pd.read_csv(crime_info_path)
    distribution_html = plot_crime_distribution(df)
    return render_template('visualization.html', chart_html=distribution_html, title="Crime Category Distribution")

# route to show the crime map of top universities
@app.route('/crime_map_top')
def crime_map_top():
    title = "Top University Crime Map"
    crime_map_path = plot_top_universities_crime_info()  # Correct function for top universities map
    return render_template('map.html', map_file=os.path.basename(crime_map_path), page_title = title)

# route for crime types by top university
@app.route('/trend_analysis_top')
def trend_analysis_top():
    trend_analysis_html = plot_crime_by_top_university()
    return render_template('visualization.html', chart_html=trend_analysis_html, title="Crimes by Top Universities")

# route for crime category distribution of top universities
@app.route('/crime_distribution_top')
def crime_distribution_top():
    crime_distribution_html = plot_crime_distribution_top()
    return render_template('visualization.html', chart_html=crime_distribution_html, title="Crime Category Distribution of Top Universities")

# route to display raw data of all the universities and associated crimes
@app.route('/raw_data')
def display_raw_data_all():
    all_universities_file = './Crime_uptodate/crime_info.csv'
    df = pd.read_csv(all_universities_file)
    table_html = df.to_html(index=False, classes='table table-striped')
    return render_template('raw_data.html', table=table_html, title="Raw Data: All Universities")

# route to display raw data of the top universities and associated crimes
@app.route('/raw_data_top')
def display_raw_data_top():
    crime_file = './Crime_uptodate/crime_info_top.csv'
    university_file = './Crime_uptodate/filtered_data_top.csv'
    print(os.path.exists(crime_file))

    crime_df = pd.read_csv(crime_file)
    university_df = pd.read_csv(university_file)
    print(crime_df.head()) 

    # clean lat and long columns
    crime_df = clean_coordinates(crime_df, 'Latitude')
    crime_df = clean_coordinates(crime_df, 'Longitude')
    university_df = clean_coordinates(university_df, 'Latitude')
    university_df = clean_coordinates(university_df, 'Longitude')
    
    print(crime_df.head())
    print(university_df.head())
    print("Crime Data Shape:", crime_df.shape)
    print("University Data Shape:", university_df.shape)

    # merge on lat and long to include university names
    merged_df = pd.merge(crime_df, university_df, on=['Latitude', 'Longitude'], how='left')
    print(merged_df.head())

    table_html = merged_df.to_html(index=False, classes='table table-striped')
    return render_template('raw_data.html', table=table_html, title="Raw Data: Top Universities")

# route to display raw data of the top median household income and crimes by address
@app.route('/raw_data_income')
def display_raw_data_income():
    merged_income_file = './Crime_uptodate/merged_crime_income_data.csv'
    df = pd.read_csv(merged_income_file)

    table_html = df.to_html(index=False, classes='table table-striped')
    return render_template('raw_data.html', table=table_html, title="Raw Data: Crime Data Merged with Median Household Income Data")

# route to display raw data of the crime category definitions
@app.route('/raw_data_crime_definitions')
def display_raw_data_crime_definitions():
    definition_file = './Crime_uptodate/crime_definitions.csv'
    df = pd.read_csv(definition_file)

    table_html = df.to_html(index=False, classes='table table-striped')
    return render_template('raw_data.html', table=table_html, title="Raw Data: Crime Definitions Scraped from Wikipedia")

# route to start SpotCrime scraping
@app.route('/scrape_spotcrime')
def scrape_spotcrime_route():
    global scrape_thread, stop_scraping_event

    # check if the scraping thread is already running
    if scrape_thread is not None and scrape_thread.is_alive():
        return render_template('scrape_status.html', message="Scraping is already in progress.")

    # reset the stop event
    stop_scraping_event.clear()

    # start the scraping in a background thread
    scrape_thread = threading.Thread(target=scrape_spotcrime, kwargs={'top': False})
    scrape_thread.start()

    return render_template('scrape_status.html', message="SpotCrime data scraping has started.")

# route to display compare schools functionality
@app.route('/compare_school')
def compare_school():
    return render_template('compare_school.html')

# route to display compare by state functionality
@app.route('/compare_state')
def compare_state():
    return render_template('compare_state.html')

# route to display the results of comparing schools (with visualizations)
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
        
# route to display the results of comparing by state (with visualizations)
@app.route('/compare_state_after', methods=['GET', 'POST'])
def compare_state_after():
    if request.method == 'POST':
        states = request.form.getlist('states')

        df = get_dataframe() 
        state_data = {}

        for state_name in states:
            state_schools_df = df[df['State'].str.lower() == state_name.lower()]
            unique_schools = state_schools_df['INSTNM'].unique()
            if len(unique_schools) > 0:
                state_data[state_name.upper()] = unique_schools.tolist()

        if state_data:
            session['state_data'] = state_data  
            return redirect(url_for('compare_state_after'))
        else:
            error_msg = "No states were found. Please try again."
            return render_template('compare_state_after.html', error=error_msg)
    else:
        state_data = session.get('state_data', {})
        year = request.args.get('year', '20')
        if state_data:
            image_path = create_bar_chart_state(state_data, year)
            return render_template('compare_state_after.html', state_data=state_data, year=year, image_file=image_path)
        else:
            return redirect(url_for('home'))

# route to start SpotCrime scraping for top universities
@app.route('/scrape_spotcrime_top')
def scrape_spotcrime_top_route():
    global scrape_thread, stop_scraping_event

    # check if the scraping thread is already running
    if scrape_thread is not None and scrape_thread.is_alive():
        return render_template('scrape_status.html', message="Scraping is already in progress.")

    # reset the stop event in case it was set before
    stop_scraping_event.clear()

    scrape_thread = threading.Thread(target=scrape_spotcrime, kwargs={'top': True})
    scrape_thread.start()

    return render_template('scrape_status.html', message="Top University SpotCrime data scraping has started.")

# route to scrape latitude and longitude for top universities
@app.route('/scrape_latitude_and_longitude')
def scrape_latitude_and_longitude():
    global scrape_thread

    # check if the thread is already running
    if scrape_thread is not None and scrape_thread.is_alive():
        return render_template('scrape_status.html', message="Latitude and Longitude scraping is already in progress.")
    
    scrape_thread = threading.Thread(target=get_top_universities_latlong)
    scrape_thread.start()

    return render_template('scrape_status.html', message="Latitude and Longitude scraping has started.")

# route to display the scraping has stopped page
@app.route('/stop_scraping')
def stop_scraping():
    global stop_scraping_event

    # set the stop flag to signal the thread to stop
    stop_scraping_event.set()

    return render_template('scrape_status.html', message="SpotCrime data scraping is stopping...")
    
# route for crime vs income bar chart
@app.route('/crime_vs_income')
def crime_vs_income():
    df = pd.read_csv('./Crime_uptodate/merged_crime_income_data.csv')
    crime_vs_income_html = plot_crime_vs_income(df)
    return render_template('visualization.html', chart_html=crime_vs_income_html, title="Crime vs Median Household Income")

# route for crime count vs income bar chart
@app.route('/crime_amount_vs_income')
def crime_amount_vs_income():
    df = pd.read_csv('./Crime_uptodate/merged_crime_income_data.csv')
    crime__amount_vs_income_html = plot_crime_amount_vs_income(df)
    return render_template('visualization.html', chart_html=crime__amount_vs_income_html, title="Crime Amount vs Median Household Income")

# route for crime locations with median household income on a map
@app.route('/income_crime_map')
def income_crime_map():
    df = pd.read_csv('./Crime_uptodate/merged_crime_income_data.csv')
    map_path = plot_income_crime_map(df)
    return render_template('map.html', map_file=os.path.basename(map_path), title="Crime and Median Household Income Map")

# route for static files (like crime_map.html, heatmap.html)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(static_dir, filename)

if __name__ == "__main__":
    app.run(debug=True)

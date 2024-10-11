# UniversitySafety

```
 _   _       _                    _ _           ____         __      _         
| | | |_ __ (_)_   _____ _ __ ___(_) |_ _   _  / ___|  __ _ / _| ___| |_ _   _ 
| | | | '_ \| \ \ / / _ \ '__/ __| | __| | | | \___ \ / _` | |_ / _ \ __| | | |
| |_| | | | | |\ V /  __/ |  \__ \ | |_| |_| |  ___) | (_| |  _|  __/ |_| |_| |
 \___/|_| |_|_| \_/ \___|_|  |___/_|\__|\__, | |____/ \__,_|_|  \___|\__|\__, |
                                        |___/                            |___/ 
```

The need for our application comes from the fact that though there may be resources that have crime data for universities, there are not sources that place universities in context of the larger city that surrounds them. Having an application for this will allow users to make a better-informed decision on where they choose to attend university.

There is not a current solution to this need. Most universities publish crime data in the form of just a table, or there may be visualizations but none that include local crime outside of the university.

This project did not cost anything, as all the data we need is publicly available, and we only had to merge, clean, and visualize the data.

The current problem is due to a lack of a better understanding of a city’s local crime statistics. University crime itself does not paint the whole picture of a student’s safety in their new university life. This application will be helpful for prospective students, families, and researchers in understanding the relationship between local crime and university crime. 

## Run
To run the project, run the app.py in the **flask_app** folder.
```{sh}
python flask_app/app.py
```

## Installaton

We suggest you to create a virtual environment.

### 1. Create a Virtual Environment
Use Python's built-in `venv` module to create a virtual environment. Run the following command in the terminal:

```{sh}
python -m venv myenv
```

Here, myenv is the name of the virtual environment, and you can replace it with any name you prefer.

### 2. Activate the Virtual Environment
The method to activate the virtual environment depends on your operating system:

**Windows:**
```{sh}
myenv\Scripts\activate
```

**macOS/Linux:**

```{sh}
source myenv/bin/activate
```

### 3. Install Dependencies
Once activated, you can use pip to install all the dependencies needed

```{sh}
pip install -r requirements.txt
```


# Data Scriping

## Data Source

### 1. CSS (Campus Security and Safety)
**Source:** [CSS](https://ope.ed.gov/campussafety/#/datafile/list)

**Data Description:** This source has data reported from each college and university nationwide from 2020 – 2022. It has many files included, but the three csv files we’re using are campus arrests, non campus crimes, and public property crimes.

**Acquisition:** To gather the data. We first use the `requests` library in Python to download the .zip file via the provided download link. Then, we unzip the file and convert the extracted Excel file into a CSV format using `pandas`.

### 2. Latitude and Longtitude coordinates of universities
**Source:** [Find Latitude and Longtitude](https://www.findlatitudeandlongitude.com/)

**Method:** [Convert Latlong](https://github.com/chloelocious/UniversitySafetyApp/blob/main/convert_latlong.py)


**Data Description:**  For each address in the CSS data, we use web-scraping to merge crime data with the latitude and longitude coordinates of those addresses. With latitude and longitude coordinates of universities, we can do further investigation and data sourcing.

**Acquisition:** This data was obtained by taking the addresses of all the universities in the CSS data, and then using both the python library `geopy` and web-scraping from [Latlong.net](https://www.latlong.net/convert-address-to-lat-long.html)



### 3. US Top Universities
**Source:** [USNEWS](https://www.usnews.com/best-colleges/rankings/national-universities)
**Method:** [Get Top Universities Latlong](https://github.com/chloelocious/UniversitySafetyApp/blob/main/flask_app/university_latlong.py)

**Data Description:** This data describes schools in the National Universities category that offer a full range of undergraduate majors, plus master's and doctoral programs. We used this data to filter the complete university data csv file into the subset of top universities.

**Acquisition:** The function use `requests` to download the Excel file and saved locally in binary mode ('wb'). Once the file is successfully downloaded, the function loads the Excel file to inspect the available sheet names (xls.sheet_names). Finally, it reads the specific sheet named 'Top 150 National Universities' into a DataFrame and gets the names of the universities listed in the 'University Name' column.


### 4. Spot Crime
**Source:** [Spot Crime](https://spotcrime.com/)
**Method:** [Scrape Spotcrime](https://github.com/chloelocious/UniversitySafetyApp/blob/main/flask_app/crime_scrap.py)

**Data Description:** SpotCrime is a public facing crime map and crime alert service. We can use SpotCrime to look up city and county crime data given specific location.

**Acquisition:** We first use the `pandas` library to load the filtered university data from a CSV file. Then, we use the `os` library to check if the output file already exists and load any previously scraped data to avoid duplicate entries. After that, we initialize the web driver using `selenium.webdriver` to open a browser for web scraping. For each unique latitude and longitude pair, we navigate to the SpotCrime map URL and use `selenium` to interact with the webpage and extract crime data by clicking on relevant buttons. By gathering the crime URLs in the table, we can use the `requests` library to retrieve individual crime details from the crime URLs, and `BeautifulSoup` to parse the HTML and extract crime information such as type, date, description, and address.

### 5. Median Household Income
**Source:** [Spot Crime](https://spotcrime.com/)
**Method:** [Get Median Household Income](https://github.com/chloelocious/UniversitySafetyApp/blob/main/Web%20Scraping/census_scrape.py)

**Data Description:** The data describes the median household income for specific city.

**Acquisition:** We first load the existing CSV file containing crime information using  `pandas`. For each row in the CSV, we extract the address and use simple string manipulation to create the DataUSA URL based on a city and state. Then, we use the `requests` library to fetch the webpage from this constructed URL. After that, we use `BeautifulSoup` to parse the HTML content of the webpage and locate the median household income data for the year 2022. If the data is found, we extract it.

## 6. Wikipedia definitions of crimes in data
**Source:** [Wikipedia](https://www.wikipedia.org/)
**Method:** [Get Wikipedia_Definition](https://github.com/chloelocious/UniversitySafetyApp/blob/main/Web%20Scraping/wikipedia_scrape.py)

**Data Description:** The data describes the median household income for specific city.

**Acquisition:** The method first initializes the Wikipedia API using the `wikipediaapi` library, and it sets a custom user agent to ensure compliance with Wikipedia’s API policies. Once the API is initialized, it attempts to fetch the Wikipedia page for the given crime category using `wiki.page(crime_category)`.

If the page exists, the function retrieves a summary of the page’s content through the page.summary attribute, which provides a brief definition of the crime category. This summary is then returned as the result.

# Data Visualization
We use various data visualization tools to give a whole view of nationwide university safety statistics.

## Nationwide University Crime Data Visualizations

In this section, we present visualizations of crime data surrounding universities across the country.

### View Layered Crime Map
This page is designed to display crime incidents across the U.S. Each crime event is marked as a point on the map, allowing users to zoom in to explore specific locations or zoom out to see the overall crime distribution across regions.

### View Crime Heatmap
To provide a clearer view of crime distribution across the nation, we further utilize a Heatmap to represent the total number of crimes in different areas, giving a more intuitive understanding of crime concentration.

### View Crime Trend Analysis
In this section, we use a descending bar chart to showcase the statistical data of different crime incidents, allowing users to easily see which types of crimes are more prevalent.

### View Crime Trend Analysis Over Time
Using a line chart, we visualize the crime rate trends over time, helping to understand how crime levels fluctuate during different periods.

### View Crime Category Distribution
We employ a pie chart to effectively display the proportion of various crime categories within the total crime data. Compared to bar charts, this type of visualization offers a clearer representation of the distribution of crime types across the dataset.

## Highest Ranking Universities Crime Data (Source: U.S. News)

Due to issues such as anti-scraping mechanisms and pop-up ads on crime data websites, we were unable to obtain data for all universities across the U.S. As a result, we focused our dataset on universities featured in the U.S. News rankings. This allows us to present a more detailed visualization centered around the crime data of these top-ranked institutions.

### View Crime Map of Top Universities
This section displays the crime map for all U.S. News-ranked universities. We use a different type of map visualization, where crime incidents are plotted individually on the map. Due to the large amount of data processing involved in fetching and plotting each crime record, the loading time may be slower.

### View Crime Trends by Each Top University
This dynamic page displays the crime data surrounding each university, switching between schools every second. The data is aggregated based on university names, and statistical information for different types of crimes is visualized in bar charts, allowing users to observe trends for individual institutions.

### View Crime Category Distribution of Top Universities
In this section, we use pie charts to represent the crime distribution around the top universities, offering a clear view of how different types of crimes are proportionally distributed across these institutions.

## University Crime Data Functions

To help users better understand the structure of the raw data we collected and aggregated, this section provides access to both the original data and the scraping functions. Users can run the scraping function to directly update the raw dataset of the project.

### Display Raw Data: All Universities
This section visually displays the raw crime data for all universities in a table format, allowing users to explore the dataset directly on the webpage.

### Display Raw Data: Top Universities
This section visually displays the raw crime data for top-ranked universities in a table format, providing a clear view of the data structure for these institutions.

### Display Raw Data: Crime Merged with Median Household Income
This section shows the merged data combining crime information around top universities with median household income, displayed in a table format for easy exploration.

### Display Raw Data: Crime Definitions Provided by Wikipedia
This section offers definitions for various crime types sourced from Wikipedia, helping users better understand the specific nature of each crime category.

### Scrape Latitude and Longitude Coordinates
This button allows users to scrape the latitude and longitude coordinates corresponding to the addresses in the raw data CSV file, automating the process of geolocating crime incidents.

## University Safety Comparisons

This section allows for the comparison of crime data between different universities and U.S. states.

### Compare Between Schools
Input the names of any number of schools you're interested in—just enter the most distinctive part of each school's name. This function will automatically search for the full names of the universities and compare their crime data using bar charts. By selecting different years, you can compare how crime rates around these schools have changed over time.

### Compare Between States
Select multiple U.S. states of interest, and this function will generate bar chart comparisons of crime data within those states. By selecting different years, you can explore how crime rates in these states have evolved over time.

## University Crime and Median Household Income

This section combines each city's median household income data to analyze the relationship between income levels and crime rates.

### View Crime and Median Household Income
In this part, we use box plots to visually display the median household income of cities for different types of crimes. Each point on the plot represents a crime incident, providing insight into the income levels associated with various crime types.

### Compare Crime Amount and Median Household Income
We plot a scatter chart comparing the number of crimes in each city with its median household income, and fit a trend line to the data. The results show a clear pattern where lower income levels are associated with higher crime rates. The fitted line illustrates this correlation.

### View Crime Map with Median Household Income
This section displays a Heatmap of crime incidents across cities, with each city marked by its median household income, allowing for a geographic comparison of crime levels and income distribution.


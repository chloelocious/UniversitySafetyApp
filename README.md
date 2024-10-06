# UniversitySafety

Our final project idea is to make an application that analyzes and displays nationwide university safety statistics. We will primarily a source that has nationwide United States crime data for universities, and we will merge this data with web-scraped / API-retrieved local crime data from universities of major cities. We will determine this by merging the university city locations with scraped census data, and filtering cities that meet a population number criteria to be deemed as a large city. 

After the data is collected, cleaned, and merged, we will make a Python application that displays visualizations of the crimes by type / classification, crime heatmaps, and other types of summary statistics such as crime comparison by region or crime prediction using linear regression analysis.

The user will input their choice for what visualization or statistical analysis they would like to see, and our application will keep running until the user chooses to quit.



## Installaton

We suggest you to create a virtual environment.

## 1. Create a Virtual Environment
Use Python's built-in `venv` module to create a virtual environment. Run the following command in the terminal:

```{sh}
python -m venv myenv
```

Here, myenv is the name of the virtual environment, and you can replace it with any name you prefer.

## 2. Activate the Virtual Environment
The method to activate the virtual environment depends on your operating system:

**Windows:**
```{sh}
myenv\Scripts\activate
```

**macOS/Linux:**

```{sh}
source myenv/bin/activate
```

## 3. Install Dependencies
Once activated, you can use pip to install all the dependencies needed

```{sh}
pip install -r requirements.txt
```

# Data Scriping

## Data Source

### 1. CSS (Campus Security and Safety)
Source: [CSS](https://ope.ed.gov/campussafety/#/datafile/list)
Data Description: 

Acquisition: [Create a scarping file for Crime2023Excel raw data.]

### 2. Find Latitude and Longtitude
Source: [Find Latitude and Longtitude](https://www.findlatitudeandlongitude.com/)
Data Description:

Acquisition: [Web Scraping/lat_long_webscrape.ipynb] 

### 3. Spot Crime
Source: [Spot Crime](https://spotcrime.com/)
Data Description:

Acquisition: 

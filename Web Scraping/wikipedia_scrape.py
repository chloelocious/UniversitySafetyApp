import requests
from bs4 import BeautifulSoup
import csv

# function to get the Wikipedia definition for a crime category
def get_wikipedia_definition(crime_category):
    try:
        # wikipedia URL for the crime category
        base_url = "https://en.wikipedia.org/wiki/"
        url = base_url + crime_category.replace(" ", "_")

        response = requests.get(url)
        if response.status_code != 200:
            return f"Error: Could not retrieve page for {crime_category}"

        # parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            if p.text.strip():  # Skip empty or whitespace paragraphs
                definition = p.text.strip()
                return definition

        return f"No definition found for {crime_category}"
    
    except Exception as e:
        return f"Error scraping {crime_category}: {str(e)}"

# crime categories list
crime_categories = ['Theft', 'Shooting', 'Vandalism', 'Larceny', 'Assault', 'Burglary', 'Robbery', 'Arson']
data = []

# scrape the definition for each crime category and store it in data list
for crime in crime_categories:
    definition = get_wikipedia_definition(crime)
    data.append([crime, definition])  

csv_file = 'crime_definitions.csv'

with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Crime Category', 'Definition']) 
    writer.writerows(data) 

print(f"Definitions have been saved to {csv_file}")

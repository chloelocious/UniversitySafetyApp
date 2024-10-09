import requests
from bs4 import BeautifulSoup
import csv

# Function to get the Wikipedia definition for a crime category
def get_wikipedia_definition(crime_category):
    try:
        # Generate the Wikipedia URL for the crime category
        base_url = "https://en.wikipedia.org/wiki/"
        url = base_url + crime_category.replace(" ", "_")

        # Fetch the page content
        response = requests.get(url)
        if response.status_code != 200:
            return f"Error: Could not retrieve page for {crime_category}"

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Try to find the first non-empty paragraph with text (may not always be the first <p> tag)
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            if p.text.strip():  # Skip empty or whitespace paragraphs
                definition = p.text.strip()
                return definition

        # Fallback if no valid paragraph is found
        return f"No definition found for {crime_category}"
    
    except Exception as e:
        return f"Error scraping {crime_category}: {str(e)}"

# List of crime categories
crime_categories = ['Theft', 'Shooting', 'Vandalism', 'Larceny', 'Assault', 'Burglary', 'Robbery', 'Arson']

# Prepare data for saving into CSV
data = []

# Scrape the definition for each crime category and store it in data list
for crime in crime_categories:
    definition = get_wikipedia_definition(crime)
    data.append([crime, definition])  # Store crime category and its definition

# Save the data to a CSV file
csv_file = 'crime_definitions.csv'

with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Crime Category', 'Definition'])  # Write headers
    writer.writerows(data)  # Write the rows with crime categories and definitions

print(f"Definitions have been saved to {csv_file}")

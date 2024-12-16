import requests
from bs4 import BeautifulSoup
import random

# Function to get a list of phone URLs from GSMArena
def get_phone_urls():
    url = "https://www.gsmarena.com/makers.php3"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all links to manufacturers and their models
    phone_links = soup.find_all("a", class_="brandmenu-v2-item")
    
    # Randomly select ten phones from the list
    selected_phones = random.sample(phone_links, 10)
    
    return [link.get('href') for link in selected_phones]

# Function to scrape details of a phone
def get_phone_details(phone_url):
    base_url = "https://www.gsmarena.com"
    url = base_url + phone_url
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract phone details (e.g., name, specs, price)
    name = soup.find("h1").text.strip()
    specs_section = soup.find_all("td", class_="specs-phone-name-title")
    specs_text = [spec.text.strip() for spec in specs_section]
    
    # Price (optional, may not be available on all pages)
    price_section = soup.find("span", class_="price")
    price = price_section.text.strip() if price_section else "Price not available"
    
    # Return the phone details as a dictionary
    phone_details = {
        "name": name,
        "price": price,
        "specifications": specs_text
    }
    
    return phone_details

# Main function to execute the scraping and return results
def execute():
    phone_urls = get_phone_urls()
    all_phone_details = []
    
    for phone_url in phone_urls:
        phone_details = get_phone_details(phone_url)
        all_phone_details.append(phone_details)
    
    return all_phone_details

# Call the function to get phone details


# The `phone_data` variable now contains the details of 10 phones in a structured format.

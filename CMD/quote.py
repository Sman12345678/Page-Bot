import requests
from bs4 import BeautifulSoup
import random
Info = {
    "Description":"Get Random quotes to Motivate you"
}

def execute():
    # Scrape quotes from the website
    url = "http://quotes.toscrape.com/"
    response = requests.get(url)
    
    # Check if the page is accessible
    if response.status_code != 200:
        return "⚠️ Unable to access the quotes website at the moment. Please try again later."

    # Parse HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    quotes = soup.find_all("div", class_="quote")

    if not quotes:
        return "⚠️ No quotes found on the page."

    # Randomly select a quote
    selected_quote = random.choice(quotes)
    quote_text = selected_quote.find("span", class_="text").get_text()
    author = selected_quote.find("small", class_="author").get_text()
    tags = [tag.get_text() for tag in selected_quote.find_all("a", class_="tag")]

    # Format the quote in a visually appealing way
    response = (
        f"🌟 **Inspiring Quote of the Moment** 🌟\n\n"
        f"\"{quote_text}\"\n\n"
        f"— **{author}**\n\n"
        f"🔖 **Tags**: {', '.join(tags) if tags else 'No tags available'}\n\n"
        f"💬 _Remember, a quote a day keeps negativity away!_ 💫"
    )

    return response

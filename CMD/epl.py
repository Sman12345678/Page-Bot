import requests
from bs4 import BeautifulSoup

Info = {
    "Description":"Get News About English Premier League"
}
def execute():
    # Define the URL to scrape for EPL news from Sky Sports
    url = "https://www.skysports.com/premier-league-news"

    # Send HTTP request to the URL
    response = requests.get(url)

    # Check if the page is accessible
    if response.status_code != 200:
        return "⚠️ Unable to access the Sky Sports website at the moment. Please try again later."
    
    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all news articles (Sky Sports website structure may change, so this selector is based on current structure)
    news_articles = soup.find_all('a', class_='news-list__headline-link')

    # Check if there are any news articles
    if not news_articles:
        return "⚠️ No latest news found."

    # Collect the titles and links to the news articles
    news_list = []
    for article in news_articles[:5]:  # Limit to the first 5 articles
        title = article.get_text().strip()
        link = "https://www.skysports.com" + article['href']
        news_list.append(f"🔹 {title} - [Read More]({link})")

    # Format the output
    response = "⚽ **Latest EPL News from Sky Sports** ⚽\n\n"
    response += "\n".join(news_list)

    # Fetch live matches if available
    live_matches_url = "https://www.skysports.com/live-scores/football"
    live_response = requests.get(live_matches_url)
    
    if live_response.status_code == 200:
        live_soup = BeautifulSoup(live_response.text, 'html.parser')
        live_matches = live_soup.find_all('div', class_='fixres__item')

        if live_matches:
            response += "\n\n🔥 **Live Matches** 🔥\n"
            for match in live_matches[:3]:  # Limit to 3 live matches
                teams = match.find('span', class_='matches__item-col--team-name').get_text().strip()
                score = match.find('span', class_='matches__item-col--scores').get_text().strip()
                response += f"⚡ {teams} - {score}\n"
        else:
            response += "\n\n🔥 No live matches currently."

    return response

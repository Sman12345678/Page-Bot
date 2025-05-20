import requests
from bs4 import BeautifulSoup
 # Reuse sender_id from app.py

Info={
"Description":"Top 10 headlines from BBC"
}

def scrape_news():
    url = "https://www.bbc.com/news"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []
    for item in soup.select('.gs-c-promo', limit=10):  # Get top 5 stories
        title = item.select_one('.gs-c-promo-heading__title')
        link = item.select_one('a')
        image = item.select_one('img')

        if title and link:
            articles.append({
                'title': title.text.strip(),
                'link': f"https://www.bbc.com{link['href']}" if link['href'].startswith('/') else link['href'],
                'image': image['src'] if image and 'src' in image.attrs else None
            })

    return articles

def execute(message=None,sender_id=None):
    news_items = scrape_news()

    elements = []
    for item in news_items:
        elements.append({
            "title": item['title'],
            "image_url": item['image'] or "https://via.placeholder.com/300x200?text=No+Image",
            "subtitle": "Tap to read full article.",
            "default_action": {
                "type": "web_url",
                "url": item['link'],
                "webview_height_ratio": "full"
            },
            "buttons": [
                {
                    "type": "web_url",
                    "url": item['link'],
                    "title": "Read More"
                }
            ]
        })

    return {
        "recipient": {"id": sender_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": elements
                }
            }
        }
    }

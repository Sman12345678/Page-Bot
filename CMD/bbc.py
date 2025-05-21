import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more verbose output
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

Info = {
    "Description": "Top 10 headlines from BBC"
}

def scrape_news():
    url = "https://www.bbc.com/news"
    try:
        logger.info(f"Requesting BBC News page: {url}")
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch BBC News: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')

    articles = []
    items = soup.select('.gs-c-promo')
    logger.info(f"Found {len(items)} news items on the page.")
    for item in items[:10]:  # Get top 10 stories
        title = item.select_one('.gs-c-promo-heading__title')
        link = item.select_one('a')
        image = item.select_one('img')

        if title and link:
            article = {
                'title': title.text.strip(),
                'link': f"https://www.bbc.com{link['href']}" if link['href'].startswith('/') else link['href'],
                'image': image['src'] if image and 'src' in image.attrs else None
            }
            logger.debug(f"Article parsed: {article}")
            articles.append(article)
        else:
            logger.debug("Skipped an item due to missing title or link.")

    logger.info(f"Returning {len(articles)} articles.")
    return articles

def execute(message=None, sender_id=None):
    logger.info("Executing BBC command.")
    try:
        news_items = scrape_news()
    except Exception as e:
        logger.error(f"Error in scrape_news: {e}")
        return {
            "recipient": {"id": sender_id},
            "message": {"text": f"❌ Could not fetch BBC news: {e}"}
        }

    if not news_items:
        logger.warning("No news items were returned.")
        return {
            "recipient": {"id": sender_id},
            "message": {"text": "❌ No news could be fetched from BBC at this time."}
        }

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

    logger.info("Returning news carousel to user.")
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

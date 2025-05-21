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
    "Description": "Top BBC News headlines from bbc.com/news with images, links, and descriptions"
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
    # Main news container
    main_container = soup.find(class_="sc-464f550b-2 iEUdAz")
    if not main_container:
        logger.warning("Main BBC news container not found.")
        return []

    news_items = main_container.find_all(class_="sc-225578b-0 btdqbl")
    logger.info(f"Found {len(news_items)} news items in the main container.")

    for item in news_items[:10]:  # Limit to top 10
        # Link
        a_tag = item.find("a", class_="sc-8a623a54-0 hMvGwj")
        link = a_tag["href"] if a_tag and a_tag.has_attr("href") else None
        if link and link.startswith("/"):
            link = "https://www.bbc.com" + link

        # Title (also inside <a>)
        title = a_tag.get_text(strip=True) if a_tag else None

        # Image
        img_tag = item.find("img", class_="sc-4abb68ca-0 ldLcJe")
        image_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else None

        # Description
        desc_tag = item.find("p", class_="sc-cb78bbba-0 klCBmG", attrs={"data-testid": "card-description"})
        description = desc_tag.get_text(strip=True) if desc_tag else None

        if title and link:
            article = {
                'title': title,
                'link': link,
                'image': image_url or "https://via.placeholder.com/300x200?text=No+Image",
                'description': description or ""
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
            "image_url": item['image'],
            "subtitle": item['description'] or "Tap to read full article.",
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

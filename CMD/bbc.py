import requests
from bs4 import BeautifulSoup
import logging
from io import BytesIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
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
    main_container = soup.find(class_="sc-464f550b-2 iEUdAz")
    if not main_container:
        logger.warning("Main BBC news container not found.")
        return []

    news_items = main_container.find_all(class_="sc-225578b-0 btdqbl")
    logger.info(f"Found {len(news_items)} news items in the main container.")

    for item in news_items[:10]:
        a_tag = item.find("a", class_="sc-8a623a54-0 hMvGwj")
        link = a_tag["href"] if a_tag and a_tag.has_attr("href") else None
        if link and link.startswith("/"):
            link = "https://www.bbc.com" + link
        title = a_tag.get_text(strip=True) if a_tag else None
        img_tag = item.find("img", class_="sc-d1200759-0 dvfjxj")
        image_url = img_tag["src"] if img_tag and img_tag.has_attr("src") else None
        desc_tag = item.find("p", class_="sc-cb78bbba-0 klCBmG", attrs={"data-testid": "card-description"})
        description = desc_tag.get_text(strip=True) if desc_tag else None

        if title and link:
            articles.append({
                'title': title,
                'link': link,
                'image': image_url,
                'description': description or ""
            })
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
        return [{"type": "text", "data": f"❌ Could not fetch BBC news: {e}", "success": False}]

    if not news_items:
        logger.warning("No news items were returned.")
        return [{"type": "text", "data": "❌ No news could be fetched from BBC at this time.", "success": False}]

    results = []
    for idx, item in enumerate(news_items, 1):
        # Add image if available
        if item["image"]:
            try:
                img_resp = requests.get(item["image"])
                img_resp.raise_for_status()
                img_bytes = BytesIO(img_resp.content)
                results.append({"type": "image", "data": img_bytes, "success": True})
            except Exception as e:
                logger.warning(f"Could not fetch image: {item['image']} ({e})")
        # Add text for each news item
        text = f"{idx}. {item['title']}\n{item['link']}"
        if item["description"]:
            text += f"\n    {item['description']}"
        results.append({"type": "text", "data": text, "success": True})

    return results
    

import requests as Sman

Info = {
    "Description": "Get the latest news headlines from around the world."
}

SMAN_API_KEY = '2700cb22fb254ad9b409ff1ff6bc9278'
SMAN_NEWS_URL = 'https://newsapi.org/v2/top-headlines'

def execute(message=None):
    """
    Fetch and return the top 5 news headlines from the specified country.
    """
    # Default country
    country =  'us'
    try:
        response = Sman.get(f"{SMAN_NEWS_URL}?country={country}&apiKey={SMAN_API_KEY}")
        data = response.json()
        
        # Check API status
        if data.get('status') != 'ok':
            return f"⚠️ Error: {data.get('message', 'An unknown error occurred.')}"
        
        # Extract the top 5 headlines
        articles = data.get('articles', [])
        if not articles:
            return "⚠️ No articles found for the specified country."
        
        # Format the top 5 headlines
        output = []
        output.append("✨ Top 5 Headlines ✨")
        output.append("╭───────────────────────────────╮")
        for i, article in enumerate(articles[:5], start=1):
            output.append(f"│ {i}. {article['title']}")
        output.append("╰───────────────────────────────╯")
        
        return "\n".join(output)
    except Exception as e:
        return f"⚠️ Error fetching news data: {e}"

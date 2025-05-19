# Please Do Not Misuse or Abuse API Key
import requests

Info = {
    "Description": "Perform Google Search"
}

def execute(message, sender_id=None):
    """
    Perform a Google search using the provided message text 
    and return the top results using Google Custom Search API.

    Args:
        message (str): The text to search for.
        num_results (int): Number of results to fetch.

    Returns:
        str: A formatted string containing the search results.
    ──────────────
    """

    if not message:
        return "❌ You Didn't Include A Search Query"
    
    api_key = "AIzaSyAqBaaYWktE14aDwDE8prVIbCH88zni12E"  # Your API key
    cx = "7514b16a62add47ae"  # Your Custom Search Engine ID
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={message}&num=5"

    response = requests.get(url)
    
    if response.status_code != 200:
        return "Failed to fetch search results"
    
    search_results = response.json().get('items', [])
    results = []

    results.append("────────────")
    for item in search_results:
        title = item.get('title', 'No title')
        link = item.get('link', 'No link')
        description = item.get('snippet', 'No description')

        results.append(f"⟢ ⚒️Title ⟣: {title}")
        results.append(f"⟢ 📎Link ⟣: {link}")
        results.append(f"⟢ 📋Description ⟣: {description}")
        results.append("────────────")
    
    return "\n".join(results)

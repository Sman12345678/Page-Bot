# Brain.py This File is Designed For The Purpose Of Making Bot Wiser Please Do Not Misuse or Abuse API Key
import requests
from flask import g  

def google_search(num_results=5):
    """
    Perform a Google search using the message_text from Flask's g object 
    and return the top results using Google Custom Search API.

    Args:
        num_results (int): Number of results to fetch.

    Returns:
        list: A list of dictionaries containing 'title', 'link', and 'description'.
    """
    
    query = getattr(g, 'message_text', '')  

    if not query:
        return [{"error": "No message text available"}]

    api_key = "AIzaSyAqBaaYWktE14aDwDE8prVIbCH88zni12E"  # Your API key
    cx = "7514b16a62add47ae"  # Your Custom Search Engine ID
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cx}&q={query}&num={num_results}"

    response = requests.get(url)
    
    if response.status_code != 200:
        return [{"error": "Failed to fetch search results"}]
    
    search_results = response.json().get('items', [])
    results = []
    
    for item in search_results:
        title = item.get('title', 'No title')
        link = item.get('link', 'No link')
        description = item.get('snippet', 'No description')
        
        results.append({"title": title, "link": link, "description": description})
    
    return results

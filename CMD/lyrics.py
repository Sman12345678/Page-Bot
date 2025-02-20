import requests

Info = {
    "Description": "Provide Lyrics For The Song Given"
}

def fetch_lyrics(song):
    """
    Fetches song details (lyrics, title, artist) from the API.
    
    :param song: The song name to search for.
    :return: A dictionary containing song details or an error message.
    """
    if not song:
        return {"success": False, "error": "❌ Please provide a song name."}
    
    url = f"https://kaiz-apis.gleeze.com/api/lyrics?title={song}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        if "lyrics" in data:
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": "🚨 No lyrics found for the provided song."}
    
    except requests.exceptions.RequestException as e:
        return {"success": False, "error": f"🚨 Error fetching lyrics: {str(e)}"}

def display_song(data):
    """
    Returns the song's details in a formatted string.
    
    :param data: A dictionary containing song details.
    :return: A formatted string with the song's details.
    """
    song_details = (
        f"\n{'_' * 5}\n"
        f"🎵 Title: {data['title']}\n"
        f"🎤 Artist: KORA AI\n"
        f"{'➖' * 5}\n\n"
        f"📋 Lyrics:\n\n{data['lyrics']}\n"
        f"{'_' * 5}"
    )
    return song_details

def execute(song_name):
    """
    Main function to fetch and display song details.
    
    :param song_name: The name of the song to search for.
    :return: A formatted string with song details.
    """
    result = fetch_lyrics(song_name)
    if result["success"]:
        data = result["data"]
        song_details = display_song(data)
        return song_details
    else:
        return result["error"]

# Example usage

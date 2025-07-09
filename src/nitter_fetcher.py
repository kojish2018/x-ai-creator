import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

NITTER_URL = os.getenv("NITTER_URL")
SEARCH_QUERY = os.getenv("SEARCH_QUERY")
PROCESSED_IDS_FILE = "processed_ids.txt"

def get_nitter_search_url():
    """Constructs the Nitter search URL from environment variables."""
    if not NITTER_URL or not SEARCH_QUERY:
        raise ValueError("NITTER_URL and SEARCH_QUERY must be set in the .env file")
    return f"{NITTER_URL}/search?f=tweets&q={SEARCH_QUERY}"

def fetch_and_parse_html():
    """Fetches and parses the Nitter search results page."""
    url = get_nitter_search_url()
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for bad status codes
    return BeautifulSoup(response.text, "html.parser")

def extract_tweet_info(tweet_div):
    """Extracts tweet information from a tweet div."""
    tweet_content_div = tweet_div.find("div", class_="tweet-content")
    content = tweet_content_div.text.strip() if tweet_content_div else "No content found"
    
    tweet_link_tag = tweet_div.find("a", class_="tweet-link")
    url = NITTER_URL + tweet_link_tag["href"] if tweet_link_tag else "No URL found"
    
    tweet_id = url.split('/')[-1].split('#')[0] if url != "No URL found" else "No ID found"
    
    return content, url, tweet_id

def load_processed_ids():
    """Loads processed tweet IDs from a file."""
    if not os.path.exists(PROCESSED_IDS_FILE):
        return set()
    with open(PROCESSED_IDS_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_processed_id(tweet_id):
    """Saves a processed tweet ID to the file."""
    with open(PROCESSED_IDS_FILE, "a") as f:
        f.write(f"{tweet_id}\n")

def get_new_tweets():
    """Gets new tweets that have not been processed yet."""
    processed_ids = load_processed_ids()
    new_tweets = []
    soup = fetch_and_parse_html()
    
    tweet_divs = soup.find_all("div", class_="tweet-container")

    for tweet_div in tweet_divs:
        content, url, tweet_id = extract_tweet_info(tweet_div)
        if tweet_id not in processed_ids and tweet_id != "No ID found":
            new_tweets.append({"content": content, "url": url, "id": tweet_id})
            
    return new_tweets
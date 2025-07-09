import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth
from dotenv import load_dotenv

load_dotenv()

PROCESSED_IDS_FILE = 'processed_ids.txt'

class BrowserFetcher:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("start-maximized")
        # chrome_options.add_argument("--headless")  # Headless mode can be enabled here
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        self.driver = webdriver.Chrome(options=chrome_options)

        # Apply stealth settings
        stealth(self.driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

    def _get_processed_ids(self):
        if not os.path.exists(PROCESSED_IDS_FILE):
            return set()
        with open(PROCESSED_IDS_FILE, 'r') as f:
            return set(line.strip() for line in f)

    def _add_processed_id(self, tweet_id):
        with open(PROCESSED_IDS_FILE, 'a') as f:
            f.write(f"{tweet_id}\n")

    def login(self):
        username = os.getenv("X_USERNAME")
        password = os.getenv("X_PASSWORD")

        if not username or not password:
            raise ValueError("X_USERNAME and X_PASSWORD must be set in .env file")

        self.driver.get("https://x.com/login")
        
        # Wait for username field and enter username
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='text']"))
        ).send_keys(username)
        self.driver.find_element(By.CSS_SELECTOR, "input[name='text']").send_keys(Keys.RETURN)

        # Wait for password field and enter password
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        ).send_keys(password)
        self.driver.find_element(By.CSS_SELECTOR, "input[name='password']").send_keys(Keys.RETURN)

        # Wait for login to complete (e.g., wait for home timeline to appear)
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='primaryColumn']"))
        )
        print("Login successful")

    def fetch_tweets(self, query, lang='en'):
        print(f"Searching for: {query}")
        search_url = f"https://x.com/search?q={query}&src=typed_query&f=live"
        self.driver.get(search_url)

        # Wait for search results to load
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweet']"))
        )
        
        time.sleep(5) # Wait for page to settle

        processed_ids = self._get_processed_ids()
        new_tweets = []

        articles = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")
        
        for article in articles[:10]: # Limit to 10 tweets to avoid being too aggressive
            try:
                tweet_text_element = article.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']")
                tweet_text = tweet_text_element.text
                
                # Find the timestamp which contains the permalink
                timestamp_element = article.find_element(By.css_selector, "a[aria-label*='ago'], a[aria-label*='minutes'], a[aria-label*='hour'], a[aria-label*='second']")
                tweet_url = timestamp_element.get_attribute('href')
                tweet_id = tweet_url.split('/')[-1]

                if tweet_id not in processed_ids:
                    new_tweets.append({
                        'id': tweet_id,
                        'text': tweet_text,
                        'url': tweet_url
                    })
                    self._add_processed_id(tweet_id)

            except Exception as e:
                print(f"Error processing tweet: {e}")
                continue
        
        return new_tweets

    def close(self):
        self.driver.quit()

if __name__ == '__main__':
    fetcher = BrowserFetcher()
    try:
        fetcher.login()
        tweets = fetcher.fetch_tweets('"AI breakthrough" lang:en')
        if tweets:
            print(f"Found {len(tweets)} new tweets:")
            for tweet in tweets:
                print(f"- ID: {tweet['id']}, URL: {tweet['url']}")
                print(f"  Text: {tweet['text']}")
        else:
            print("No new tweets found.")
    finally:
        fetcher.close()

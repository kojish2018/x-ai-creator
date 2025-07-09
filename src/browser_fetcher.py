import os
import time
import random
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

    def _human_like_type(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.2)) # Adjust delay as needed

    def _human_like_scroll_to_bottom(self):
        # JavaScriptでスクロールを実行する関数
        def scroll_to_position(driver, target_y):
            current_y = driver.execute_script("return window.pageYOffset;")
            # スクロール方向と距離に応じて速度を調整
            distance = target_y - current_y
            
            # 小さなステップでスクロール
            steps = int(abs(distance) / random.uniform(30, 80)) # 30pxから80pxのステップ
            if steps == 0: steps = 1

            for i in range(steps):
                # 加速・減速をシミュレート
                if i < steps / 3: # 最初はゆっくり
                    scroll_amount = random.uniform(5, 15)
                elif i > steps * 2 / 3: # 最後はゆっくり
                    scroll_amount = random.uniform(5, 15)
                else: # 途中は速く
                    scroll_amount = random.uniform(10, 30)
                
                if distance < 0: # 上にスクロールする場合
                    scroll_amount *= -1

                driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
                time.sleep(random.uniform(0.05, 0.2)) # 短い間隔で待機

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        current_scroll_position = 0

        while True:
            # 次のスクロールターゲットを計算
            # 画面の高さの半分から1倍程度をスクロールターゲットにする
            viewport_height = self.driver.execute_script("return window.innerHeight;")
            target_scroll_amount = random.uniform(viewport_height * 0.5, viewport_height * 0.9)
            
            # オーバーシュートと修正をシミュレート
            if random.random() < 0.1: # 10%の確率で少しオーバーシュート
                target_scroll_amount += random.uniform(50, 100)

            target_y = current_scroll_position + target_scroll_amount
            
            # ページの一番下を超えないように調整
            if target_y > last_height:
                target_y = last_height

            scroll_to_position(self.driver, target_y)
            current_scroll_position = self.driver.execute_script("return window.pageYOffset;")

            # スクロール後のランダムな待機
            time.sleep(random.uniform(0.5, 2.0))

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # ページの一番下まで到達したか、または新しいコンテンツがロードされなくなった場合
            if current_scroll_position >= last_height or new_height == last_height:
                break
            last_height = new_height # 新しいコンテンツがロードされた場合、高さを更新

    def login(self):
        username = os.getenv("X_USERNAME")
        password = os.getenv("X_PASSWORD")

        if not username or not password:
            raise ValueError("X_USERNAME and X_PASSWORD must be set in .env file")

        self.driver.get("https://x.com/login")
        
        # Wait for username field and enter username
        username_field = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='text']"))
        )
        self._human_like_type(username_field, username)
        username_field.send_keys(Keys.RETURN)

        # Wait for password field and enter password
        password_field = WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        )
        self._human_like_type(password_field, password)
        password_field.send_keys(Keys.RETURN)

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
        
        self._human_like_scroll_to_bottom() # 人間らしいスクロールを実行
        time.sleep(random.uniform(1, 3)) # スクロール後の最終待機

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

import os
import time
import random
import re
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
        print("Initializing BrowserFetcher...")
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Successfully connected to Chrome Driver.")
        except Exception as e:
            self.driver = None
            print(f"Error connecting to Chrome Driver: {e}")

    def check_login_status(self):
        print("Checking login status...")
        self.driver.get("https://x.com")
        try:
            # Wait for a specific element that only appears when logged in
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='SideNav_AccountSwitcher_Button']"))
            )
            print("Login confirmed.")
            return True
        except:
            print("Login not confirmed.")
            return False

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

    

    def fetch_tweets(self, keywords, lang='ja'):
        all_collected_tweets = []
        for keyword in keywords:
            print(f"Searching for: {keyword} lang:{lang}")
            search_url = f"https://x.com/search?q={keyword} lang:{lang}&src=typed_query&f=top"
            self.driver.get(search_url)

            # Wait for search results to load
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='tweet']"))
            )
            
            self._human_like_scroll_to_bottom() # 人間らしいスクロールを実行
            time.sleep(random.uniform(1, 3)) # スクロール後の最終待機

            processed_ids = self._get_processed_ids()
            
            articles = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")
            
            for article in articles[:20]: # Limit to 20 tweets per keyword
                try:
                    tweet_text_element = article.find_element(By.CSS_SELECTOR, "[data-testid='tweetText']")
                    tweet_text = tweet_text_element.text
                    
                    # Find the permalink (tweet URL) by looking for an <a> tag with '/status/' in its href
                    tweet_url_element = article.find_element(By.CSS_SELECTOR, "a[href*='/status/']")
                    tweet_url = tweet_url_element.get_attribute('href')
                    tweet_id = tweet_url.split('/')[-1]

                    likes = 0
                    retweets = 0
                    followers = 0 # フォロワー数はツイートカードから直接取得が困難なため、0とします。

                    try:
                        # いいね数 (aria-labelから取得)
                        like_button = article.find_element(By.CSS_SELECTOR, "[data-testid='like']")
                        aria_label = like_button.get_attribute('aria-label')
                        match = re.search(r'(\d+)\s+いいね', aria_label)
                        likes = int(match.group(1)) if match else 0
                    except:
                        pass

                    try:
                        # リツイート数 (aria-labelから取得)
                        retweet_button = article.find_element(By.CSS_SELECTOR, "[data-testid='retweet']")
                        aria_label = retweet_button.get_attribute('aria-label')
                        match = re.search(r'(\d+)\s+リツイート', aria_label)
                        retweets = int(match.group(1)) if match else 0
                    except:
                        pass

                    if tweet_id not in processed_ids:
                        all_collected_tweets.append({
                            'id': tweet_id,
                            'text': tweet_text,
                            'url': tweet_url,
                            'likes': likes,
                            'retweets': retweets
                        })
                        self._add_processed_id(tweet_id)

                except Exception as e:
                    print(f"Error processing tweet: {e}")
                    continue
            
            # BAN対策: キーワード間のランダムな待機時間
            if keyword != keywords[-1]: # 最後のキーワードの後は待機しない
                delay = random.uniform(5, 10) # 長めの待機時間
                print(f"Waiting for {delay:.2f} seconds before next keyword search...")
                time.sleep(delay)
        
        return all_collected_tweets

    

if __name__ == '__main__':
    fetcher = BrowserFetcher()
    if fetcher.driver is None:
        print("chrome driverが開いていません。")
    elif fetcher.check_login_status():
        keywords_to_search = ['AI', 'SaaS']
        collected_tweets = fetcher.fetch_tweets(keywords_to_search, lang='ja')
        if collected_tweets:
            print(f"Found {len(collected_tweets)} new tweets:")
            for tweet in collected_tweets:
                print(f"- ID: {tweet['id']}, URL: {tweet['url']}")
                print(f"  Text: {tweet['text']}")
                print(f"  Likes: {tweet['likes']}, Retweets: {tweet['retweets']}")
        else:
            print("No new tweets found.")
    else:
        print("xが開けていないかxにログインできていません")
    

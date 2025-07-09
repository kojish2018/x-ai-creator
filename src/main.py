import os
import time
import schedule
import logging
from dotenv import load_dotenv

from browser_fetcher import BrowserFetcher
from gemini_client import GeminiClient
from twitter_client import TwitterClient

load_dotenv()

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# --- Main Workflow ---
def run_workflow():
    logging.info("Starting workflow...")
    fetcher = None
    try:
        # 1. Fetch new tweets
        search_query = os.getenv("SEARCH_QUERY", '"AI breakthrough" lang:en')
        
        fetcher = BrowserFetcher()
        fetcher.login()
        new_tweets = fetcher.fetch_tweets(search_query)

        if not new_tweets:
            logging.info("No new tweets found.")
            return

        logging.info(f"Found {len(new_tweets)} new tweets to process.")

        # 2. Initialize clients
        gemini = GeminiClient()
        twitter = TwitterClient()

        # 3. Process each tweet
        for tweet in new_tweets:
            try:
                logging.info(f"Processing tweet: {tweet['url']}")

                # Generate comment
                comment = gemini.generate_comment(tweet['text'])
                if not comment:
                    logging.warning(f"Comment generation failed for tweet {tweet['id']}. Skipping.")
                    continue
                
                logging.info(f"Generated comment: {comment}")

                # Post to X
                twitter.post_quote_tweet(comment, tweet['url'])
                logging.info(f"Successfully posted quote tweet for {tweet['id']}.")
                
                # Wait a bit between posts to avoid being too spammy
                time.sleep(10)

            except Exception as e:
                logging.error(f"An error occurred while processing tweet {tweet['id']}: {e}", exc_info=True)
                continue # Continue to the next tweet

    except Exception as e:
        logging.critical(f"A critical error occurred in the main workflow: {e}", exc_info=True)
    finally:
        if fetcher:
            fetcher.close()
        logging.info("Workflow finished.")

# --- Scheduling --- 
if __name__ == "__main__":
    schedule_interval = int(os.getenv("SCHEDULE_INTERVAL_HOURS", 1))
    logging.info(f"Scheduling job to run every {schedule_interval} hour(s).")

    # Run once immediately
    run_workflow()

    schedule.every(schedule_interval).hours.do(run_workflow)

    while True:
        schedule.run_pending()
        time.sleep(1)

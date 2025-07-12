
import snscrape.modules.twitter as sntwitter
import pandas as pd
from datetime import datetime, timedelta
import time
import random

def get_popular_tweets(query, since_date, limit=100):
    """
    指定されたクエリと日付で人気のツイートを取得する
    """
    tweets_list = []
    # snscrapeでツイートを検索
    # lang:ja -> 日本語のツイートのみ
    # since:{since_date} -> 指定日以降のツイート
    # min_faves:10 -> いいねが10以上のツイートのみ (人気投稿のフィルタリング)
    search_query = f'{query} lang:ja since:{since_date} min_faves:10'
    
    print(f"Searching for: {search_query}")
    
    scraper = sntwitter.TwitterSearchScraper(search_query)
    
    for i, tweet in enumerate(scraper.get_items()):
        if i >= limit:
            break
        tweets_list.append({
            'date': tweet.date,
            'id': tweet.id,
            'content': tweet.rawContent,
            'username': tweet.user.username,
            'followers': tweet.user.followersCount,
            'likes': tweet.likeCount,
            'retweets': tweet.retweetCount,
            'url': tweet.url
        })
    
    return tweets_list

def main():
    """
    メイン処理
    """
    # 検索キーワード
    keywords = ['AI', 'SaaS']
    
    # 1週間前の日付を計算
    since_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    all_tweets_df = pd.DataFrame()
    
    for keyword in keywords:
        # BAN対策: ランダムな待機時間
        sleep_time = random.uniform(2, 5)
        print(f"Waiting for {sleep_time:.2f} seconds before next keyword...")
        time.sleep(sleep_time)
        
        tweets = get_popular_tweets(keyword, since_date)
        
        if tweets:
            df = pd.DataFrame(tweets)
            all_tweets_df = pd.concat([all_tweets_df, df], ignore_index=True)

    if not all_tweets_df.empty:
        # いいねの数で降順にソート
        all_tweets_df = all_tweets_df.sort_values(by='likes', ascending=False)
        
        # 結果をCSVファイルに出力
        output_path = 'tweets.csv'
        all_tweets_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"Successfully saved {len(all_tweets_df)} tweets to {output_path}")
    else:
        print("No tweets found.")

if __name__ == '__main__':
    main()

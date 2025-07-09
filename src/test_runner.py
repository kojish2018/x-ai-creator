import os
from pathlib import Path
from dotenv import load_dotenv
import os
from pathlib import Path
from dotenv import load_dotenv
from browser_fetcher import BrowserFetcher
from gemini_client import generate_comment

# .envファイルから環境変数を読み込む
# このファイルの絶対パスを取得し、その2つ上の親ディレクトリにある.envファイルを読み込む
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

print("--- テスト開始 ---")

# .envファイルの内容をチェック
print("\n[ステップ1: 環境変数の読み込みチェック]")
required_vars = [
    "TWITTER_API_KEY", "TWITTER_API_SECRET_KEY",
    "TWITTER_ACCESS_TOKEN", "TWITTER_ACCESS_TOKEN_SECRET",
    "GEMINI_API_KEY", "SEARCH_QUERY", "X_USERNAME", "X_PASSWORD"
]
all_vars_set = True
for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"  - {var}: 設定済み")
    else:
        print(f"  - {var}: 未設定！ .envファイルを確認してください。")
        all_vars_set = False

if not all_vars_set:
    print("\nエラー: 必要な環境変数が設定されていません。処理を中断します。")
    exit()


# 1. ツイート収集テスト
print("\n[ステップ2: ブラウザからのツイート収集テスト]")
fetcher = None
target_tweet = None
try:
    fetcher = BrowserFetcher()
    fetcher.login()
    search_query = os.getenv("SEARCH_QUERY", '"AI breakthrough" lang:en')
    new_tweets = fetcher.fetch_tweets(search_query)
    
    if not new_tweets:
        print("新しいツイートは見つかりませんでした。")
        print("  - 検索クエリが正しいか確認してください。")
        print("  - すべてのツイートが処理済み (processed_ids.txt) の可能性があります。")
    else:
        print(f"{len(new_tweets)}件の新しいツイートを取得しました。")
        target_tweet = new_tweets[0] # 最初の1件をテスト対象とする
        print("  - テスト対象ツイート:")
        print(f"    - ID: {target_tweet['id']}")
        print(f"    - URL: {target_tweet['url']}")
        print(f"    - 内容: {target_tweet['text'][:100]}...")

except Exception as e:
    print(f"エラーが発生しました: {e}")
    print("  - ブラウザの起動またはXへのログインに失敗しました。")
    print("  - X_USERNAME, X_PASSWORD, またはネットワーク接続を確認してください。")
finally:
    if fetcher:
        fetcher.close()


# 2. AIコメント生成テスト
if target_tweet:
    print("\n[ステップ3: Geminiによるコメント生成テスト]")
    try:
        generated_comment = generate_comment(target_tweet['text'])
        print("AIによるコメントが生成されました:")
        print(f"  - {generated_comment}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        print("  - Gemini APIキーが正しいか確認してください。")
        generated_comment = None
else:
    print("\n[ステップ3: Geminiによるコメント生成テスト] - スキップ (対象ツイートなし)")
    generated_comment = None

# 3. X投稿シミュレーション
if target_tweet and generated_comment:
    print("\n[ステップ4: Xへの投稿シミュレーション]")
    print("以下の内容で投稿が実行されます（実際には投稿されません）:")
    post_content = f"{generated_comment} {target_tweet['url']}"
    print("--- 投稿内容 ---")
    print(post_content)
    print("------------------")

    # BrowserFetcherがprocessed_ids.txtを管理するため、ここでは何もしない
    print(f"\nツイートID {target_tweet['id']} はBrowserFetcherによって処理済みとして記録されます。")
else:
    print("\n[ステップ4: Xへの投稿シミュレーション] - スキップ (ツイートまたはコメントが不十分)")

print("\n--- テスト終了 ---\n")
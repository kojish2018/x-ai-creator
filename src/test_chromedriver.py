import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_chromedriver_functionality():
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # ヘッドレスモードで実行する場合はコメントを外してください
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # 1. Googleを開く
        print("Googleを開きます...")
        driver.get("https://www.google.com")
        time.sleep(2) # ページ読み込みを待つ

        # 2. 「テスト」を検索する
        print("「テスト」を検索します...")
        search_box = driver.find_element(By.NAME, "q")
        # 一文字ずつゆっくり入力
        text_to_type = "テスト"
        for char in text_to_type:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.1, 0.3)) # 0.1秒から0.3秒の間で待機
        search_box.send_keys(Keys.RETURN)
        time.sleep(3) # 検索結果の読み込みを待つ

        # 3. ページの一番下までスクロールする (徹底的に人間らしい速度で)
        print("ページの一番下までスクロールします (人間らしい速度で)...")
        
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

        last_height = driver.execute_script("return document.body.scrollHeight")
        current_scroll_position = 0

        while True:
            # 次のスクロールターゲットを計算
            # 画面の高さの半分から1倍程度をスクロールターゲットにする
            viewport_height = driver.execute_script("return window.innerHeight;")
            target_scroll_amount = random.uniform(viewport_height * 0.5, viewport_height * 0.9)
            
            # オーバーシュートと修正をシミュレート
            if random.random() < 0.1: # 10%の確率で少しオーバーシュート
                target_scroll_amount += random.uniform(50, 100)

            target_y = current_scroll_position + target_scroll_amount
            
            # ページの一番下を超えないように調整
            if target_y > last_height:
                target_y = last_height

            scroll_to_position(driver, target_y)
            current_scroll_position = driver.execute_script("return window.pageYOffset;")

            # スクロール後のランダムな待機
            time.sleep(random.uniform(0.5, 2.0))

            new_height = driver.execute_script("return document.body.scrollHeight")
            
            # ページの一番下まで到達したか、または新しいコンテンツがロードされなくなった場合
            if current_scroll_position >= last_height or new_height == last_height:
                break
            last_height = new_height # 新しいコンテンツがロードされた場合、高さを更新

        time.sleep(random.uniform(1, 3)) # スクロール完了後の最終待機

        # 4. 2ページ目を開く
        print("2ページ目を開きます...")
        # 2ページ目のリンクを探す (Googleの検索結果ページの構造に依存します)
        # 一般的には、ページネーションのリンクは 'pn' クラスや 'nav' タグの中にあることが多いです
        # ここでは、テキストが '2' のリンクを探します
        try:
            # ページネーションのリンクが複数ある場合があるので、適切なものを選択
            # 例: <a aria-label="Page 2" href="...">2</a>
            # または <a class="fl" href="...">2</a>
            second_page_link = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Page 2'] | //a[text()='2']"))
            )
            second_page_link.click()
            print("2ページ目を開きました。")
            time.sleep(5) # 2ページ目の読み込みを待つ
        except Exception as e:
            print(f"2ページ目のリンクが見つからないか、クリックできませんでした: {e}")
            print("手動でページネーションの要素を確認する必要があるかもしれません。")

        print("テストが完了しました。")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
    finally:
        print("ブラウザを閉じます。")
        driver.quit()

if __name__ == "__main__":
    test_chromedriver_functionality()
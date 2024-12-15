import os
import time
import requests
import pandas as pd

def main():
    # 実行ファイルのディレクトリを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # url.csvのパスを設定
    csv_path = os.path.join(script_dir, 'url.csv')
    
    # filesフォルダのパスを設定
    files_dir = os.path.join(script_dir, 'files')
    
    # filesフォルダが存在しない場合は作成
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)
        print(f"'files'フォルダを作成しました: {files_dir}")
    
    try:
        # CSVファイルを読み込む
        df = pd.read_csv(csv_path, header=None)
        urls = df[0].tolist()
        print(f"読み込んだURLの数: {len(urls)}")
    except FileNotFoundError:
        print(f"エラー: '{csv_path}' が見つかりません。")
        return
    except Exception as e:
        print(f"CSV読み込み時にエラーが発生しました: {e}")
        return
    
    # ヘッダー情報を設定（User-Agentを追加）
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                      'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                      'Chrome/112.0.0.0 Safari/537.36'
    }
    
    for idx, url in enumerate(urls, start=1):
        try:
            print(f"{idx}/{len(urls)}: URLをダウンロード中: {url}")
            
            # HTTP GETリクエストを送信（ヘッダーを追加）
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()  # ステータスコードが200番台でない場合例外を発生
            
            # ファイル名を生成
            # URLの最後の部分を取得
            last_part = url.rstrip('/').split('/')[-1]
            
            if len(last_part) < 2:
                print(f"警告: URLの最後の部分が短すぎてファイル名を生成できません: {url}")
                continue
            
            # ファイル名の生成ロジックを修正
            # 例: last_part = '2022-001' -> '2022-001.html'
            # 要件に合わせて適宜調整
            if len(last_part) >= 8:
                filename_part = last_part[-8:]  # 最後の8文字を取得
            else:
                filename_part = last_part  # 8文字未満の場合は全体を使用
            
            # ファイル名に拡張子を追加
            filename = f"{filename_part}.html"
            
            # ファイルの保存パスを設定
            file_path = os.path.join(files_dir, filename)
            
            # 重複を避けるために、ファイルが既に存在する場合は番号を追加
            original_file_path = file_path
            counter = 1
            while os.path.exists(file_path):
                file_path = os.path.join(files_dir, f"{filename_part}_{counter}.html")
                counter += 1
            
            # HTMLコンテンツをファイルに保存
            with open(file_path, 'w', encoding=response.encoding if response.encoding else 'utf-8') as file:
                file.write(response.text)
            
            print(f"保存完了: {file_path}")
        
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTPエラー: {http_err} - URL: {url}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"接続エラー: {conn_err} - URL: {url}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"タイムアウトエラー: {timeout_err} - URL: {url}")
        except requests.exceptions.RequestException as req_err:
            print(f"リクエストエラー: {req_err} - URL: {url}")
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e} - URL: {url}")
        
        # 次のダウンロードまで3秒待機
        time.sleep(3)

if __name__ == "__main__":
    main()

import csv
import os
import time
import requests
from urllib.parse import urlparse

# CSVファイルのパス
csv_file = '07_outurllist.csv'

# 出力ディレクトリ
output_dir = '追加分証跡'

# 失敗したURLを格納するリスト
failed_urls = []

def download_file(url, filename):
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # URLの末尾が.pdfの場合、拡張子を.pdfに変更
        if url.lower().endswith('.pdf'):
            filename = os.path.splitext(filename)[0] + '.pdf'
        else:
            filename = os.path.splitext(filename)[0] + '.html'
        
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"ファイルを保存しました: {filepath}")
        return response.status_code
    except requests.RequestException as e:
        print(f"エラー: {url} - {str(e)}")
        failed_urls.append(url)
        return None
    except IOError as e:
        print(f"ファイル保存エラー: {filepath} - {str(e)}")
        failed_urls.append(url)
        return None

# 出力ディレクトリが存在しない場合は作成
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"ディレクトリを作成しました: {output_dir}")

# CSVファイルを読み込み、URLをダウンロード
try:
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if 'url' not in reader.fieldnames:
            raise ValueError("CSVファイルに'url'列が見つかりません。")
        
        for row in reader:
            filename = row.get(reader.fieldnames[0], '')  # 1列目をファイル名として使用
            url = row.get('url', '').strip()
            if url:
                print(f"ダウンロード中: {url}")
                status_code = download_file(url, filename)
                if status_code:
                    print(f"完了 - ステータスコード: {status_code}")
                time.sleep(3)  # 3秒待機
            else:
                print(f"警告: 空のURLがスキップされました。行: {reader.line_num}")

except FileNotFoundError:
    print(f"エラー: CSVファイル '{csv_file}' が見つかりません。")
except csv.Error as e:
    print(f"CSVファイルの読み込みエラー: {str(e)}")
except Exception as e:
    print(f"予期せぬエラーが発生しました: {str(e)}")

# 失敗したURLを表示
if failed_urls:
    print("\nダウンロードに失敗したURL:")
    for url in failed_urls:
        print(url)
else:
    print("\n全てのURLのダウンロードが成功しました。")

print(f"\n処理が完了しました。ダウンロードしたファイルは '{output_dir}' フォルダにあります。")

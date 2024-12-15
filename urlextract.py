import os
import re
import csv
from datetime import datetime
from bs4 import BeautifulSoup

def extract_information_from_html(html_content):
    """
    HTMLコンテンツから必要な情報を抽出する関数
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # タイトルの抽出
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else 'なし'

    # 日付の抽出とフォーマット変換
    time_tag = soup.find('time', class_='text-grey')
    if time_tag:
        date_str = time_tag.get_text(strip=True).split(' ')[0]  # '06-01-2022' の部分を取得
        try:
            date_obj = datetime.strptime(date_str, '%d-%m-%Y')
            date_formatted = date_obj.strftime('%Y/%m/%d')
        except ValueError:
            date_formatted = '無効な日付形式'
    else:
        date_formatted = 'なし'

    # URLの抽出
    urls = []
    # 全ての<a>タグを探索し、href属性を取得
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        if href.startswith('https://'):
            urls.append(href)
    
    return title, date_formatted, urls

def filter_urls(urls, excluded_domains):
    """
    URLリストから特定のドメインを含むURLを除外する関数
    """
    filtered = []
    for url in urls:
        # ドメイン部分を抽出
        domain_match = re.match(r'https?://([^/]+)/?', url)
        if domain_match:
            domain = domain_match.group(1).lower()
            # 除外ドメインが含まれているかチェック
            if not any(excluded_domain in domain for excluded_domain in excluded_domains):
                filtered.append(url)
    return filtered

def main():
    # スクリプトと同じディレクトリの 'files' フォルダへのパス
    current_dir = os.path.dirname(os.path.abspath(__file__))
    files_dir = os.path.join(current_dir, 'files')

    # 除外するドメインのリスト（小文字に統一）
    excluded_domains = [
        'europa.eu',
        'linkedin.com',
        'github.com',
        'infosec.exchange',
        'facebook.com'
    ]

    # CSV出力用のデータリスト
    data_rows = []

    # 'files' フォルダ内のすべてのHTMLファイルを処理
    for filename in os.listdir(files_dir):
        if filename.lower().endswith('.html'):
            file_path = os.path.join(files_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    html_content = file.read()
            except UnicodeDecodeError:
                # UTF-8で読み込めない場合は、Shift-JISを試みる
                with open(file_path, 'r', encoding='shift_jis') as file:
                    html_content = file.read()
            except Exception as e:
                print(f"ファイル {filename} の読み込み中にエラーが発生しました: {e}")
                continue

            # 情報の抽出
            title, date, urls = extract_information_from_html(html_content)

            # URLのフィルタリング
            filtered_urls = filter_urls(urls, excluded_domains)

            # フィルタリング後のURLが存在しない場合でも 'なし' を出力
            if not filtered_urls:
                filtered_urls = ['なし']

            # 各URLごとにデータ行を作成
            for url in filtered_urls:
                data_rows.append({
                    'date': date,
                    'title': title,
                    'from': filename,
                    'url': url
                })

    # 'from' 列で昇順にソート
    data_rows_sorted = sorted(data_rows, key=lambda x: x['from'])

    # No列を追加（1から始まる連番）
    for idx, row in enumerate(data_rows_sorted, start=1):
        row['No'] = idx

    # CSVの列順を指定
    csv_columns = ['No', 'date', 'title', 'from', 'url']

    # CSVファイルへの書き込み（日本語環境のExcelで文字化けしないように 'utf-8-sig' エンコーディングを使用）
    output_csv_path = os.path.join(current_dir, '07_outurllist.csv')
    try:
        with open(output_csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            writer.writeheader()
            for row in data_rows_sorted:
                writer.writerow(row)
        print(f"CSVファイル '07_outurllist.csv' を作成しました。")
    except Exception as e:
        print(f"CSVファイルの作成中にエラーが発生しました: {e}")

if __name__ == '__main__':
    main()

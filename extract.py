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

    # CVE番号の抽出（重複を排除）
    cve_pattern = r'CVE-\d{4}-\d{4,}'
    cves = re.findall(cve_pattern, html_content)
    unique_cves = sorted(list(set(cves))) if cves else ['なし']

    return title, date_formatted, unique_cves

def main():
    # スクリプトと同じディレクトリの 'files' フォルダへのパス
    current_dir = os.path.dirname(os.path.abspath(__file__))
    files_dir = os.path.join(current_dir, 'files')

    # CSV出力用のデータリスト
    data_rows = []

    # 'files' フォルダ内のすべてのHTMLファイルを処理
    for filename in os.listdir(files_dir):
        if filename.lower().endswith('.html'):
            file_path = os.path.join(files_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            # 情報の抽出
            title, date, cves = extract_information_from_html(html_content)

            # URLの生成（拡張子を除くファイル名を使用）
            file_base_name = os.path.splitext(filename)[0]
            url = f'https://cert.europa.eu/publications/security-advisories/{file_base_name}/'

            # CVEごとにデータ行を作成
            for cve in cves:
                data_rows.append({
                    'date': date,
                    'CVE': cve,
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
    csv_columns = ['No', 'date', 'CVE', 'title', 'from', 'url']

    # CSVファイルへの書き込み（日本語環境のExcelで文字化けしないように 'utf-8-sig' エンコーディングを使用）
    output_csv_path = os.path.join(current_dir, '01_output.csv')
    with open(output_csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        for row in data_rows_sorted:
            writer.writerow(row)

    print(f"CSVファイル '01_output.csv' を作成しました。")

if __name__ == '__main__':
    main()

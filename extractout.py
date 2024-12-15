import os
import re
import csv
import warnings
from bs4 import BeautifulSoup
from collections import defaultdict

# BeautifulSoupの警告を抑制
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')

def extract_cve(html_content):
    pattern = r'CVE-(\d{4}-\d+)'
    matches = re.findall(pattern, html_content)
    return [match for match in matches if not match.startswith('2024')]

def read_file_with_fallback_encoding(file_path, encodings=['utf-8', 'utf-8-sig', 'shift_jis', 'iso-8859-1']):
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    
    # If all encodings fail, try to read as much as possible
    with open(file_path, 'rb') as file:
        raw = file.read()
    return raw.decode('utf-8', errors='ignore')

def process_html_files(directory):
    data = defaultdict(set)
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            file_path = os.path.join(directory, filename)
            try:
                html_content = read_file_with_fallback_encoding(file_path)
                
                # HTMLパーサーを使用
                soup = BeautifulSoup(html_content, 'html.parser')
                cve_list = extract_cve(str(soup))
                
                if cve_list:
                    for cve in cve_list:
                        data[filename].add(f"CVE-{cve}")
                else:
                    data[filename].add("なし")
            except Exception as e:
                print(f"エラー: ファイル '{filename}' の処理中に問題が発生しました。エラー: {str(e)}")
    
    return data

def write_csv(data):
    with open('01_outurl.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['No', 'CVE', 'from'])
        
        row_number = 1
        for filename, cve_set in sorted(data.items()):
            for cve in sorted(cve_set):
                writer.writerow([row_number, cve, filename])
                row_number += 1

def main():
    current_dir = os.getcwd()
    additional_dir = os.path.join(current_dir, '追加分証跡')
    
    if not os.path.exists(additional_dir):
        print(f"エラー: '{additional_dir}' ディレクトリが見つかりません。")
        return
    
    data = process_html_files(additional_dir)
    write_csv(data)
    print("CSVファイルの作成が完了しました。")

if __name__ == "__main__":
    main()

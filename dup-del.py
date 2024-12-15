import csv
import codecs

def process_csv(input_file, output_file):
    # BOMを考慮してファイルを開く
    with codecs.open(input_file, 'r', 'utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # fromとCVEの組み合わせでユニークな行を保持
    unique_rows = {}
    deleted_rows = []

    for row in rows:
        key = (row['from'], row['CVE'])
        if key not in unique_rows:
            unique_rows[key] = row
        else:
            deleted_rows.append(row)

    # 結果を書き出す
    with codecs.open(output_file, 'w', 'utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(unique_rows.values())

    return deleted_rows

# スクリプトの実行
input_file = 'dup.csv'
output_file = 'processed_dup.csv'
deleted_rows = process_csv(input_file, output_file)

print("削除された行:")
for row in deleted_rows:
    print(row)

print(f"\n削除された行の数: {len(deleted_rows)}")

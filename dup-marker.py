import os
import pandas as pd
from glob import glob

# 現在のディレクトリ内の'03_master_'で始まるすべてのCSVファイルを取得
csv_files = glob('03_master_*.csv')

total_duplicates = 0  # 重複の総数をカウントする変数を初期化

for file in csv_files:
    # CSVファイルを読み込む（エンコーディングを指定）
    df = pd.read_csv(file, encoding='utf-8-sig')

    # 日付列を日付型に変換
    df['date'] = pd.to_datetime(df['date'], format='%Y/%m/%d')

    # CVE値が重複するグループを抽出
    duplicates = df[df.duplicated('CVE', keep=False)]

    # 重複の数をカウント
    total_duplicates += len(duplicates)

    # 行番号を一時的に保存するための列を作成
    df['index'] = df.index  

    for cve in duplicates['CVE'].unique():
        cve_group = df[df['CVE'] == cve].sort_values(['date', 'index'])  

        # cve_groupが空でない場合に処理を実行
        if not cve_group.empty:
            # 一番古い行以外のCVE列に!を付与
            df.loc[(df['CVE'] == cve) & (df.index != cve_group.index[0]), 'CVE'] = cve + '!'

    # 更新されたデータフレームを元のCSVファイルに書き込む（エンコーディングを指定）
    # 一時的に作成したindex列を削除して保存
    df.drop(columns=['index'], inplace=True)  
    df.to_csv(file, index=False, encoding='utf-8-sig')

# 重複の総数を出力
if total_duplicates > 0:
    print(f"重複は合計 {total_duplicates} 件ありました。")
else:
    print("重複はありませんでした。")

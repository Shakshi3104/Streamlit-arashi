import pandas as pd

from utils import loader, music_parser

if __name__ == "__main__":
    # データの読み込み
    dirpath = "./data/"
    all_songs, all_writers, info = loader.load_all_songs(dirpath)
    songs_lives_cross, counted_live_songs, live_info = loader.load_live_info(dirpath)
    play_counts, date_ = music_parser.load_arashi_play_counts(dirpath)

    # マートテーブルに整形
    mart_table = pd.merge(all_songs, play_counts, left_on="曲名", right_on="Name", how="left").fillna(0)
    mart_table = pd.merge(mart_table, counted_live_songs, left_on="曲名", right_on="曲名", how="left").fillna(0)

    # 不要なカラムを削除
    mart_table = mart_table.drop(columns="Name")

    # カラム名を変更
    mart_table = mart_table.rename(columns={"Play Count": "再生回数"})

    # 型を変換
    mart_table["再生回数"] = mart_table["再生回数"].astype(int)
    mart_table["収録回数"] = mart_table["収録回数"].astype(int)
    mart_table["再生回数_日付"] = date_.strftime("%Y/%m/%d %H:%M:%S")

    # CSVファイルに書き出す
    s_format = '%Y%m%d_%H%M'
    date_str = date_.strftime(s_format)
    filename = f"arashi_songs_{date_str}.csv"

    mart_table.to_csv(dirpath + filename, encoding="utf-8_sig")

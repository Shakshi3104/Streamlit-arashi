import pandas as pd

import streamlit as st

from pathlib import Path

import re
import unicodedata


@st.cache
def load_all_songs(dirpath):
    dirpath = Path(dirpath)
    all_songs = pd.read_csv(dirpath / "All Songs-All Songs.csv")

    info = []
    all_writers = []

    for cd, maker in zip(all_songs["収録CD"], all_songs["クレジット"]):
        # 収録CDを抽出する
        cd_ = cd.split(" | ")

        # クレジットを抽出する
        if type(maker) is str:
            maker_ = maker.replace("作詞：", "").replace("作詞・作曲：", "").replace("作詞・作曲・編曲：", "") \
                .replace("作曲：", "").replace("作曲・編曲：", "").replace("オーケストラ編曲：", "").replace("編曲：", "") \
                .replace("Rap詞：", "").replace("All Rap presented by ", "") \
                .replace("Written by ", "").replace("Produced by ", "").replace("Track produced by ", "") \
                .replace("Music by ", "").replace("Remixed by ", "").replace("Rap by ", "").replace("Lyrics by ", "") \
                .replace("Arranged by ", "").replace("Track production by ", "") \
                .replace("Additional track production by ", "")

            maker_ = maker_.replace(" / ", ", ")
            maker_ = maker_.split(", ")

            all_writers += maker_

        else:
            maker_ = [""]

        tmp_dict = {"CD": cd_, "Writers": maker_}
        info += [tmp_dict]

    # すべてのソングライターの一覧
    all_writers = list(set(all_writers))
    # 櫻井翔の別名を削除する
    all_writers.remove("SHOW")
    all_writers.remove("Sho Sakurai")

    # NaNを空白に置き換える
    all_songs = all_songs.fillna("")

    return all_songs, all_writers, info


def find_songs_from_songwriter(all_songs, info, writer_select):
    names = []
    writers = []
    infos = []
    cds = []

    for i, song_info in enumerate(info):
        if writer_select in song_info["Writers"]:
            line = all_songs.iloc[i, :]
            names += [line["曲名"]]
            writers += [line["クレジット"]]
            cds += [line["収録CD"]]
            infos += [line["タイアップ、備考"]]

        if writer_select == "櫻井翔":
            if "SHOW" in song_info["Writers"] or "Sho Sakurai" in song_info["Writers"]:
                line = all_songs.iloc[i, :]
                names += [line["曲名"]]
                writers += [line["クレジット"]]
                cds += [line["収録CD"]]
                infos += [line["タイアップ、備考"]]

    selected_info = pd.DataFrame({"Song name": names,
                                  "Songwriter": writers,
                                  "CD": cds,
                                  "Information": infos})

    return selected_info


@st.cache
def load_single_sales(dirpath: str):
    dirpath = Path(dirpath)
    single_sales = pd.read_csv(dirpath / "Single sales.csv")
    single_sales.columns = ["Title", "Best rank", "Ranked week", "Sales", "Release"]

    return single_sales


@st.cache
def load_album_sales(dirpath: str):
    dirpath = Path(dirpath)
    album_sales = pd.read_csv(dirpath / "Album sales.csv")
    album_sales.columns = ["Title", "Best rank", "Ranked week", "Sales", "Release"]

    return album_sales


# 結合文字を使用した濁点や半濁点を直前の仮名と結合させる
# https://qiita.com/gretchi/items/13c0825282415e2e360d
def join_diacritic(text, mode="NFC"):
    """
    基底文字と濁点・半濁点を結合
    """
    # str -> bytes
    bytes_text = text.encode()

    # 濁点Unicode結合文字置換
    bytes_text = re.sub(b"\xe3\x82\x9b", b'\xe3\x82\x99', bytes_text)
    bytes_text = re.sub(b"\xef\xbe\x9e", b'\xe3\x82\x99', bytes_text)

    # 半濁点Unicode結合文字置換
    bytes_text = re.sub(b"\xe3\x82\x9c", b'\xe3\x82\x9a', bytes_text)
    bytes_text = re.sub(b"\xef\xbe\x9f", b'\xe3\x82\x9a', bytes_text)

    # bytet -> str
    text = bytes_text.decode()

    # 正規化
    text = unicodedata.normalize(mode, text)

    return text

@st.cache
def load_live_info(dirpath):
    dirpath = Path(dirpath)
    dirpath_dvd = dirpath / "DVD"

    live_songs = pd.DataFrame()

    for filepath in dirpath_dvd.glob("*.csv"):
        # ライブ名
        live_name = join_diacritic(filepath.name.replace("-表1.csv", ""))

        live = pd.read_csv(filepath)
        live["コンサート名"] = live_name

        live_songs = pd.concat([live_songs, live], ignore_index=True)

    # カウントする
    counted_live_songs = live_songs.groupby(by="曲名").size().sort_values(ascending=False).to_frame().reset_index()
    counted_live_songs = counted_live_songs.rename(columns={0: "収録回数"})

    # コンサートの情報
    live_info = pd.read_csv(dirpath / "live-info.csv")

    # コンサート情報とマージする
    live_songs = pd.merge(live_info, live_songs, left_on="名前", right_on="コンサート名").drop(columns="名前")

    # 曲名とコンサート名のクロス集計表
    songs_lives_cross = pd.crosstab(live_songs["曲名"], live_songs["略称"])
    songs_lives_cross = songs_lives_cross[list(live_info["略称"])]

    return songs_lives_cross, counted_live_songs, live_info


if __name__ == "__main__":
    dirpath = "../data/"
    all_, writes, info = load_all_songs(dirpath)

    songs_lives_cross, counted_live_songs, live_info = load_live_info(dirpath)

    all_song_ = pd.merge(all_, songs_lives_cross, left_on="曲名", right_on="曲名", how="left")
    all_song_ = pd.merge(all_song_, counted_live_songs, left_on="曲名", right_on="曲名", how="left")



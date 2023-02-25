import pandas as pd

import streamlit as st

from pathlib import Path


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


if __name__ == "__main__":
    dirpath = "../data/"
    all_, writes, info = load_all_songs(dirpath)

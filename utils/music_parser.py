import pandas as pd
import plistlib

from pathlib import Path

from .utils import join_diacritic


def load_music_library(dirpath):
    dirpath = Path(dirpath)
    filepath = dirpath / "music-library.xml"

    with filepath.open('rb') as f:
        library_plist = plistlib.load(f)

    tracks = pd.DataFrame(list(library_plist["Tracks"].values()))

    return tracks, library_plist["Date"]


def load_arashi_play_counts(dirpath):
    tracks, date_ = load_music_library(dirpath)
    tracks = tracks[tracks["Artist"] == "嵐"].reset_index(drop=True)

    # 表記揺れを直す
    replace_dict = {
        'Doors 〜勇気の軌跡〜': 'Doors〜勇気の軌跡〜',
        'Doors ～勇気の軌跡～': 'Doors〜勇気の軌跡〜',
        'ALL or NOTHING Ver.1.02': 'ALL or NOTHING Ver,1.02',
        'Crazy Moon ～キミ・ハ・ムテキ～': 'Crazy Moon～キミ・ハ・ムテキ～',
        "Don't stop": "Don't Stop",
        "Mr. Lonely": "Mr.Lonely",
        "NA!NA!NA!!": "NA! NA! NA!!",
        "OK! ALL RIGHT! いい恋をしよう": "OK!ALL RIGHT!いい恋をしよう",
        "PIKA☆NCHI(album version)": "PIKA☆NCHI",
        "PIKA☆☆NCHI DOUBLE": "PIKA★★NCHI DOUBLE",
        "Reach for the sky ～天までとどけ～": "Reach for the sky〜天までとどけ〜",
        "movin'on": "movin' on",
        "とまどいながら(album version)": "とまどいながら",
        "エナジーソング ～絶好調超!!!!～": "エナジーソング～絶好調超!!!!～",
        "台風ジェネレーション -Typhoon Generation-": "台風ジェネレーション",
        "日本よいとこ摩訶不思議 covered by 嵐": "日本よいとこ摩訶不思議",
        "虹のカケラ ～no rain, no rainbow～": "虹のカケラ～no rain, no rainbow～",
        "道 DOUBLE Ver.": "道 DOUBLE Ver,"
    }

    tracks["Name"] = tracks["Name"].replace(replace_dict)
    tracks["Name"] = tracks["Name"].map(join_diacritic)

    tracks = tracks[["Name", "Play Count"]]
    play_counts = tracks.groupby(by="Name").sum().reset_index().rename(columns={0: "Name"})

    return play_counts, date_


if __name__ == "__main__":
    dirpath = "../data/"
    counts, date_ = load_arashi_play_counts(dirpath)


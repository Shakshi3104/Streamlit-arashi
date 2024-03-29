import pandas as pd
import streamlit as st

import plotly.graph_objects as go
from st_aggrid import AgGrid

from utils import loader, music_parser


def release_type_to_color(x) -> str:
    if x == "シングル":
        return "rgba(255, 168, 167, 0.8)"
    elif x == "カップリング":
        return "rgba(199, 227, 212, 0.8)"
    elif x == "アルバム":
        return "rgba(192, 197, 213, 0.8)"


if __name__ == "__main__":
    st.set_page_config(page_title="ARASHI Songs", layout="wide")

    """
    # ARASHI Songs Dashboard
    """

    # データの読み込み
    dirpath = "./data/"
    all_songs, all_writers, info = loader.load_all_songs(dirpath)
    songs_lives_cross, counted_live_songs, live_info = loader.load_live_info(dirpath)
    play_counts, date_ = music_parser.load_arashi_play_counts(dirpath)

    # 全曲リストとライブで披露された回数をマージする
    counted_live_songs = pd.merge(counted_live_songs, all_songs)
    songs_lives_cross = pd.merge(all_songs, songs_lives_cross, left_on="曲名", right_on="曲名").fillna(0)

    # サマリー
    cols = st.columns(4)
    # リリースされた曲数
    with cols[0]:
        st.metric("All songs", f"{all_songs['曲名'].count()}")
        f"""
        Single: {all_songs[all_songs['タイプ'] == 'シングル']['曲名'].count()}, 
        c/w: {all_songs[all_songs['タイプ'] == 'カップリング']['曲名'].count()}, 
        Album: {all_songs[all_songs['タイプ'] == 'アルバム']['曲名'].count()}
        """

    # ライブで披露された曲数
    with cols[1]:
        st.metric("Songs singed on concerts", f"{counted_live_songs['曲名'].count()}")
        f"""
        Single: {counted_live_songs[counted_live_songs['タイプ'] == 'シングル']['曲名'].count()}, 
        c/w: {counted_live_songs[counted_live_songs['タイプ'] == 'カップリング']['曲名'].count()}, 
        Album: {counted_live_songs[counted_live_songs['タイプ'] == 'アルバム']['曲名'].count()}
        """

    # Rap詞: 櫻井翔がある曲数
    with cols[2]:
        rap_songs = loader.find_songs_from_songwriter(all_songs, info, "櫻井翔")
        st.metric("Songs with rap by Sho Sakurai", f"{rap_songs['曲名'].count()}")
        f"""
        Single: {rap_songs[rap_songs['タイプ'] == 'シングル']['曲名'].count()}, 
        c/w: {rap_songs[rap_songs['タイプ'] == 'カップリング']['曲名'].count()}, 
        Album: {rap_songs[rap_songs['タイプ'] == 'アルバム']['曲名'].count()}
        """

    # 総再生回数
    with cols[3]:
        st.metric("All play counts", f"{int(play_counts['Play Count'].sum())}")
        f"""
        By {date_.strftime('%Y/%m/%d')}
        """

    # タブ
    tabs = st.tabs(["Concert", "Songwriter", "Play count"])

    with tabs[0]:

        """
        ### Sing in Concert Top 30
        """
        # リリースタイプの選択
        selected_types_live = st.multiselect(
            label="Release type",
            options=["シングル", "カップリング", "アルバム"],
            default=["シングル", "カップリング", "アルバム"],
            key="live"
        )
        selected_counted_live_song = counted_live_songs[counted_live_songs["タイプ"].isin(selected_types_live)]

        # コンサート披露回数が多い順に30曲
        top30_live_songs = selected_counted_live_song.sort_values(by="収録回数", ascending=False)[:30]

        # 棒グラフ
        colors = list(map(lambda x: release_type_to_color(x), top30_live_songs["タイプ"]))
        fig = go.Figure(
            go.Bar(
                x=top30_live_songs["収録回数"],
                y=top30_live_songs["曲名"],
                hovertext=top30_live_songs["リリース年"],
                orientation='h',
                hovertemplate="<b>%{y}</b> (%{hovertext}年): %{x}回<extra></extra>",
                showlegend=False,
                marker_color=colors,
            ))
        fig.update_layout(yaxis=dict(autorange="reversed"),
                          width=None,
                          height=None,
                          autosize=True)
        st.plotly_chart(fig)

        # AgGrid(top30_live_songs)

        """
        ### Concert distribution
        """
        # ヒートマップ
        # hovertextを作る
        hovertext = songs_lives_cross[list(live_info["略称"])]
        for live_name in live_info["略称"]:
            full_live_name = list(live_info[live_info["略称"] == live_name]["名前"])[0]
            hovertext[live_name] = [f"<b>{song}</b><br>({full_live_name})" if count > 0 else ""
                                    for song, count in zip(songs_lives_cross["曲名"], hovertext[live_name])]

        fig = go.Figure(
            go.Heatmap(
                z=songs_lives_cross[list(live_info["略称"])],
                x=list(live_info["略称"]),
                y=songs_lives_cross["曲名"],
                text=hovertext,
                showscale=False,
                colorscale="blues",
                hovertemplate="%{text}<extra></extra>",
            )
        )
        fig.update_layout(yaxis=dict(autorange="reversed"),
                          width=None,
                          height=None,
                          autosize=True)
        st.plotly_chart(fig)

        # テーブルで表示するか
        show_table = st.checkbox("Show as table")
        if show_table:
            AgGrid(songs_lives_cross[["曲名"] + list(live_info["略称"])])

    with tabs[1]:
        """
        ### Find ARASHI songs from songwriters 
        """
        # セレクトボックスのデフォルトは嵐にしておく
        default_writer = all_writers.index("嵐")
        writer_select = st.selectbox(
            "Song Writer", all_writers, default_writer
        )

        st.write("Find ARASHI songs written by {}".format(writer_select))
        selected_songs = loader.find_songs_from_songwriter(all_songs, info, writer_select)
        AgGrid(selected_songs)

    with tabs[2]:
        play_counts = pd.merge(all_songs, play_counts, left_on="曲名", right_on="Name", how="left").drop(columns="Name")
        play_counts["Play Count"] = play_counts["Play Count"].fillna(0)

        """
        ### Play Top 30
        """
        # リリースタイプの選択
        selected_types_play = st.multiselect(
            label="Release type",
            options=["シングル", "カップリング", "アルバム"],
            default=["シングル", "カップリング", "アルバム"],
            key="play"
        )
        selected_play_counts = play_counts[play_counts["タイプ"].isin(selected_types_play)]

        # 再生回数Top30
        top30_play_songs = selected_play_counts.sort_values(by="Play Count", ascending=False)[:30]

        # 棒グラフ
        colors = list(map(lambda x: release_type_to_color(x), top30_play_songs["タイプ"]))
        fig = go.Figure(
            go.Bar(
                x=top30_play_songs["Play Count"],
                y=top30_play_songs["曲名"],
                hovertext=top30_play_songs["リリース年"],
                orientation='h',
                hovertemplate="<b>%{y}</b> (%{hovertext}年): %{x}回<extra></extra>",
                showlegend=False,
                marker_color=colors,
            ))
        fig.update_layout(yaxis=dict(autorange="reversed"),
                          width=None,
                          height=None,
                          autosize=True)
        st.plotly_chart(fig)

        """
        ### All songs
        """
        show_all = st.checkbox("Show all")
        if show_all:
            AgGrid(play_counts, fit_columns_on_grid_load=True)

import streamlit as st

import plotly.graph_objects as go

from utils import utils


if __name__ == "__main__":
    st.set_page_config(layout="wide")

    """
    # ARASHI
    """

    dirpath = "./data/"
    all_songs, all_writers, info = utils.load_all_songs(dirpath)
    songs_lives_cross, counted_live_songs, live_info = utils.load_live_info(dirpath)

    """
    ### Find ARASHI's songs from songwriters 
    """
    # セレクトボックスのデフォルトは嵐にしておく
    default_writer = all_writers.index("嵐")
    writer_select = st.selectbox(
        "Song Writer", all_writers, default_writer
    )

    st.write("Find ARASHI's songs written by {}".format(writer_select))
    selected_songs = utils.find_songs_from_songwriter(all_songs, info, writer_select)
    st.write(selected_songs)

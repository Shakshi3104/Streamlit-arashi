import streamlit as st
import numpy as np
import plotly.graph_objects as go

from utils import utils
from utils.utils import PathManager

if __name__ == "__main__":
    """
    # ARASHI
    ## Find ARASHI's songs from songwriters 
    """

    manager = PathManager("ARASHI List/")
    all_songs, all_writers, info = utils.load_all_songs(manager)

    # セレクトボックスのデフォルトは嵐にしておく
    default_writer = all_writers.index("嵐")
    writer_select = st.selectbox(
        "Song Writer", all_writers, default_writer
    )

    st.write("Find ARASHI's songs written by {}".format(writer_select))
    selected_songs = utils.find_songs_from_songwriter(all_songs, info, writer_select)
    st.write(selected_songs)

    """
    ## Single sales
    """
    single_sales = utils.load_single_sales(manager)
    plot_single_sales = [go.Bar(x=single_sales["Title"], y=single_sales["Sales"])]
    # layout = go.Layout(width=1200)
    st.plotly_chart(go.Figure(data=plot_single_sales))

    """
    ## Album sales
    """
    album_sales = utils.load_album_sales(manager)
    plot_album_sales = [go.Bar(x=album_sales["Title"], y=album_sales["Sales"])]
    st.plotly_chart(go.Figure(data=plot_album_sales))

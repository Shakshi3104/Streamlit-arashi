import streamlit as st
# import plotly.graph_objects as go

from utils import utils
from utils.utils import PathManager

if __name__ == "__main__":
    """
    # ARASHI
    
    ## Find ARASHI's songs from songwriters 
    """

    manager = PathManager("ARASHI List/")
    all_songs, all_writers, info = utils.load_all_songs(manager)

    writer_select = st.selectbox(
        "Song Writer", all_writers
    )

    st.write("Find ARASHI's songs written by {}".format(writer_select))
    selected_songs = utils.find_songs_from_songwriter(all_songs, info, writer_select)
    st.write(selected_songs)
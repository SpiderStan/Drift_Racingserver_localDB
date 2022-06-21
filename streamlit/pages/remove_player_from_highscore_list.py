import streamlit as st
import time
import base64
from datetime import timedelta
import pandas as pd 
import numpy as np
from PIL import Image

from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger

def app():

    lobby_id = st.session_state.lobby_id        

    st.write("Remove Player from Highscore List of Lobby: " + str(lobby_id))

    with st.form("my_form"):
        result = fetch_get(f"{settings.driftapi_path}/driftapi/game/{lobby_id}/highscores")
        result = [r["user_name"] for r in result if (type(r) is dict) and ("user_name" in r.keys())]
        user_name = st.selectbox(label="Choose Player", options=result)

        if st.form_submit_button(f"Remove Selected {st.session_state.remove_emoji}"):
            result = fetch_delete(f"{settings.driftapi_path}/driftapi/game/{lobby_id}/remove_player/{user_name}/highscores")
            st.session_state.nextpage = "highscore_list"
            st.experimental_rerun()

    if st.button(f"Back {st.session_state.back_emoji}"):
        st.session_state.nextpage = "highscore_list"
        st.experimental_rerun()

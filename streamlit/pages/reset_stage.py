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
    game_id = st.session_state.game_id
    num_stages = st.session_state.num_stages

    result = []
    for x in range(num_stages):
        result.append(x+1)
    
    st.write("Reset a Stage of Event " + str(game_id) + " of Lobby: " + str(lobby_id))

    with st.form("my_form"):

        stage_id = st.selectbox(label="Choose Stage", options=result)

        if st.form_submit_button(f"Reset Selected {st.session_state.reset_emoji}"):
            result = fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/reset_stage/{lobby_id}/{game_id}/{stage_id}")
            st.session_state.stage_id = 1
            st.session_state.nextpage = "stage_racedisplay"
            st.experimental_rerun()

    if st.button(f"Back to Event {st.session_state.back_emoji}"):
        st.session_state.nextpage = "stage_racedisplay"
        st.experimental_rerun()

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
    stage_id = st.session_state.stage_id

    st.write("Remove Player from Game " + str(game_id) + " of Lobby: " + str(lobby_id))

    with st.form("my_form"):
        result = fetch_get(f"{settings.driftapi_path}/driftapi/game/{lobby_id}/{game_id}/{stage_id}/playerstatus")
        result = [r["user_name"] for r in result if (type(r) is dict) and ("user_name" in r.keys())]
        player_id = st.selectbox(label="Choose Player", options=result)

        if st.form_submit_button(f"Delete Selected {st.session_state.remove_emoji}"):
            result = fetch_delete(f"{settings.driftapi_path}/driftapi/manage_game/reset_player/{lobby_id}/{game_id}/{player_id}")
            game = fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/get/{lobby_id}/{game_id}/{stage_id}/")
            if(game["num_stages"] == 1):
                st.session_state.num_stages = 1
                st.session_state.nextpage = "racedisplay"
            else:
                st.session_state.num_stages = game["num_stages"]
                st.session_state.nextpage = "stage_racedisplay"
            st.experimental_rerun()


    if st.button(f"Back to Race {st.session_state.back_emoji}"):
        game = fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/get/{lobby_id}/{game_id}/{stage_id}/")
        if(game["num_stages"] == 1):
            st.session_state.num_stages = 1
            st.session_state.nextpage = "racedisplay"
        else:
            st.session_state.num_stages = game["num_stages"]
            st.session_state.nextpage = "stage_racedisplay"
        st.experimental_rerun()

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

    placeholder1 = st.empty()
    placeholder2 = st.empty()
    placeholder3 = st.empty()

    with placeholder1.container(): 
        st.write("Remove Player from Game " + str(game_id) + " of Lobby: " + str(lobby_id))

    with placeholder2.container(): 
        with st.form("my_form"):
            result = fetch_get(f"{settings.driftapi_path}/driftapi/game/{lobby_id}/{game_id}/{stage_id}/playerstatus")
            result = [r["user_name"] for r in result if (type(r) is dict) and ("user_name" in r.keys())]
            user_name = st.selectbox(label="Choose Player", options=result)

            if st.form_submit_button(f"Delete Selected {st.session_state.remove_emoji}"):
                result = fetch_delete(f"{settings.driftapi_path}/driftapi/manage_game/reset_player/{lobby_id}/{game_id}/{user_name}")
                game = fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/get/{lobby_id}/{game_id}/{stage_id}/")
                if(game["num_stages"] == 1):
                    st.session_state.num_stages = 1
                    st.session_state.nextpage = "racedisplay"
                    st.session_state.show_awards = False
                else:
                    st.session_state.num_stages = game["num_stages"]
                    st.session_state.nextpage = "stage_racedisplay"
                    st.session_state.show_awards = False
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                time.sleep(0.1)
                st.experimental_rerun()

    with placeholder3.container(): 
        if st.button(f"Back to Race {st.session_state.back_emoji}"):
            game = fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/get/{lobby_id}/{game_id}/{stage_id}/")
            if(game["num_stages"] == 1):
                st.session_state.num_stages = 1
                st.session_state.nextpage = "racedisplay"
            else:
                st.session_state.num_stages = game["num_stages"]
                st.session_state.nextpage = "stage_racedisplay"
            placeholder1.empty()
            placeholder2.empty()
            placeholder3.empty()
            time.sleep(0.1)
            st.experimental_rerun()

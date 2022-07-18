import streamlit as st
import time

from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger

import os
from os.path import exists

def app():

    lobby_id = st.session_state.lobby_id        
    game_id = None
    stage_id = 1

    st.subheader("Delete Game from Lobby " + str(lobby_id))

    placeholder1 = st.empty()
    placeholder2 = st.empty()
    
    with placeholder1.container():
        if 'game_id' not in st.session_state:
            with st.form("my_form"):
                result = fetch_post(f"{settings.driftapi_path}/driftapi/manage_game/find/{lobby_id}", {})
                if result:
                    result = [r["game_id"] for r in result if ("game_id" in r.keys())]
                    game_id = st.selectbox(label="Choose Game", options=result)
                    if st.form_submit_button(f"Delete {st.session_state.delete_emoji}"):
                    
                        game = fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/get/{lobby_id}/{game_id}/{stage_id}/")
                        
                        if( game["game_mode"] == "GYMKHANA_TRAINING" ):
                            os.makedirs("gymkhana_training/" + str(lobby_id) + "/" + str(game_id) + "/runs/", exist_ok=True)
                            dir_name = "gymkhana_training/" + str(lobby_id) + "/" + str(game_id) + "/runs/"
                            output_filename = "Gymkhana_Training_" + str(lobby_id) + "_" + str(game_id)
                            zip_path = "gymkhana_training/" + str(lobby_id) + "/" + str(game_id) + "/" 
                            if len(os.listdir(str(dir_name))) != 0:
                                for f in os.listdir(dir_name):
                                    os.remove(os.path.join(dir_name, f))
                                if os.path.exists(str(zip_path) + str(output_filename) + ".zip"):
                                    os.remove(str(zip_path) + str(output_filename) + ".zip")
                        result = fetch_delete(f"{settings.driftapi_path}/driftapi/manage_game/delete/{lobby_id}/{game_id}")
                        st.session_state.game_id = None
                        st.session_state.stage_id = 1
                        st.session_state.num_stages = 1
                        st.session_state.nextpage = "main_page"
                        placeholder1.empty()
                        placeholder2.empty()
                        time.sleep(0.1)
                        st.experimental_rerun()

    with placeholder2.container():
        if st.button(f"Back {st.session_state.back_emoji}"):
            st.session_state.nextpage = "main_page"
            placeholder1.empty()
            placeholder2.empty()
            time.sleep(0.1)
            st.experimental_rerun()

import streamlit as st
import pandas as pd 
from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings

def app():

    st.session_state.new_stage_event = False
    st.session_state.new_game = False
    
    lobby_id = st.session_state.lobby_id        

    st.header("You are currently in Lobby " + str(lobby_id))

    if 'game_id' in st.session_state:
        del st.session_state.game_id
    if 'stage_id' in st.session_state:
        del st.session_state.stage_id
    if 'num_stages' in st.session_state:
        del st.session_state.num_stages
    if 'stage_track_images_set' in st.session_state:
        del st.session_state.stage_track_images_set
    if 'stage_track_images' in st.session_state:
        del st.session_state.stage_track_images
    if 'game_track_images_set' in st.session_state:
        del st.session_state.game_track_images_set
    if 'game_track_images' in st.session_state:
        del st.session_state.game_track_images

    if st.button(f"New Race Game {st.session_state.create_emoji}"):
        st.session_state.nextpage = "create_race_game"
        st.experimental_rerun()
        
    if st.button(f"New Gymkhana Game {st.session_state.create_emoji}"):
        st.session_state.nextpage = "create_gymkhana_game"
        st.experimental_rerun()

    if st.button(f"New Stage Race Game {st.session_state.create_emoji}"):
        st.session_state.nextpage = "create_pre_stagerace_game"
        st.experimental_rerun()

    if st.button(f"Show Game {st.session_state.show_game_emoji}"):
        st.session_state.nextpage = "select_race"
        st.experimental_rerun()

    if st.button(f"Delete Game {st.session_state.delete_emoji}"):
        st.session_state.nextpage = "delete_race"
        st.experimental_rerun()


    if st.button(f"Quit Lobby " + str(lobby_id) + f" {st.session_state.quit_emoji}"):
        st.session_state.nextpage = "pre_mainpage"
        st.experimental_rerun()

    st.write("Available Games in Lobby " + str(lobby_id))
    result = fetch_post(f"{settings.driftapi_path}/driftapi/manage_game/find/{lobby_id}/", {})
    if result:
        result = pd.DataFrame( [{"game_id":r["game_id"]} for r in result if ("game_id" in r)] )
        st.write(result)
        

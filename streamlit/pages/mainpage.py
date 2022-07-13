import streamlit as st
import time

import pandas as pd 
from .session import fetch_post, fetch_put, fetch_get, fetch_delete
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
    if 'game_track_images_set' in st.session_state:
        del st.session_state.game_track_images_set
    if 'game_track_images' in st.session_state:
        del st.session_state.game_track_images
    if 'game_track_images_set' in st.session_state:
        del st.session_state.game_track_images_set
    if 'game_track_images' in st.session_state:
        del st.session_state.game_track_images
    if 'show_awards' in  st.session_state:
        del st.session_state.show_awards

    placeholder1 = st.empty()
    placeholder2 = st.empty()
    placeholder3 = st.empty()
    placeholder4 = st.empty()
    placeholder5 = st.empty()
    
    with placeholder1.container():

        colM11, colM12, colM13, colM14 = st.columns(4)

        with colM11:
            if st.button(f"New Race Game {st.session_state.create_emoji}"):
                st.session_state.nextpage = "create_race_game"
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                placeholder4.empty()
                placeholder5.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with colM12:        
            if st.button(f"New Gymkhana Game {st.session_state.create_emoji}"):
                st.session_state.nextpage = "create_gymkhana_game"
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                placeholder4.empty()
                placeholder5.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with colM13:
            if st.button(f"New Stage Race Game {st.session_state.create_emoji}"):
                st.session_state.nextpage = "create_pre_stagerace_game"
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                placeholder4.empty()
                placeholder5.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with colM14:
            if st.button(f"New Gymkhana Training {st.session_state.create_emoji}"):
                st.session_state.nextpage = "create_gymkhana_training"
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                placeholder4.empty()
                placeholder5.empty()
                time.sleep(0.1)
                st.experimental_rerun()

    with placeholder2.container():

        colM21, colM22, colM23, colM24 = st.columns(4)

        with colM21:
            if st.button(f"New Lap Race Game {st.session_state.create_emoji}"):
                st.session_state.nextpage = "create_lap_race_game"
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                placeholder4.empty()
                placeholder5.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with colM22:
            if st.button(f"New Time Race Game {st.session_state.create_emoji}"):
                st.session_state.nextpage = "create_time_race_game"
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                placeholder4.empty()
                placeholder5.empty()
                time.sleep(0.1)
                st.experimental_rerun()

    with placeholder3.container():

        colM31, colM32, colM33, colM34 = st.columns(4)

        with colM31:
            if st.button(f"Gymkhana High Scores {st.session_state.award_trophy_emoji}"):
                st.session_state.nextpage = "highscore_list"
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                placeholder4.empty()
                placeholder5.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with colM32:
            if st.button(f"Show Game {st.session_state.show_game_emoji}"):
                st.session_state.nextpage = "select_race"
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                placeholder4.empty()
                placeholder5.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with colM33:
            if st.button(f"Delete Game {st.session_state.delete_emoji}"):
                st.session_state.nextpage = "delete_race"
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                placeholder4.empty()
                placeholder5.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with colM34:
            if st.button(f"Quit Lobby " + str(lobby_id) + f" {st.session_state.quit_emoji}"):
                st.session_state.nextpage = "pre_mainpage"
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                placeholder4.empty()
                placeholder5.empty()
                time.sleep(0.1)
                st.experimental_rerun()

    # CSS to inject contained in a string
    hide_dataframe_row_index = """
                <style>
                .row_heading.level0 {display:none}
                .blank {display:none}
                </style>
    """
    # Inject CSS with Markdown
    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

    with placeholder4.container():
        st.write("Available Games in Lobby " + str(lobby_id))
       
    with placeholder5.container():
        result = fetch_post(f"{settings.driftapi_path}/driftapi/manage_game/find/{lobby_id}/", {})
        if result:
            result = pd.DataFrame( [{"game_id":r["game_id"], "game_mode":r["game_mode"]} for r in result if ("game_id" in r)] )
            st.write(result)
        

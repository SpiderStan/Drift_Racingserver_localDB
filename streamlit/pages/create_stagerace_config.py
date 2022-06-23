import streamlit as st
from zoneinfo import ZoneInfo #to set the timezone to german time
from enum import Enum
from datetime import datetime, timezone, timedelta
from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger
from .model import track_condition, track_bundle, wheels, setup_mode, target_code, game_mode

def app():

    lobby_id = st.session_state.lobby_id
    num_stages = st.session_state.num_stages

    game_type_selected = ["RACE","RACE","RACE","RACE","RACE","RACE","RACE","RACE","RACE","RACE","RACE","RACE","RACE","RACE","RACE","RACE","RACE","RACE","RACE","RACE"]

    st.write("Configure the new Stage Race Game in Lobby " + str(lobby_id) + " (Part 1)")
        
    with st.form("my_form", clear_on_submit=True):
        gameOptions = {}
        game_id = st.text_input("Game ID", value="Stage1", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, disabled=False)
        for x in range(num_stages):
            game_type_selected[x] = st.selectbox(label="Game Type of Stage " + str(x+1), options=[e.value for e in game_mode])
        submitted = st.form_submit_button(f"Go to Stage Config (Part 2) {st.session_state.create_emoji}")
        if submitted:
            st.session_state.game_type_selected = game_type_selected
            st.session_state.nextpage = "create_stagerace_game"
            st.session_state.game_id = game_id
            st.session_state.stage_id = 1
            st.session_state.num_stages = num_stages
            st.experimental_rerun()

    if st.button(f"Back {st.session_state.back_emoji}"):
        st.session_state.nextpage = "main_page"
        st.experimental_rerun()
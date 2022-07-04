import streamlit as st
import time
from zoneinfo import ZoneInfo #to set the timezone to german time
from enum import Enum
from datetime import datetime, timezone, timedelta
from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger
from .model import track_condition, track_bundle, wheels, setup_mode, target_code, bonus_target, gymkhana_training_targets

# Spider: not used at the moment
def createGameOptionContainer(label:str, options:Enum):
    with st.container():
        columnLeft, columnRight = st.columns(2)
        with columnLeft:
            enabled = st.checkbox("Sync. "+label, value=False, key=None, help=None, on_change=None)
#            enabled = st.checkbox("Enable "+label, value=False, key=None, help=None, on_change=None)
        with columnRight:
            selected = st.selectbox(label=label, options=[e.value for e in options])
        if enabled:
            return {label:selected}
        else:
            return {}
        

def app():

    lobby_id = st.session_state.lobby_id        

    st.header("Create new Gymkhana Training in Lobby " + str(lobby_id))
        
    placeholder1 = st.empty()
    placeholder2 = st.empty()

    with placeholder1.container():   
        with st.form("my_form", clear_on_submit=True):
            gameOptions = {}
            game_id = st.text_input("Game ID", value="Train1", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, disabled=False)
            gymkhana_training_selected = st.selectbox(label="target sequence", options=[e.value for e in gymkhana_training_targets], index=0)

            with st.expander(f"Optional settings {st.session_state.tweak_game_emoji}", expanded=True):
                #password = st.text_input("password", value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, disabled=False)
                track_id = st.text_input("Track name", value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, disabled=False)

                with st.container():
                    columnLeft, columnRight = st.columns(2)
                    with columnLeft:
                       track_condition_enabled = st.checkbox("Sync. track condition", value=True, key=None, help=None, on_change=None)
                    with columnRight:
                       track_condition_selected = st.selectbox(label="track condition", options=[e.value for e in track_condition])

                with st.container():
                    columnLeft, columnRight = st.columns(2)
                    with columnLeft:
                        wheels_enabled = st.checkbox("Sync. wheels", value=True, key=None, help=None, on_change=None)
                    with columnRight:
                        wheels_selected = st.selectbox(label="wheels", options=[e.value for e in wheels])

                with st.container():
                    columnLeft, columnRight = st.columns(2)
                    with columnLeft:
                        setup_mode_enabled = st.checkbox("Sync. setup mode", value=True, key=None, help=None, on_change=None)
                    with columnRight:
                        setup_mode_selected = st.selectbox(label="setup mode", options=[e.value for e in setup_mode], index=1)

            submitted = st.form_submit_button(f"Create {st.session_state.create_emoji}")

            if submitted:
                    body = {
                        "lobby_id" : lobby_id,
                        "game_id" : game_id,
                        "track_id" : track_id,
                    }

                    if track_condition_enabled:
                        body['track_condition'] = str(track_condition_selected)

                    if wheels_enabled:
                        body['wheels'] = str(wheels_selected)

                    if setup_mode_enabled:
                        body['setup_mode'] = str(setup_mode_selected)

                    body['game_mode'] = "GYMKHANA_TRAINING" 

                    body['individual_trial'] = True
                    
                    body['gymkhana_training_targets'] = str(gymkhana_training_selected)

                    num_stages = 1
                    stage_id = 1
                    body['num_stages'] = str(num_stages)
                    body['stage_id'] = str(stage_id)

                    result = fetch_post(f"{settings.driftapi_path}/driftapi/manage_game/create/{lobby_id}", body)

                    #if result:
                        #st.success("Race has been created")
                        #st.write(result)

                    st.session_state.nextpage = "gymkhana_training_racedisplay"
                    st.session_state.new_game = True
                    st.session_state.game_id = game_id
                    st.session_state.stage_id = stage_id
                    st.session_state.num_stages = num_stages
                    st.session_state.game_track_images_set = False
                    st.session_state.game_track_images = None
                    st.session_state.show_awards = False
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
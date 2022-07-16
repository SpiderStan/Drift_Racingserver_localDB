import streamlit as st
import time
from zoneinfo import ZoneInfo #to set the timezone to german time
from enum import Enum
from datetime import datetime, timezone, timedelta
from .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger
from .model import track_condition, track_bundle, wheels, setup_mode, target_code

# not used at the moment
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

    st.header("Create new Elimination Game in Lobby " + str(lobby_id))

    placeholder1 = st.empty()
    placeholder2 = st.empty()

    with placeholder1.container():
        with st.form("my_form", clear_on_submit=True):
            gameOptions = {}
            game_id = st.text_input("Game ID", value="Elim1", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, disabled=False)
            
            time_limit = st.number_input("elimination time [m]", min_value=1, max_value=10000, value=3, step=1, format=None, key=None, help="eliminate each x minutes", on_change=None, disabled = False)

# change start time widget in order to be able to select start time in minute intervalls
            start = "00:00"
            end = "23:59"
            times = []
            start = now = datetime.strptime(start, "%H:%M")
            end = datetime.strptime(end, "%H:%M")
            while now != end:
                times.append(str(now.strftime("%H:%M")))
                now += timedelta(minutes=1)
            times.append(end.strftime("%H:%M"))

            time1 = datetime.now(tz=ZoneInfo("Europe/Berlin"))
            timedelta_1 = time1.utcoffset()
# make sure that start index is current time + 2 minutes for quick start possibility
            start_time = st.selectbox('Start time (Local)',times, index=(times.index(datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime("%H:%M")))+2, key=None, help=None, on_change=None, disabled = False)
            start_time = datetime.strptime(start_time, '%H:%M').time()
            start_time = datetime.combine(datetime.today(), start_time)-timedelta_1
            start_time = start_time.astimezone(timezone.utc)            

            num_sectors = st.number_input("sectors", min_value=1, max_value=9, value=5, step=1, format=None, key=None, help="number of sectors", on_change=None, disabled = False)

#            individual_trial = st.checkbox("Individual Time Trail Mode", value=False, key=None, help="if set, user can decide when award ceremony should take place", on_change=None)

            with st.expander(f"Optional settings {st.session_state.tweak_game_emoji}", expanded=True):
                #password = st.text_input("password", value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, disabled=False)
                track_id = st.text_input("Track name", value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, disabled=False)

                with st.container():
                    columnLeft, columnRight = st.columns(2)
                    with columnLeft:
                       track_condition_enabled = st.checkbox("Sync. track condition", value=False, key=None, help=None, on_change=None)
                    with columnRight:
                       track_condition_selected = st.selectbox(label="track condition", options=[e.value for e in track_condition])

                with st.container():
                    columnLeft, columnRight = st.columns(2)
                    with columnLeft:
                        track_bundle_enabled = st.checkbox("Sync. track bundle", value=False, key=None, help=None, on_change=None)
                    with columnRight:
                        track_bundle_selected = st.selectbox(label="track bundle", options=[e.value for e in track_bundle])

                with st.container():
                    columnLeft, columnRight = st.columns(2)
                    with columnLeft:
                        wheels_enabled = st.checkbox("Sync. wheels", value=False, key=None, help=None, on_change=None)
                    with columnRight:
                        wheels_selected = st.selectbox(label="wheels", options=[e.value for e in wheels])

                with st.container():
                    columnLeft, columnRight = st.columns(2)
                    with columnLeft:
                        setup_mode_enabled = st.checkbox("Sync. setup mode", value=False, key=None, help=None, on_change=None)
                    with columnRight:
                        setup_mode_selected = st.selectbox(label="setup mode", options=[e.value for e in setup_mode])

                with st.container():
                    columnLeft, columnRight = st.columns(2)
                    with columnLeft:
                        joker_lap_enabled = st.checkbox("Enable Joker Lap Counter", value=False, key=None, help=None, on_change=None)
                        joker_lap_precondition_enabled = st.checkbox("Enable precondition", value=False, key=None, help="when a precondition code is set, the actual joker lap code is only counted when the racer deceted the precondition code right before the joker lap code.", on_change=None)
                    with columnRight:
                        options = {"start/finish":target_code.start_finish, "angle drift":target_code.angle_drift, "360":target_code.threesixty, "180 speed":target_code.oneeighty, "speed drift":target_code.speed_drift}
                        joker_lap_code = str(options[st.selectbox(label="Code to be used for joker lap", options=[*options], index=1)].value)
                        joker_lap_precondition_code = str(options[st.selectbox(label="Additional code that need to be detected before the actual joker lap code", options=[*options], index=1)].value)

            submitted = st.form_submit_button(f"Create {st.session_state.create_emoji}")

            if submitted:
                    body = {
                        "lobby_id" : lobby_id,
                        "game_id" : game_id,
                        "track_id" : track_id,
                    }

                    body['start_time'] = str(start_time)

                    body['time_limit'] = str(time_limit)

                    body['lap_count'] = str(100)

                    if track_condition_enabled:
                        body['track_condition'] = str(track_condition_selected)

                    if track_bundle_enabled:
                        body['track_bundle'] = str(track_bundle_selected)

                    if wheels_enabled:
                        body['wheels'] = str(wheels_selected)

                    if setup_mode_enabled:
                        body['setup_mode'] = str(setup_mode_selected)

                    body['game_mode'] = "ELIMINATION" 

                    if joker_lap_enabled:
                        body['joker_lap_code'] = str(joker_lap_code)

                        if joker_lap_precondition_enabled:
                            body['joker_lap_precondition_code'] = str(joker_lap_precondition_code)

#                    body['individual_trial'] = individual_trial

                    body['num_sectors'] = str(num_sectors)

                    num_stages = 1
                    stage_id = 1
                    body['num_stages'] = str(num_stages)
                    body['stage_id'] = str(stage_id)

                    result = fetch_post(f"{settings.driftapi_path}/driftapi/manage_game/create/{lobby_id}", body)

                    #if result:
                        #st.success("Race has been created")
                        #st.write(result)

                    st.session_state.nextpage = "eliminationracedisplay"
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
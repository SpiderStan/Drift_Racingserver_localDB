import streamlit as st
from zoneinfo import ZoneInfo #to set the timezone to german time
from enum import Enum
from datetime import datetime, timezone, timedelta
from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger
from .model import track_condition, track_bundle, wheels, setup_mode, target_code, bonus_target

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

    st.write("Create new Gymkhana Game in Lobby " + str(lobby_id))
        
    with st.form("my_form", clear_on_submit=True):
        gameOptions = {}
        game_id = st.text_input("Game ID", value="Drift1", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, disabled=False)

        with st.expander(f"Optional settings {st.session_state.tweak_game_emoji}", expanded=True):
            #password = st.text_input("password", value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, disabled=False)
            track_id = st.text_input("Track name", value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, disabled=False)

            with st.container():
                columnLeft, columnRight = st.columns(2)

                with columnLeft:
                    start_time_enabled = st.checkbox("Sync. start time", value=False, key=None, help=None, on_change=None)
                with columnRight:

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

            with st.container():
                columnLeft, columnRight = st.columns(2)
                with columnLeft:
                   track_condition_enabled = st.checkbox("Sync. track condition", value=False, key=None, help=None, on_change=None)
                with columnRight:
                   track_condition_selected = st.selectbox(label="track condition", options=[e.value for e in track_condition])

            with st.container():
                columnLeft, columnRight = st.columns(2)
                with columnLeft:
                    wheels_enabled = st.checkbox("Sync. wheels", value=False, key=None, help=None, on_change=None)
                with columnRight:
                    wheels_selected = st.selectbox(label="wheels", options=[e.value for e in wheels])

            with st.container():
                columnLeft, columnRight = st.columns(2)
                with columnLeft:
                    setup_mode_enabled = st.checkbox("Sync. setup mode", value=True, key=None, help=None, on_change=None)
                with columnRight:
                    setup_mode_selected = st.selectbox(label="setup mode", options=[e.value for e in setup_mode], index=1)

            with st.container():
                columnLeft, columnRight = st.columns(2)
                with columnLeft:
                    bonus_target_set = st.checkbox("Set Different Bonus Target", value=False, key=None, help="here you can select the bonus target for best target medal (if not activated, default bonus target will be 360)", on_change=None)
                with columnRight:
                    bonus_target_selected = st.selectbox(label="bonus target", options=[e.value for e in bonus_target])

        submitted = st.form_submit_button(f"Create {st.session_state.create_emoji}")

        if submitted:
                body = {
                    "lobby_id" : lobby_id,
                    "game_id" : game_id,
                    "track_id" : track_id,
                }

                if start_time_enabled:
                    body['start_time'] = str(start_time)

                if track_condition_enabled:
                    body['track_condition'] = str(track_condition_selected)

                if wheels_enabled:
                    body['wheels'] = str(wheels_selected)

                if setup_mode_enabled:
                    body['setup_mode'] = str(setup_mode_selected)

                body['game_mode'] = "GYMKHANA" 

                if bonus_target_set:
                    body['bonus_target'] = str(bonus_target_selected)

                num_stages = 1
                stage_id = 1
                body['num_stages'] = str(num_stages)
                body['stage_id'] = str(stage_id)

                result = fetch_post(f"{settings.driftapi_path}/driftapi/manage_game/create/{lobby_id}", body)

                #if result:
                    #st.success("Race has been created")
                    #st.write(result)

                st.session_state.nextpage = "racedisplay"
                st.session_state.game_id = game_id
                st.session_state.stage_id = stage_id
                st.session_state.num_stages = num_stages
                st.experimental_rerun()

    if st.button(f"Back to Main Menu {st.session_state.back_emoji}"):
        st.session_state.nextpage = "main_page"
        st.experimental_rerun()
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

def getGameInfo(lobby_id, game_id, stage_id):
    return fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/get/{lobby_id}/{game_id}/{stage_id}/")

def app():

    lobby_id = st.session_state.lobby_id
    game_id = st.session_state.game_id
    num_stages = st.session_state.num_stages
    game_type_selected = st.session_state.game_type_selected

    st.write("Configure the new Stage Race Game " + str(game_id) + " in Lobby " + str(lobby_id) + " (Part 2)")
    
    track_id = ["","","","","","","","","",""]
    time_limit_enabled = [False,False,False,False,False,False,False,False,False,False]
    time_limit = [None,None,None,None,None,None,None,None,None,None]
    lap_limit_enabled = [False,False,False,False,False,False,False,False,False,False]
    lap_count = [None,None,None,None,None,None,None,None,None,None]
    track_condition_enabled = [False,False,False,False,False,False,False,False,False,False]
    track_condition_selected = [None,None,None,None,None,None,None,None,None,None]
    track_bundle_enabled = [False,False,False,False,False,False,False,False,False,False]
    track_bundle_selected = [None,None,None,None,None,None,None,None,None,None]
    wheels_enabled = [False,False,False,False,False,False,False,False,False,False]
    wheels_selected = [None,None,None,None,None,None,None,None,None,None]
    setup_mode_enabled = [False,False,False,False,False,False,False,False,False,False]
    setup_mode_selected = [None,None,None,None,None,None,None,None,None,None]
    joker_lap_enabled = [False,False,False,False,False,False,False,False,False,False]
    joker_lap_precondition_enabled = [False,False,False,False,False,False,False,False,False,False]
    joker_lap_code = [None,None,None,None,None,None,None,None,None,None]
    joker_lap_precondition_code = [None,None,None,None,None,None,None,None,None,None]
    bonus_target_set = [False,False,False,False,False,False,False,False,False,False]
    bonus_target_selected = [None,None,None,None,None,None,None,None,None,None]
    
    with st.form("my_form", clear_on_submit=True):
        gameOptions = {}

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
        start_time = st.selectbox('Start time (Local)',times, index=(times.index(datetime.now(tz=ZoneInfo("Europe/Berlin")).strftime("%H:%M")))+2, key=None, help="Might be the start time for the first stage; however you always can sync. the start time to be two minutes in the future once in stage overview", on_change=None, disabled = False)
        start_time = datetime.strptime(start_time, '%H:%M').time()
        start_time = datetime.combine(datetime.today(), start_time)-timedelta_1
        start_time = start_time.astimezone(timezone.utc)

        for x in range(num_stages):

            with st.expander(f"Optional settings for Stage " + str(x+1) + f" with game mode " + str(game_type_selected[x]) + f" {st.session_state.tweak_game_emoji}", expanded=True):

                track_id[x] = st.text_input("Stage " + str(x+1) + " Track name", value="", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, disabled=False)
                
                if(game_type_selected[x] == "RACE"):
                    with st.container():
                        columnLeft, columnRight = st.columns(2)
                        with columnLeft:
                            time_limit_enabled[x] = st.checkbox("Sync. time limit", value=False, key="Sync. time limit "+str(x+1), help=None, on_change=None)
                        with columnRight:
                            time_limit[x] = st.number_input("time [m]", min_value=0, max_value=10000, value=10, step=1, format=None, key="time_limit "+str(x+1), help="time limit in minutes", on_change=None, disabled = False)

                    with st.container():
                        columnLeft, columnRight = st.columns(2)
                        with columnLeft:
                            lap_limit_enabled[x] = st.checkbox("Sync. lap limit", value=True, key="Sync. lap limit "+str(x+1), help=None, on_change=None)
                        with columnRight:
                            lap_count[x] = st.number_input("laps", min_value=0, max_value=100, value=3, step=1, format=None, key="lap_count "+str(x+1), help="number of laps", on_change=None, disabled = False)

                    with st.container():
                        columnLeft, columnRight = st.columns(2)
                        with columnLeft:
                           track_condition_enabled[x] = st.checkbox("Sync. track condition", value=True, key="Sync. track condition "+str(x+1), help=None, on_change=None)
                        with columnRight:
                           track_condition_selected[x] = st.selectbox(label="track condition", key="track condition "+str(x+1), options=[e.value for e in track_condition])

                    with st.container():
                        columnLeft, columnRight = st.columns(2)
                        with columnLeft:
                            track_bundle_enabled[x] = st.checkbox("Sync. track bundle", value=True, key="Sync. track bundle "+str(x+1), help=None, on_change=None)
                        with columnRight:
                            track_bundle_selected[x] = st.selectbox(label="track bundle", key="track bundle "+str(x+1), options=[e.value for e in track_bundle])

                    with st.container():
                        columnLeft, columnRight = st.columns(2)
                        with columnLeft:
                            wheels_enabled[x] = st.checkbox("Sync. wheels", value=True, key="Sync. wheels "+str(x+1), help=None, on_change=None)
                        with columnRight:
                            wheels_selected[x] = st.selectbox(label="wheels", key="wheels "+str(x+1), options=[e.value for e in wheels])

                    with st.container():
                        columnLeft, columnRight = st.columns(2)
                        with columnLeft:
                            setup_mode_enabled[x] = st.checkbox("Sync. setup mode", value=True, key="Sync. setup mode "+str(x+1), help=None, on_change=None)
                        with columnRight:
                            setup_mode_selected[x] = st.selectbox(label="setup mode", key="setup mode "+str(x+1), options=[e.value for e in setup_mode])

                    with st.container():
                        columnLeft, columnRight = st.columns(2)
                        with columnLeft:
                            joker_lap_enabled[x] = st.checkbox("Enable Joker Lap Counter", value=False, key="Enable Joker Lap Counter "+str(x+1), help=None, on_change=None)
                            joker_lap_precondition_enabled[x] = st.checkbox("Enable precondition", value=False, key="Enable precondition "+str(x+1), help="when a precondition code is set, the actual joker lap code is only counted when the racer detected the precondition code right before the joker lap code.", on_change=None)
                        with columnRight:
                            options = {"start/finish":target_code.start_finish, "angle drift":target_code.angle_drift, "360":target_code.threesixty, "180 speed":target_code.oneeighty, "speed drift":target_code.speed_drift}
                            joker_lap_code[x] = str(options[st.selectbox(label="Code to be used for joker lap", key="joker_lap_code "+str(x+1), options=[*options], index=1)].value)
                            joker_lap_precondition_code[x] = str(options[st.selectbox(label="Additional code that need to be detected before the actual joker lap code", key="joker_lap_precondition_code "+str(x+1), options=[*options], index=1)].value)
                else:
                    with st.container():
                        columnLeft, columnRight = st.columns(2)
                        with columnLeft:
                           track_condition_enabled[x] = st.checkbox("Sync. track condition", value=True, key="Sync. track condition "+str(x+1), help=None, on_change=None)
                        with columnRight:
                           track_condition_selected[x] = st.selectbox(label="track condition", key="track condition "+str(x+1), options=[e.value for e in track_condition])

                    with st.container():
                        columnLeft, columnRight = st.columns(2)
                        with columnLeft:
                            wheels_enabled[x] = st.checkbox("Sync. wheels", value=True, key="Sync. wheels "+str(x+1), help=None, on_change=None)
                        with columnRight:
                            wheels_selected[x] = st.selectbox(label="wheels", key="wheels "+str(x+1), options=[e.value for e in wheels])

                    with st.container():
                        columnLeft, columnRight = st.columns(2)
                        with columnLeft:
                            setup_mode_enabled[x] = st.checkbox("Sync. setup mode", value=True, key="Sync. setup mode "+str(x+1), help=None, on_change=None)
                        with columnRight:
                            setup_mode_selected[x] = st.selectbox(label="setup mode", key="setup mode "+str(x+1), options=[e.value for e in setup_mode], index=1)

                    with st.container():
                        columnLeft, columnRight = st.columns(2)
                        with columnLeft:
                            bonus_target_set[x] = st.checkbox("Set Different Bonus Target", value=True, key="Set Different Bonus Target "+str(x+1), help="here you can select the bonus target for best target medal (if not activated, default bonus target will be 360)", on_change=None)
                        with columnRight:
                            bonus_target_selected[x] = st.selectbox(label="bonus target", key="bonus target "+str(x+1), options=[e.value for e in bonus_target])
                  
        submitted = st.form_submit_button(f"Create {st.session_state.create_emoji}")

        if submitted:
        
            for x in range(num_stages):

                body = {
                    "lobby_id" : lobby_id,
                    "game_id" : game_id,
                    "track_id" : track_id[x],
                    "num_stages" : num_stages,
                    "stage_id" : str(x+1),
                    "game_mode" : str(game_type_selected[x]),
                }

                body['start_time'] = str(start_time)

                if(game_type_selected[x] == "RACE"):
                    if time_limit_enabled[x]:
                        body['time_limit'] = str(time_limit[x])

                    if lap_limit_enabled[x]:
                        body['lap_count'] = str(lap_count[x])

                    if track_condition_enabled[x]:
                        body['track_condition'] = str(track_condition_selected[x])

                    if track_bundle_enabled[x]:
                        body['track_bundle'] = str(track_bundle_selected[x])

                    if wheels_enabled[x]:
                        body['wheels'] = str(wheels_selected[x])

                    if setup_mode_enabled[x]:
                        body['setup_mode'] = str(setup_mode_selected[x])

                    if joker_lap_enabled[x]:
                        body['joker_lap_code'] = str(joker_lap_code[x])

                        if joker_lap_precondition_enabled[x]:
                            body['joker_lap_precondition_code'] = str(joker_lap_precondition_code[x])

                else:
                    if track_condition_enabled[x]:
                        body['track_condition'] = str(track_condition_selected[x])

                    if wheels_enabled[x]:
                        body['wheels'] = str(wheels_selected[x])

                    if setup_mode_enabled[x]:
                        body['setup_mode'] = str(setup_mode_selected[x])

                    if bonus_target_set[x]:
                        body['bonus_target'] = str(bonus_target_selected[x])
                    
                result = fetch_post(f"{settings.driftapi_path}/driftapi/manage_game/create/{lobby_id}", body)

# enbale new stage game racedisplay
            st.session_state.nextpage = "stage_racedisplay"
            st.session_state.game_id = game_id
            st.session_state.stage_id = 1
            st.session_state.num_stages = num_stages
            st.experimental_rerun()

    if st.button(f"Back to Main Menu {st.session_state.back_emoji}"):
        if 'game_type_selected' in st.session_state:
            del st.session_state.game_type_selected
        st.session_state.game_id = None
        st.session_state.stage_id = 1
        st.session_state.num_stages = 1
        st.session_state.nextpage = "main_page"
        st.experimental_rerun()
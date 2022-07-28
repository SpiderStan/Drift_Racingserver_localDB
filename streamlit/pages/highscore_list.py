import streamlit as st
import time
#import socket
from zoneinfo import ZoneInfo #to set the timezone to german time
from datetime import timedelta, timezone, datetime
import pandas as pd 
import numpy as np
import operator
from PIL import Image
from math import floor

from .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger
from .helper import get_game_mode, get_starttime, get_track_cond, get_track_bundle, get_wheels, get_setup, get_bool, get_model, get_tuning, handleCurrentTrackCondition

def getGameInfo(lobby_id, game_id, stage_id):
    return fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/get/{lobby_id}/{game_id}/{stage_id}/")

def getHighScoreBoard(lobby_id):
    return fetch_get(f"{settings.driftapi_path}/driftapi/game/{lobby_id}/highscores")

def app():   

    m = st.markdown("""
    <style>
    div.stButton > button:first-child {
        color: white;
        height: 2em;
        width: 13em;
        border-radius:10px;
        font-size:15px;
        font-weight: bold;
        margin: auto;
    }

    div.stButton > button:active {
        position:relative;
        top:3px;
    }

    </style>""", unsafe_allow_html=True)

    lobby_id = st.session_state.lobby_id        
    
    st.subheader("Gymkhana High Score List of Lobby " + str(lobby_id))

    placeholder1 = st.empty()
    highscoreboard = st.empty()
    
    with placeholder1.container():

        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

        with col1:
            if st.button(f"Back {st.session_state.back_emoji}"):
                if 'game_id' in st.session_state:
                    game = getGameInfo(lobby_id, st.session_state.game_id, 1)
                    if not game:
                        st.error("No Game with that id exists, going back to main menu...")
                        time.sleep(1)
                        st.session_state.nextpage = "main_page"
                        st.experimental_rerun()
                    if (game["game_mode"] == "GYMKHANA"):
                        st.session_state.nextpage = "racedisplay"
                    elif (game["game_mode"] == "GYMKHANA_TRAINING"):
                        st.session_state.nextpage = "gymkhana_training_racedisplay"
                else:
                    st.session_state.nextpage = "main_page"
                highscoreboard.empty()
                placeholder1.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col2:
            if st.button(f"Remove Player {st.session_state.remove_emoji}"):
                st.session_state.nextpage = "remove_player_from_highscore_list"
                highscoreboard.empty()
                placeholder1.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col3:
            if st.button(f"Clear List {st.session_state.delete_emoji}"):
                result = fetch_delete(f"{settings.driftapi_path}/driftapi/game/{lobby_id}/reset/highscores")
                highscoreboard.empty()
                placeholder1.empty()
                time.sleep(0.1)
                st.experimental_rerun()
 
    while True:

        with highscoreboard.container():

            # CSS to inject contained in a string
            hide_dataframe_row_index = """
                        <style>
                        .row_heading.level0 {display:none}
                        .blank {display:none}
                        </style>
            """
            # Inject CSS with Markdown
            st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

            highscoreboard_data = getHighScoreBoard(lobby_id)

            def constructEntry(r:dict):

                if((("engine_type" in r) and (r["engine_type"] is not None)) and (("tuning_type" in r) and (r["tuning_type"] is not None))):
                    model = get_model(r["engine_type"],r["tuning_type"])
                else:
                    model = "-"
                    
                if(("tuning_type" in r) and (r["tuning_type"] is not None)):
                    tuning = get_tuning(r["tuning_type"])
                else:
                    tuning = "-"
                    
                if(("setup_mode" in r) and (r["setup_mode"] is not None)):  
                    setup = get_setup(r["setup_mode"])
                else:
                    setup = "-"
                    
                if(("softsteering" in r) and (r["softsteering"] is not None)):
                    soft_s = get_bool(r["softsteering"])
                else:
                    soft_s = "-"
                    
                if(("driftassist" in r) and (r["driftassist"] is not None)):
                    drift_a = get_bool(r["driftassist"])
                else:
                    drift_a = "-"
                    
                if(("wheels" in r) and (r["wheels"] is not None)):
                    wheels = get_wheels(r["wheels"])
                else:
                    wheels = "-"

                d = {
                    "DRIVER":r["user_name"] if "user_name" in r else "",
                    "POINTS":r["high_score"] if "high_score" in r else "-",
                    "MODEL":str(model),
                    "TUNING":str(tuning),
                    "SETUP":str(setup),
                    "S.-ANGLE":int(r["steering_angle"]) if "steering_angle" in r else "-",
                    "SOFT-S.":str(soft_s),
                    "DRIFT-A.":str(drift_a),
                    "WHEELS":str(wheels),
                    
                }

                if "track_condition" in r:
                    if( (r["track_condition"] == "drift_asphalt" ) ):
                        d["TRACK"] = f"{st.session_state.track_dry_emoji}"
                    elif( (r["track_condition"] == "drift_asphalt_wet" ) ):
                        d["TRACK"] = f"{st.session_state.track_wet_emoji}"
                    elif( (r["track_condition"] ==  "drift_dirt") ):
                        d["TRACK"] = f"{st.session_state.track_gravel_emoji}"
                    elif( (r["track_condition"] == "drift_ice" ) ):
                        d["TRACK"] = f"{st.session_state.track_snow_emoji}"
                    else:
                        d["TRACK"] = f"{st.session_state.track_unknown_emoji}"
                else:
                    d["TRACK"] = "-"

                if "high_score_timestamp" in r:
                    time1 = datetime.now(tz=ZoneInfo("Europe/Berlin"))
                    timedelta_1 = time1.utcoffset()
                    correct_time = datetime.strptime(r["high_score_timestamp"], '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(timezone.utc)+timedelta_1
                    d["DATE"] = correct_time.strftime("%d.%m.%Y, %H:%M:%S")
                else:
                    d["DATE"] = "-"

                return (d)

            if(len(highscoreboard_data) > 0):
                (highscoreboard_data) = [constructEntry(r) for r in highscoreboard_data if (type(r) is dict)]

            #if there is no entry, just add an empty one by calling the construct Entry with an empty dict
            while len(highscoreboard_data)<1:
                highscoreboard_data.append(constructEntry({}))

            highscoreboard_data = (sorted(highscoreboard_data, key=operator.itemgetter('POINTS'), reverse=True))
            df = pd.DataFrame( highscoreboard_data ) 
            df = df.style.set_properties(**{
                'font-size': '25pt',
                'font-family': 'IBM Plex Mono',
            })

#            st.dataframe(df)
            st.table(df)
            
            time.sleep(2)

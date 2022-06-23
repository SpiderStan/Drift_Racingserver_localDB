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

from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger

def getHighScoreBoard(lobby_id):
    return fetch_get(f"{settings.driftapi_path}/driftapi/game/{lobby_id}/highscores")

def app():   

    lobby_id = st.session_state.lobby_id        
    
    st.header("Gymkhana High Score List of Lobby " + str(lobby_id))

    highscoreboard = st.empty()

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(f"Back {st.session_state.back_emoji}"):
            if 'game_id' in st.session_state:
                st.session_state.nextpage = "racedisplay"
            else:
                st.session_state.nextpage = "main_page"
            st.experimental_rerun()

    with col2:
        if st.button(f"Remove Player {st.session_state.remove_emoji}"):
            st.session_state.nextpage = "remove_player_from_highscore_list"
            st.experimental_rerun()

    with col3:
        if st.button(f"Clear List {st.session_state.delete_emoji}"):
            result = fetch_delete(f"{settings.driftapi_path}/driftapi/game/{lobby_id}/reset/highscores")
            st.experimental_rerun()
 
    while True:

        with highscoreboard.container():

            highscoreboard_data = getHighScoreBoard(lobby_id)

            def constructEntry(r:dict):
            
                d = {
                    "Fahrer":r["user_name"] if "user_name" in r else "",
                    "Punkte":r["high_score"] if "high_score" in r else "-",
                    "Motor":r["engine_type"] if "engine_type" in r else "-",
                    "Tuning":r["tuning_type"] if "tuning_type" in r else "-",
                    "LW":r["steering_angle"] if "steering_angle" in r else "-",
                    "DA":r["driftassist"] if "driftassist" in r else "-",
                    "ST":r["softsteering"] if "softsteering" in r else "-",
                    "Setup":r["setup_mode"] if "setup_mode" in r else "-",
                }
                
                if "wheels" in r:
                    if( (r["wheels"] == "normal" ) ):
                        d["Reifen"] = "Straße"
                    elif( (r["wheels"] == "spikes" ) ):
                        d["Reifen"] = "Spikes"
                    elif( (r["wheels"] == "gravel_tires" ) ):
                        d["Reifen"] = "Rally"
                    else:
                        d["Reifen"] = "-"
                else:
                    d["Reifen"] = "-"

                if "track_condition" in r:
                    if( (r["track_condition"] == "drift_asphalt" ) ):
                        d["Strecke"] = f"{st.session_state.track_dry_emoji}"
                    elif( (r["track_condition"] == "drift_asphalt_wet" ) ):
                        d["Strecke"] = f"{st.session_state.track_wet_emoji}"
                    elif( (r["track_condition"] ==  "drift_dirt") ):
                        d["Strecke"] = f"{st.session_state.track_gravel_emoji}"
                    elif( (r["track_condition"] == "drift_ice" ) ):
                        d["Strecke"] = f"{st.session_state.track_snow_emoji}"
                    else:
                        d["Strecke"] = f"{st.session_state.track_unknown_emoji}"
                else:
                    d["Strecke"] = "-"

                if "high_score_timestamp" in r:
                    time1 = datetime.now(tz=ZoneInfo("Europe/Berlin"))
                    timedelta_1 = time1.utcoffset()
                    correct_time = datetime.strptime(r["high_score_timestamp"], '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(timezone.utc)+timedelta_1
                    d["Datum"] = correct_time.strftime("%d/%m/%Y, %H:%M:%S")
                else:
                    d["Datum"] = "-"

                return (d)

            (highscoreboard_data) = [constructEntry(r) for r in highscoreboard_data if (type(r) is dict)]

            #if there is no entry, just add an empty one by calling the construct Entry with an empty dict
            while len(highscoreboard_data)<1:
                highscoreboard_data.append(constructEntry({}))

            highscoreboard_data = (sorted(highscoreboard_data, key=operator.itemgetter('Punkte'), reverse=True))
            df = pd.DataFrame( highscoreboard_data ) 
            st.dataframe(df)

            time.sleep(2)

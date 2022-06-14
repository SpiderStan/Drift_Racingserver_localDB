import streamlit as st
import time
from datetime import timedelta
import pandas as pd 
import numpy as np
from PIL import Image
from math import floor

from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger

# TBD: fix - get info of all game stages!

def getGameInfo(lobby_id, game_id, stage_id):
    return fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/get/{lobby_id}/{game_id}/{stage_id}/")

def getScoreBoard(lobby_id, game_id, stage_id):
    return fetch_get(f"{settings.driftapi_path}/driftapi/game/{lobby_id}/{game_id}/{stage_id}/playerstatus")

def app():

    lobby_id = st.session_state.lobby_id
    game_id = st.session_state.game_id
    stage_id = st.session_state.stage_id
    num_stages = st.session_state.num_stages

    st.write("Download Game Data of Game " + str(game_id) + " Stage " + str(stage_id) + " from Lobby " + str(lobby_id))

    if st.button(f"Back to Race {st.session_state.back_emoji}"):
        st.session_state.nextpage = "racedisplay"
        st.experimental_rerun()

    game = getGameInfo(lobby_id, game_id, stage_id)

    if not game:
        st.error("No Game with that id exists, going back to main menu...")
        time.sleep(1)
        st.session_state.nextpage = "main_page"
        st.experimental_rerun()

    joker_lap_code = None
    if game:
        if "joker_lap_code" in game:
            joker_lap_code = game["joker_lap_code"]

            scoreboard_data = getScoreBoard(lobby_id, game_id, stage_id)

            def showTime(s):
                if ((s is None) or s==''):
                    return ''
                s = float(s)
                ms = floor((s % 1)*1000)
                s = floor(s)
                m = floor(s / 60)
                s = s -60*m
                return f"{m:02d}:{s:02d}:{ms:03d}"
                #return round(float(s),2) if not((s is None) or s== '') else None

            def constructEntry(r:dict):
                d = {
                    "Spieler":r["user_name"] if "user_name" in r else "",
                    "Motor":r["enter_data"]["engine_type"] if "enter_data" in r else "-",
                    "Tuning":r["enter_data"]["tuning_type"] if "enter_data" in r else "-",
                    "Setup":r["enter_data"]["setup_mode"] if "enter_data" in r else "-",
                    "Strecke":r["enter_data"]["track_condition"] if "enter_data" in r else "-",
                    "Reifen":r["enter_data"]["wheels"] if "enter_data" in r else "-",
                    "Modus":r["enter_data"]["game_mode"] if "enter_data" in r else "-",
                    "Kursmodus":r["enter_data"]["track_bundle"] if "enter_data" in r else "-",
                    "Runden":r["enter_data"]["lap_count"] if "enter_data" in r else 0, 
                    "Aktuelle Runde":r["laps_completed"] if "laps_completed" in r else 0,
                    "Beste":showTime(r["best_lap"]) if "best_lap" in r else showTime(None),
                    "Letzte":showTime(r["last_lap"]) if "last_lap" in r else showTime(None),
                    "Punkte":r["total_score"] if ("total_score" in r) and (not (r["total_score"] is None)) else 0,
                    "Gesamtzeit":showTime(r["total_time"]) if "total_time" in r else showTime(None),
                }

                if joker_lap_code != None:
                    d["Joker"] = int(r["joker_laps_counter"]) if "joker_laps_counter" in r else 0

                if "end_data" in r:
                    d = {**d, **r["enter_data"], **r["start_data"], **r["end_data"]}
                    

                return d

            scoreboard_data = [constructEntry(r) for r in scoreboard_data if (type(r) is dict)]

            while len(scoreboard_data)<1:
                scoreboard_data.append(constructEntry({}))

            df = pd.DataFrame( scoreboard_data )

            st.download_button(
                f"Press to Download as csv {st.session_state.download_emoji}",
                df.to_csv(index = False),
                game_id+".csv",
                "text/csv",
                key='download-csv'
            )
            '''
            st.download_button(
                f"Press to Download as html {st.session_state.download_emoji}",
                df.to_html(),
                game_id+".html",
                "text/html",
                key='download-html'
            )
            '''

            st.download_button(
                f"Press to Download as json {st.session_state.download_emoji}",
                df.to_json(orient='records'),
                game_id+".json",
                "text/json",
                key='download-json'
            )





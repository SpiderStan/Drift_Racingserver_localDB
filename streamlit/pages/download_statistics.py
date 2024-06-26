import streamlit as st
import time
#import socket
from datetime import timedelta, timezone, datetime
import pandas as pd 
import numpy as np
import qrcode
import operator
from PIL import Image
from math import floor

from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger
from .helper import get_model, get_tuning, get_app_game_mode, get_starttime, get_track_cond, get_track_bundle, get_wheels, get_setup, get_joker_lap_code, get_bool, handleCurrentTrackCondition, getGameInfo, getScoreBoard, getDetailedTargetData, showTime, showDistance, showMeanSpeed

def app():

    lobby_id = st.session_state.lobby_id        
    game_id = st.session_state.game_id
    stage_id = st.session_state.stage_id
    num_stages = st.session_state.num_stages

    game_track_images_set = st.session_state.game_track_images_set
    game_track_images = st.session_state.game_track_images
    
    st.subheader("Download detailed Game Statistics of Game " + str(game_id) + " Stage " + str(stage_id) + " from Lobby " + str(lobby_id))

    placeholder1 = st.empty()
    placeholder2 = st.empty()

    game = getGameInfo(lobby_id, game_id, stage_id)
    if not game:
        st.error("No Game with that id exists, going back to main menu...")
        time.sleep(1)
        st.session_state.nextpage = "main_page"
        st.experimental_rerun()

    with placeholder1.container():
        if st.button(f"Back {st.session_state.back_emoji}"):
            st.session_state.num_stages = game["num_stages"]
            st.session_state.nextpage = "statistics"
            st.session_state.game_track_images_set = game_track_images_set
            st.session_state.game_track_images = game_track_images
            placeholder1.empty()
            placeholder2.empty()
            time.sleep(0.1)
            st.experimental_rerun()

    with placeholder2.container():

        def constructEntry(r:dict,last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time, section_condition, user_name, sum_score):

            d = { } # new dict

            next_section_condition = section_condition

            if ( game["game_mode"] == "RACE" ):
                if "target_data" in r:
                    if(str(game["track_bundle"]) == "rally"):
                        if(r["target_data"]["target_code"] == 4):
                            next_section_condition = f" {st.session_state.track_dry_emoji}"
                        elif(r["target_data"]["target_code"] == 5):
                            next_section_condition = f" {st.session_state.track_wet_emoji}"
                        elif(r["target_data"]["target_code"] == 6):
                            next_section_condition = f" {st.session_state.track_gravel_emoji}"
                        elif(r["target_data"]["target_code"] == 7):
                            next_section_condition = f" {st.session_state.track_snow_emoji}"
                        section_distance = r["target_data"]["driven_distance"] - last_driven_distance
                        section_time = r["target_data"]["driven_time"] - last_driven_time
                        if(section_time != 0): # normal case
                            d[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = showDistance(section_distance)
                            d[f"SECTOR - {st.session_state.time_emoji}"] = showTime(section_time)
                            d[f"SECTOR - {st.session_state.average_speed_emoji}"] = f"Ø " + showMeanSpeed(section_distance,section_time)
                            d[f"SECTOR - {st.session_state.track_emoji}"] = section_condition
                        else: # this occurs if after finish further targets will be crossed
                            d[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d[f"SECTOR - {st.session_state.time_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d[f"SECTOR - {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d[f"SECTOR - {st.session_state.track_emoji}"] = f"{st.session_state.false_start_emoji}"
                        last_driven_distance = r["target_data"]["driven_distance"]
                        last_driven_time = r["target_data"]["driven_time"]      
                    elif(str(game["track_bundle"]) == "rally_cross"):
                        if(r["target_data"]["target_code"] == 0):
                            next_section_condition = section_condition
                        if(r["target_data"]["target_code"] == 4):
                            next_section_condition = f" {st.session_state.track_dry_emoji}"
                        elif(r["target_data"]["target_code"] == 5):
                            next_section_condition = f" {st.session_state.track_wet_emoji}"
                        elif(r["target_data"]["target_code"] == 6):
                            next_section_condition = f" {st.session_state.track_gravel_emoji}"
                        elif(r["target_data"]["target_code"] == 7):
                            next_section_condition = section_condition
                            section_condition = next_section_condition + f" {st.session_state.track_gravel_trap_emoji}"
                        section_distance = r["target_data"]["driven_distance"] - last_driven_distance
                        section_time = r["target_data"]["driven_time"] - last_driven_time
                        if(section_time != 0): # normal case
                            d[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = showDistance(section_distance)
                            d[f"SECTOR - {st.session_state.time_emoji}"] = showTime(section_time)
                            d[f"SECTOR - {st.session_state.average_speed_emoji}"] = f"Ø " + showMeanSpeed(section_distance,section_time)
                            d[f"SECTOR - {st.session_state.track_emoji}"] = section_condition
                        else: # this occurs if after finish further targets will be crossed
                            d[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d[f"SECTOR - {st.session_state.time_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d[f"SECTOR - {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d[f"SECTOR - {st.session_state.track_emoji}"] = f"{st.session_state.false_start_emoji}"
                        last_driven_distance = r["target_data"]["driven_distance"]
                        last_driven_time = r["target_data"]["driven_time"]
                    else:
                        section_distance = r["target_data"]["driven_distance"] - last_driven_distance
                        section_time = r["target_data"]["driven_time"] - last_driven_time
                        if(section_time != 0): # normal case
                            d[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = showDistance(section_distance)
                            d[f"SECTOR - {st.session_state.time_emoji}"] = showTime(section_time)
                            d[f"SECTOR - {st.session_state.average_speed_emoji}"] = f"Ø " + showMeanSpeed(section_distance,section_time)
                            d[f"SECTOR - {st.session_state.track_emoji}"] = section_condition
                        else: # this occurs if after finish further targets will be crossed
                            d[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d[f"SECTOR - {st.session_state.time_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d[f"SECTOR - {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d[f"SECTOR - {st.session_state.track_emoji}"] = f"{st.session_state.false_start_emoji}"
                        last_driven_distance = r["target_data"]["driven_distance"]
                        last_driven_time = r["target_data"]["driven_time"]  

                    if(r["target_data"]["target_code"] == 0):
                        round_distance = r["target_data"]["driven_distance"] - last_round_driven_distance
                        round_time = r["target_data"]["driven_time"] - last_round_driven_time
                        d[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = showDistance(round_distance) + f" {st.session_state.round_emoji}"
                        d[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = showTime(round_time) + f" {st.session_state.round_emoji}"
                        d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(round_distance,round_time) + f" {st.session_state.round_emoji}"
                        last_round_driven_distance = r["target_data"]["driven_distance"]
                        last_round_driven_time = r["target_data"]["driven_time"]
                    else:
                        d[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = showDistance(r["target_data"]["driven_distance"] - last_round_driven_distance)
                        d[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = showTime(r["target_data"]["driven_time"] - last_round_driven_time)
                        d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(r["target_data"]["driven_distance"] - last_round_driven_distance,r["target_data"]["driven_time"] - last_round_driven_time)
                                
            elif ( game["game_mode"] == "GYMKHANA" ):
                if "target_data" in r:
                    if(r["target_data"]["target_code"] == 4):
                        gymkhana_target = "Speed Drift"
                    elif(r["target_data"]["target_code"] == 5):
                        gymkhana_target = "Angle Drift"
                    elif(r["target_data"]["target_code"] == 6):
                        gymkhana_target = "180° Speed"
                    elif(r["target_data"]["target_code"] == 7):
                        gymkhana_target = "360° Angle"
                    else:
                        gymkhana_target = "Finish"

                    section_distance = r["target_data"]["driven_distance"] - last_round_driven_distance
                    section_time = r["target_data"]["driven_time"] - last_round_driven_time
                    sum_score = sum_score + r["target_data"]["score"]
                    d[str(scoreboard_data[player]["user_name"]) + f" {st.session_state.target_emoji}"] = gymkhana_target
                    d[f"{st.session_state.points_emoji}"] = str(r["target_data"]["score"])
                    d[f" ∑ {st.session_state.points_emoji}"] = sum_score
                    d[f"{st.session_state.distance_emoji}"] = showDistance(section_distance)
                    d[f"{st.session_state.time_emoji}"] = showTime(section_time)
                    d[f"Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(section_distance,section_time)
                    d[f" ∑ {st.session_state.distance2_emoji}"] = showDistance(r["target_data"]["driven_distance"])
                    d[f" ∑ {st.session_state.time2_emoji}"] = showTime(r["target_data"]["driven_time"])
                    d[f"CUM. Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(r["target_data"]["driven_distance"],r["target_data"]["driven_time"])
                    last_round_driven_distance = r["target_data"]["driven_distance"]
                    last_round_driven_time = r["target_data"]["driven_time"]

            return (d,last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,next_section_condition,sum_score)

        scoreboard_data = getScoreBoard(lobby_id, game_id, stage_id)
        num_players = len(scoreboard_data)
                
        for player in range(num_players):
            targetboard_data = getDetailedTargetData(lobby_id, game_id, stage_id, scoreboard_data[player]["user_name"])
    #        targetboard_data = (sorted(targetboard_data, key=operator.itemgetter('target_ctr')))
            targetboard_data_len = len(targetboard_data)            
                   
            last_driven_distance = float(0)
            last_driven_time = float(0)
            last_round_driven_distance = float(0)
            last_round_driven_time = float(0)
            sum_score = int(0)
            
            if "enter_data" in scoreboard_data[player]:
                if(scoreboard_data[player]["enter_data"]["track_condition"] == "drift_asphalt"):
                    section_condition = f" {st.session_state.track_dry_emoji}"
                elif(scoreboard_data[player]["enter_data"]["track_condition"] == "drift_asphalt_wet"):
                    section_condition = f" {st.session_state.track_wet_emoji}"
                elif(scoreboard_data[player]["enter_data"]["track_condition"] == "drift_dirt"):
                    section_condition = f" {st.session_state.track_gravel_emoji}"
                elif(scoreboard_data[player]["enter_data"]["track_condition"] == "drift_ice"):
                    section_condition = f" {st.session_state.track_snow_emoji}"
            else:
                section_condition = f" {st.session_state.track_unknown_emoji}"
            for x in range(targetboard_data_len):
                (targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition,sum_score) = constructEntry(targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"],sum_score)
                if ( game["game_mode"] == "RACE" ) and (x == 0):
                    last_driven_distance = float(0)
                    last_driven_time = float(0)
                    last_round_driven_distance = float(0)
                    last_round_driven_time = float(0)

            if( game["game_mode"] == "RACE" ):
                d = {}
                d[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = f"∑ {st.session_state.distance2_emoji} " + showDistance(scoreboard_data[player]["end_data"]["total_driven_distance"])
                d[f"SECTOR - {st.session_state.time_emoji}"] = f"∑ {st.session_state.time2_emoji} " + showTime(scoreboard_data[player]["total_time"])
                d[f"SECTOR - {st.session_state.average_speed_emoji}"] = f"Ø {st.session_state.average_speed_emoji} " + showMeanSpeed(scoreboard_data[player]["end_data"]["total_driven_distance"],scoreboard_data[player]["total_time"])
                d[f"SECTOR - {st.session_state.track_emoji}"] = ""
                d[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = f"Ø {st.session_state.distance2_emoji} / {st.session_state.round_emoji} " + showDistance(float(float(scoreboard_data[player]["end_data"]["total_driven_distance"])/float(scoreboard_data[player]["laps_completed"]))) 
                d[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = f"Ø {st.session_state.time2_emoji} / {st.session_state.round_emoji} " + showTime(float(float(scoreboard_data[player]["total_time"])/float(scoreboard_data[player]["laps_completed"])))
                d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = ""
                targetboard_data.append(d)

            #if there is no entry, just add an empty one by calling the construct Entry with an empty dict
            while len(targetboard_data)<1:
                targetboard_data.append(constructEntry({}))

            df = pd.DataFrame( targetboard_data ) 

            col11, col12 = st.columns(2)
            
            with col11:
                st.download_button(
                    f"Download Stats of " + str(scoreboard_data[player]["user_name"]) + f" as csv {st.session_state.download_emoji}",
                    df.to_csv(index = False).encode('utf-8'),
                    "Stats_" + str(lobby_id) + "_" + str(game_id) + "_" + str(stage_id) + "_" + str(scoreboard_data[player]["user_name"])+".csv",
                    "text/csv",
                    key='download-csv'
                )

            with col12:
                st.download_button(
                    f"Download Stats of " + str(scoreboard_data[player]["user_name"]) + f"  as json {st.session_state.download_emoji}",
                    df.to_json(orient='records'),
                    "Stats_" + str(lobby_id) + "_" + str(game_id) + "_" + str(stage_id) + "_" + str(scoreboard_data[player]["user_name"])+".json",
                    "text/json",
                    key='download-json'
                )










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

from .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger
from .helper import get_game_mode, get_starttime, get_track_cond, get_track_bundle, get_wheels, get_setup, get_bool, get_model, get_tuning

def getGameInfo(lobby_id, game_id, stage_id):
    return fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/get/{lobby_id}/{game_id}/{stage_id}/")

def getScoreBoard(lobby_id, game_id, stage_id):
    return fetch_get(f"{settings.driftapi_path}/driftapi/game/{lobby_id}/{game_id}/{stage_id}/playerstatus")

def getDetailedTargetData(lobby_id, game_id, stage_id, user_name):
    return fetch_get(f"{settings.driftapi_path}/driftapi/game/{lobby_id}/{game_id}/{stage_id}/{user_name}/targetstatus")

def showTime(s):
    if ((s is None) or s==''):
        return ''
    s = float(s)
    ms = floor((s % 1)*1000)
    s = floor(s)
    m = floor(s / 60)
    s = s -60*m
    return f"{m:02d}:{s:02d}.{ms:03d}"
    #return round(float(s),2) if not((s is None) or s== '') else None

def showDistance(s):
    if ((s is None) or s==''):
        return ''
    s = float(s)
    cm = floor((s % 1)*100)
    m = floor(s)
    km = floor(s / 1000)
    m = m - 1000*km
    return f"{km:01d}km {m:03d}m {cm:02d}cm"
    
def showMeanSpeed(d,t):
    if ((d is None) or d==''):
        return ''
    if ((t is None) or t==''):
        return ''
    d = float(d)
    t = float(t)
    kmh = d/t*3.6
    return f"{kmh:03.2f}km/h"

def app():   

    lobby_id = st.session_state.lobby_id        
    game_id = st.session_state.game_id
    stage_id = st.session_state.stage_id
    num_stages = st.session_state.num_stages

    game_track_images_set = st.session_state.game_track_images_set
    game_track_images = st.session_state.game_track_images
    
    st.subheader("Detailed Game Statistics of Game " + str(game_id) + " Stage " + str(stage_id) + " from Lobby " + str(lobby_id))

    game = getGameInfo(lobby_id, game_id, stage_id)

    if not game:
        st.error("No Game with that id exists, going back to main menu...")
        time.sleep(1)
        st.session_state.nextpage = "main_page"
        st.experimental_rerun()

    placeholder1 = st.empty()
    targetboard = st.empty()

    with placeholder1.container(): 
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

        with col1:
            if st.button(f"Back {st.session_state.back_emoji}"):
                if(game["num_stages"] == 1):
                    st.session_state.num_stages = 1
                    st.session_state.nextpage = "racedisplay"
                else:
                    st.session_state.num_stages = game["num_stages"]
                    st.session_state.nextpage = "stage_racedisplay"
                st.session_state.game_track_images_set = game_track_images_set
                st.session_state.game_track_images = game_track_images
                placeholder1.empty()
                targetboard.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col2:
            if st.button(f"Download Statistics {st.session_state.download_emoji}"):
                st.session_state.nextpage = "download_statistics"
                st.session_state.game_track_images_set = game_track_images_set
                st.session_state.game_track_images = game_track_images
                placeholder1.empty()
                targetboard.empty()
                time.sleep(0.1)
                st.experimental_rerun()
 
    while True:

        with targetboard.container():

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
                                d[f"SECTOR - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(section_distance,section_time)
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
                            elif(r["target_data"]["target_code"] == 4):
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
                                d[f"SECTOR - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(section_distance,section_time)
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
                                d[f"SECTOR - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(section_distance,section_time)
                                d[f"SECTOR - {st.session_state.track_emoji}"] = section_condition
                            else: # this occurs if after finish further targets will be crossed
                                d[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = f"{st.session_state.false_start_emoji}"
                                d[f"SECTOR - {st.session_state.time_emoji}"] = f"{st.session_state.false_start_emoji}"
                                d[f"SECTOR - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                                d[f"SECTOR - {st.session_state.track_emoji}"] = f"{st.session_state.false_start_emoji}"
                            last_driven_distance = r["target_data"]["driven_distance"]
                            last_driven_time = r["target_data"]["driven_time"]  

                        if(r["target_data"]["target_code"] == 0):
                            if(section_time != 0): # normal case
                                round_distance = r["target_data"]["driven_distance"] - last_round_driven_distance
                                round_time = r["target_data"]["driven_time"] - last_round_driven_time
                                d[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = showDistance(round_distance) + f" {st.session_state.round_emoji}"
                                d[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = showTime(round_time) + f" {st.session_state.round_emoji}"
                                d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(round_distance,round_time) + f" {st.session_state.round_emoji}"
                                last_round_driven_distance = r["target_data"]["driven_distance"]
                                last_round_driven_time = r["target_data"]["driven_time"]
                            else:
                                d[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = f"{st.session_state.false_start_emoji}"
                                d[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = f"{st.session_state.false_start_emoji}"
                                d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                        else:
                            if(section_time != 0): # normal case
                                d[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = showDistance(r["target_data"]["driven_distance"] - last_round_driven_distance)
                                d[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = showTime(r["target_data"]["driven_time"] - last_round_driven_time)
                                d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(r["target_data"]["driven_distance"] - last_round_driven_distance,r["target_data"]["driven_time"] - last_round_driven_time)
                            else:
                                d[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = f"{st.session_state.false_start_emoji}"
                                d[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = f"{st.session_state.false_start_emoji}"
                                d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                                
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
#                targetboard_data = (sorted(targetboard_data, key=operator.itemgetter('target_ctr')))
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

                if ( ( "end_data" in scoreboard_data[player] ) and not ( scoreboard_data[player]["end_data"] is None ) ):
                    if( game["game_mode"] == "RACE" ):
                        d = {}
                        d[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = f"∑ {st.session_state.distance2_emoji} " + showDistance(scoreboard_data[player]["end_data"]["total_driven_distance"])
                        d[f"SECTOR - {st.session_state.time_emoji}"] = f"∑ {st.session_state.time2_emoji} " + showTime(scoreboard_data[player]["total_time"])
                        d[f"SECTOR - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.average_speed_emoji} " + showMeanSpeed(scoreboard_data[player]["end_data"]["total_driven_distance"],scoreboard_data[player]["total_time"])
                        d[f"SECTOR - {st.session_state.track_emoji}"] = ""
                        if(scoreboard_data[player]["laps_completed"] != 0):
                            d[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = f"Ø {st.session_state.distance2_emoji} / {st.session_state.round_emoji} " + showDistance(float(float(scoreboard_data[player]["end_data"]["total_driven_distance"])/float(scoreboard_data[player]["laps_completed"]))) 
                            d[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = f"Ø {st.session_state.time2_emoji} / {st.session_state.round_emoji} " + showTime(float(float(scoreboard_data[player]["total_time"])/float(scoreboard_data[player]["laps_completed"])))
                        else:
                            d[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = ""
                            d[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = ""
                        d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = ""
                        targetboard_data.append(d)
                        
                #if there is no entry, just add an empty one by calling the construct Entry with an empty dict
                while len(targetboard_data)<1:
                    targetboard_data.append(constructEntry({},last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"], sum_score)[0])

                df = pd.DataFrame( targetboard_data ) 
#                st.text("Detailed Statistics of " + str(scoreboard_data[player]["user_name"]))

                model = get_model(scoreboard_data[player]["enter_data"]["engine_type"],scoreboard_data[player]["enter_data"]["tuning_type"])
                tuning = get_tuning(scoreboard_data[player]["enter_data"]["tuning_type"])
                with st.expander("Detailed Statistics of " + str(scoreboard_data[player]["user_name"]) + " (" + str(model) + " | " + str(tuning) + f") {st.session_state.show_game_emoji}", expanded=False):
                    st.dataframe(df)

            time.sleep(0.5)
            

import streamlit as st
import os
from os.path import exists
import time
#import socket
from zoneinfo import ZoneInfo #to set the timezone to german time
from datetime import timedelta, timezone, datetime
import pandas as pd 
import numpy as np
import qrcode
from PIL import Image
from math import floor

from .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger

import base64
import shutil

@st.cache
def getqrcode(content):
    logger.info("create qr code")
    logger.info(content)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="white", back_color="#212529")
    logger.info(str(img))
    img.save('./qrcode_test.png')
    return Image.open('./qrcode_test.png')

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
    return f"{m:02d}m {s:02d}s {ms:03d}ms"
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

def decode_targets(gymkhana_training_targets):
    if (gymkhana_training_targets == "ANGLE -> 180° -> SPEED -> 360°"):
        t_list = [5,6,4,7]
    elif (gymkhana_training_targets == "ANGLE -> 180° -> 360° -> SPEED"):
        t_list = [5,6,7,4]
    elif (gymkhana_training_targets == "ANGLE -> SPEED -> 180° -> 360°"):
        t_list = [5,4,6,7]
    elif (gymkhana_training_targets == "ANGLE -> SPEED -> 360° -> 180°"):
        t_list = [5,4,7,6]
    elif (gymkhana_training_targets == "ANGLE -> 360° -> SPEED -> 180°"):
        t_list = [5,7,4,6]
    elif (gymkhana_training_targets == "ANGLE -> 360° -> 180° -> SPEED"):
        t_list = [5,7,6,4]
    elif (gymkhana_training_targets == "SPEED -> 180° -> ANGLE -> 360°"):
        t_list = [4,6,5,7]
    elif (gymkhana_training_targets == "SPEED -> 180° -> 360° -> ANGLE"):
        t_list = [4,6,7,5]
    elif (gymkhana_training_targets == "SPEED -> ANGLE -> 180° -> 360°"):
        t_list = [4,5,6,7]
    elif (gymkhana_training_targets == "SPEED -> ANGLE -> 360° -> 180°"):
        t_list = [4,5,7,6]
    elif (gymkhana_training_targets == "SPEED -> 360° -> ANGLE -> 180°"):
        t_list = [4,7,5,6]
    elif (gymkhana_training_targets == "SPEED -> 360° -> 180° -> ANGLE"):
        t_list = [4,7,6,5]
    elif (gymkhana_training_targets == "180° -> ANGLE -> 360° -> SPEED"):
        t_list = [6,5,7,4]
    elif (gymkhana_training_targets == "180° -> ANGLE -> SPEED -> 360°"):
        t_list = [6,5,4,7]
    elif (gymkhana_training_targets == "180° -> 360° -> ANGLE -> SPEED"):
        t_list = [6,7,5,4]
    elif (gymkhana_training_targets == "180° -> 360° -> SPEED -> ANGLE"):
        t_list = [6,7,4,5]
    elif (gymkhana_training_targets == "180° -> SPEED -> ANGLE -> 360°"):
        t_list = [6,4,5,7]
    elif (gymkhana_training_targets == "180° -> SPEED -> 360° -> ANGLE"):
        t_list = [6,4,7,5]
    elif (gymkhana_training_targets == "360° -> ANGLE -> 180° -> SPEED"):
        t_list = [7,5,6,4]
    elif (gymkhana_training_targets == "360° -> ANGLE -> SPEED -> 180°"):
        t_list = [7,5,4,6]
    elif (gymkhana_training_targets == "360° -> 180° -> ANGLE -> SPEED"):
        t_list = [7,6,5,4]
    elif (gymkhana_training_targets == "360° -> 180° -> SPEED -> ANGLE"):
        t_list = [7,6,4,5]
    elif (gymkhana_training_targets == "360° -> SPEED -> 180° -> ANGLE"):
        t_list = [7,4,6,5]
    elif (gymkhana_training_targets == "360° -> SPEED -> ANGLE -> 180°"):
        t_list = [7,4,5,6]
    return t_list

# added function to handle awards after the race (Race: 1st, 2nd, 3rd and bonus award for fastest lap)
def get_minvalue(inputlist):
    #get the minimum value in the list
    min_value = min(inputlist)
    #return the index of minimum value 
    res = [i for i,val in enumerate(inputlist) if val==min_value]
    return res

# added function to handle awards after the gymkhana (Race: 1st, 2nd, 3rd and bonus award for highest bonus target)
def get_maxvalue(inputlist):
    #get the maximum value in the list
    max_value = max(inputlist)
    if max_value == 0:
        res = []
        return res
    #return the index of maximum value 
    res = [i for i,val in enumerate(inputlist) if val==max_value]
    return res

def app():   

    lobby_id = st.session_state.lobby_id        
    game_id = st.session_state.game_id
    stage_id = st.session_state.stage_id
    num_stages = st.session_state.num_stages

    game_track_images_set = st.session_state.game_track_images_set
    game_track_images = st.session_state.game_track_images

    game = getGameInfo(lobby_id, game_id, stage_id)

    if not game:
        st.error("No Game with that id exists, going back to main menu...")
        time.sleep(1)
        st.session_state.nextpage = "main_page"
        st.experimental_rerun()

    st.header("Statistics of Gymkhana Training (" + str(game["gymkhana_training_targets"]) + ") " + str(game_id) + " from Lobby " + str(lobby_id))
    
    os.makedirs("gymkhana_training/" + str(lobby_id) + "/" + str(game_id) + "/runs/", exist_ok=True)
    dir_name = "gymkhana_training/" + str(lobby_id) + "/" + str(game_id) + "/runs/"
    output_filename = "Gymkhana_Training_" + str(lobby_id) + "_" + str(game_id)
    zip_path = "gymkhana_training/" + str(lobby_id) + "/" + str(game_id) + "/"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button(f"Back {st.session_state.back_emoji}"):
            st.session_state.num_stages = 1
            st.session_state.nextpage = "main_page"
            st.experimental_rerun()

    with col2:
        if len(os.listdir(str(dir_name))) != 0:
            with open(str(zip_path) + str(output_filename) + ".zip", 'rb') as fp:
                btn = st.download_button(
                    label=f"Download Saved Runs as zip {st.session_state.download_emoji}",
                    data=fp,
                    file_name=output_filename  + ".zip",
                    mime="application/zip"
                )

    with col3:
        if len(os.listdir(str(dir_name))) != 0:
            if st.button(f"Delete Saved Runs {st.session_state.delete_emoji}"):
                for f in os.listdir(dir_name):
                    os.remove(os.path.join(dir_name, f))
                if os.path.exists(str(zip_path) + str(output_filename) + ".zip"):
                    os.remove(str(zip_path) + str(output_filename) + ".zip")                    
                st.experimental_rerun()

    with col4:
        if st.button(f"Delete Game {st.session_state.delete_emoji}"):
            if len(os.listdir(str(dir_name))) != 0:
                for f in os.listdir(dir_name):
                    os.remove(os.path.join(dir_name, f))
                if os.path.exists(str(zip_path) + str(output_filename) + ".zip"):
                    os.remove(str(zip_path) + str(output_filename) + ".zip")
            result = fetch_delete(f"{settings.driftapi_path}/driftapi/manage_game/delete/{lobby_id}/{game_id}")
            st.session_state.game_id = None
            st.session_state.stage_id = 1
            st.session_state.num_stages = 1
            st.session_state.game_track_images_set = False
            st.session_state.game_track_images = None
            st.session_state.nextpage = "main_page"
            st.experimental_rerun()

    autosave = st.checkbox("AutoSave", value=False, key=None, help="if set, gymkhana runs will be saved", on_change=None)
    
    t_list = decode_targets(game["gymkhana_training_targets"])

#    start_finish = 0 #Gymkhana, Race, Rally, Rally Cross
#    speed_drift = 4 #Gymkhana
#    drift_asphalt = 4 #Rally, Rally Cross
#    angle_drift = 5 #Gymkhana
#    drift_asphalt_wet = 5 #Rally, Rally Cross
#    oneeighty = 6 #Gymkhana
#    drift_dirt = 6 # Rally, Rally Cross
#    threesixty = 7 #Gymkhana
#    drift_ice = 7 # Rally
#    drift_sand = 7 # Rally Cross

    targetboard = st.empty()

    with st.expander(f"Game Settings {st.session_state.show_game_emoji}", expanded = False):
        st.write(game)
        
        track_image = st.empty()
        track_image_upload = st.file_uploader("Here you can upload the track layout", type=['png', 'jpg'], accept_multiple_files=False, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False)

        if(game_track_images_set == False): # no track image upload so far
            if(track_image_upload != None): # user has supplied a track image
                game_track_images_set = True
                track_image = st.image(track_image_upload, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto") # Show Uploaded Track Image
                game_track_images = track_image_upload # store in session state
        elif(game_track_images_set == True): # track image existing
            if(track_image_upload != None): # user has supplied a new track image
                game_track_images_set = True
                track_image = st.image(track_image_upload, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto") # Show Uploaded Track Image
                game_track_images = track_image_upload # store in session state
            else:
                track_image = st.image(game_track_images, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto") # Show Prev. Uploaded Track Image
        if st.button(f"Remove Image {st.session_state.remove_emoji}", key=None):
            track_image.empty()
            game_track_images_set = False

    with st.expander(f"Connection info {st.session_state.show_game_emoji} - Join the game via URL: http://"+str(st.session_state.ip_address)+":8001/driftapi/game/"+str(lobby_id)+"/"+str(stage_id)+" and GAME ID: "+str(game_id), expanded=False):
        submitUri:str = "http://"+str(st.session_state.ip_address)+":8001/driftapi/game/"+str(lobby_id)+"/"+str(stage_id)
        st.image(getqrcode(submitUri), clamp=True)
        st.write("URL: "+submitUri)
        st.write("GAME ID: "+game_id)

    while True:

        with targetboard.container():

            scoreboard_data = getScoreBoard(lobby_id, game_id, stage_id)
            num_players = len(scoreboard_data)
            
            for player in range(num_players):
                targets_data = getDetailedTargetData(lobby_id, game_id, stage_id, scoreboard_data[player]["user_name"])
#                targets_data = (sorted(targets_data, key=operator.itemgetter('target_ctr')))
                targets_data_len = len(targets_data)
                
                targetboard_data = []
               
                last_driven_distance = float(0)
                last_driven_time = float(0)
                last_round_driven_distance = float(0)
                last_round_driven_time = float(0)
                sum_score = int(0)
                last_round_score = int(0)
                t_cnt = int(0)

#                if "enter_data" in scoreboard_data[player]:
#                    if(scoreboard_data[player]["enter_data"]["track_condition"] == "drift_asphalt"):
#                        section_condition = f" {st.session_state.track_dry_emoji}"
#                    elif(scoreboard_data[player]["enter_data"]["track_condition"] == "drift_asphalt_wet"):
#                        section_condition = f" {st.session_state.track_wet_emoji}"
#                    elif(scoreboard_data[player]["enter_data"]["track_condition"] == "drift_dirt"):
#                        section_condition = f" {st.session_state.track_gravel_emoji}"
#                    elif(scoreboard_data[player]["enter_data"]["track_condition"] == "drift_ice"):
#                        section_condition = f" {st.session_state.track_snow_emoji}"
#                else:
#                    section_condition = f" {st.session_state.track_unknown_emoji}"                    
                    
                for x in range(targets_data_len):
                
                    if "target_data" in targets_data[x]:
                        if(targets_data[x]["target_data"]["target_code"] == 4):
                            gymkhana_target = "Speed Drift"
                        elif(targets_data[x]["target_data"]["target_code"] == 5):
                            gymkhana_target = "Angle Drift"
                        elif(targets_data[x]["target_data"]["target_code"] == 6):
                            gymkhana_target = "180° Speed"
                        elif(targets_data[x]["target_data"]["target_code"] == 7):
                            gymkhana_target = "360° Angle"
                        else:
                            gymkhana_target = "Finish"
                
                        if ( targets_data[x]["target_data"]["target_code"] != 0 ): # target is not finish
                            while (targets_data[x]["target_data"]["target_code"] != t_list[t_cnt]): # missed targets
                            
# TDB: what if missed target is last one (round indicator) - how to handle this?
                            
                                d = {}
                                d[str(targets_data[x]["user_name"]) + f" {st.session_state.target_emoji}"] = f"{st.session_state.remove_emoji}"
                                
                                d[f"{st.session_state.points_emoji}"] = f"{st.session_state.remove_emoji}"
                                d[f"∑ {st.session_state.points_emoji}"] = f"{st.session_state.remove_emoji}"

                                d[f"Sektor - {st.session_state.distance_emoji}"] = f"{st.session_state.remove_emoji}"
                                d[f"Sektor - {st.session_state.time_emoji}"] = f"{st.session_state.remove_emoji}"
                                d[f"Sektor - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.remove_emoji}"

                                if(t_cnt == 3): #the fourth (last) target
                                    d[f"∑ Sektoren - {st.session_state.distance2_emoji}"] = f"{st.session_state.remove_emoji} {st.session_state.emoji_round}"
                                    d[f"∑ Sektoren - {st.session_state.time2_emoji}"] = f"{st.session_state.remove_emoji} {st.session_state.emoji_round}"
                                    d[f"Cum. Sektoren - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.remove_emoji} {st.session_state.emoji_round}"
                                    d[f"{st.session_state.emoji_round} {st.session_state.points_emoji}"] = f"- {st.session_state.emoji_round}"
                                else:
                                    d[f"∑ Sektoren - {st.session_state.distance2_emoji}"] = f"{st.session_state.remove_emoji}"
                                    d[f"∑ Sektoren - {st.session_state.time2_emoji}"] = f"{st.session_state.remove_emoji}"
                                    d[f"Cum. Sektoren - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.remove_emoji}"
                                    d[f"{st.session_state.emoji_round} {st.session_state.points_emoji}"] = ""
                                
                                targetboard_data.append(d)

                                t_cnt = (t_cnt + 1) % 4
                            
                            d = {}
                            section_distance = targets_data[x]["target_data"]["driven_distance"] - last_driven_distance
                            section_time = targets_data[x]["target_data"]["driven_time"] - last_driven_time
                            sum_score = sum_score + targets_data[x]["target_data"]["score"]

                            # show target
                            d[str(targets_data[x]["user_name"]) + f" {st.session_state.target_emoji}"] = gymkhana_target

                            # show target score
                            d[f"{st.session_state.points_emoji}"] = str(targets_data[x]["target_data"]["score"])
                            d[f"∑ {st.session_state.points_emoji}"] = str(sum_score)
                            
                            # show distance, time and average speed from target to target
                            d[f"Sektor - {st.session_state.distance_emoji}"] = showDistance(section_distance)
                            d[f"Sektor - {st.session_state.time_emoji}"] = showTime(section_time)
                            d[f"Sektor - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(section_distance,section_time)
                            
                            last_driven_distance = targets_data[x]["target_data"]["driven_distance"]
                            last_driven_time = targets_data[x]["target_data"]["driven_time"]                 
                            
                            # show distance, time and cum. average speed from round to round
                            if(targets_data[x]["target_data"]["target_code"] == t_list[3]): #the fourth (last) target
                                round_distance = targets_data[x]["target_data"]["driven_distance"] - last_round_driven_distance
                                round_time = targets_data[x]["target_data"]["driven_time"] - last_round_driven_time
                                round_score = sum_score - last_round_score
                                d[f"∑ Sektoren - {st.session_state.distance2_emoji}"] = showDistance(round_distance) + f" {st.session_state.emoji_round}"
                                d[f"∑ Sektoren - {st.session_state.time2_emoji}"] = showTime(round_time) + f" {st.session_state.emoji_round}"
                                d[f"Cum. Sektoren - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(round_distance,round_time) + f" {st.session_state.emoji_round}"
                                d[f"{st.session_state.emoji_round} {st.session_state.points_emoji}"] = str(round_score) + f" {st.session_state.emoji_round}"
                                last_round_driven_distance = targets_data[x]["target_data"]["driven_distance"]
                                last_round_driven_time = targets_data[x]["target_data"]["driven_time"]
                                last_round_score = last_round_score + round_score
                            else:
                                d[f"∑ Sektoren - {st.session_state.distance2_emoji}"] = showDistance(targets_data[x]["target_data"]["driven_distance"] - last_round_driven_distance)
                                d[f"∑ Sektoren - {st.session_state.time2_emoji}"] = showTime(targets_data[x]["target_data"]["driven_time"] - last_round_driven_time)
                                d[f"Cum. Sektoren - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(targets_data[x]["target_data"]["driven_distance"] - last_round_driven_distance,targets_data[x]["target_data"]["driven_time"] - last_round_driven_time)
                                d[f"{st.session_state.emoji_round} {st.session_state.points_emoji}"] = ""
                                
                            targetboard_data.append(d)
                            
                            t_cnt = (t_cnt + 1) % 4
                        else:   # target is finish
                            d = {}
#                            section_distance = targets_data[x]["target_data"]["driven_distance"] - last_driven_distance
#                            section_time = targets_data[x]["target_data"]["driven_time"] - last_driven_time
                            sum_score = sum_score + targets_data[x]["target_data"]["score"]

                            round_distance = targets_data[x]["target_data"]["driven_distance"] - last_round_driven_distance
                            round_time = targets_data[x]["target_data"]["driven_time"] - last_round_driven_time
                            round_score = sum_score - last_round_score

                            # show target
                            d[str(targets_data[x]["user_name"]) + f" {st.session_state.target_emoji}"] = gymkhana_target

                            # show target score and summed up score so far
                            d[f"{st.session_state.points_emoji}"] = str(targets_data[x]["target_data"]["score"])
                            d[f"∑ {st.session_state.points_emoji}"] = str(sum_score)
                            
                            # show distance, time and average speed from target to target
                            d[f"Sektor - {st.session_state.distance_emoji}"] = showDistance(round_distance)
                            d[f"Sektor - {st.session_state.time_emoji}"] = showTime(round_time)
                            d[f"Sektor - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(round_distance,round_time)
                            
                            # show overall distance, time and cum. average speed
                            d[f"∑ Sektoren - {st.session_state.distance2_emoji}"] = showDistance(targets_data[x]["target_data"]["driven_distance"])
                            d[f"∑ Sektoren - {st.session_state.time2_emoji}"] = showTime(targets_data[x]["target_data"]["driven_time"])
                            d[f"Cum. Sektoren - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(targets_data[x]["target_data"]["driven_distance"],targets_data[x]["target_data"]["driven_time"])
                            d[f"{st.session_state.emoji_round} {st.session_state.points_emoji}"] = str(round_score) + f" {st.session_state.emoji_finish}"
                            
                            last_driven_distance = targets_data[x]["target_data"]["driven_distance"]
                            last_driven_time = targets_data[x]["target_data"]["driven_time"]
                            
                            targetboard_data.append(d)
                            
                            t_cnt = (t_cnt + 1) % 4

#                #if there is no entry, just add an empty one by calling the construct Entry with an empty dict
#                while len(targetboard_data)<1:
#                    d = {}
#                    d[str(targets_data[player]["user_name"]) + f" {st.session_state.target_emoji}"] = ""
#                                
#                    d[f"{st.session_state.points_emoji}"] = ""
#                    d[f" ∑ {st.session_state.points_emoji}"] = ""
#
#                    d[f"{st.session_state.distance_emoji}"] = ""
#                    d[f"{st.session_state.time_emoji}"] = ""
#                    d[f"Ø {st.session_state.average_speed_emoji}"] = ""
#
#                    d[f" ∑ {st.session_state.distance2_emoji}"] = ""
#                    d[f" ∑ {st.session_state.time2_emoji}"] = ""
#                    d[f"Cum. Ø {st.session_state.average_speed_emoji}"] = ""
#
#                    targetboard_data.append(d)

                df = pd.DataFrame( targetboard_data )
                
                if ( ( "end_data" in scoreboard_data[player] ) and not ( scoreboard_data[player]["end_data"] is None ) ):               
                    if(scoreboard_data[player]["end_data"]["false_start"]):
                        player_status = f"{st.session_state.false_start_emoji}" #"False Start!"
                    else:
                        player_status = f"{st.session_state.emoji_finish}" #"Finished"
                    
                    if ( autosave ):
                    
                        time1 = datetime.now(tz=ZoneInfo("Europe/Berlin"))
                        timedelta_1 = time1.utcoffset()
                        correct_time = datetime.strptime(scoreboard_data[player]["end_data"]["finished_time"], '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(timezone.utc)+timedelta_1
                        filename = str(scoreboard_data[player]["user_name"]) + "_" + str(scoreboard_data[player]["total_score"]) + "_" + str(correct_time.strftime("%d_%m_%Y_%H_%M_%S")) + ".csv"
                        file_exists = exists("gymkhana_training/" + str(lobby_id) + "/" + str(game_id) + "/runs/" + str(filename))
                    
                        if ( not file_exists ):
#                            df_to_save = df
#                            df_to_save.to_csv(str(dir_name) + str(filename), encoding="utf-8")
                            df.to_csv(str(dir_name) + str(filename), encoding="utf-8")
                            shutil.make_archive(str(zip_path) + str(output_filename), 'zip', dir_name)
                            st.success("Gymkhana Run Saved to File " + str(filename))
                            time.sleep(2)
                            st.experimental_rerun()
                    
                elif ( ( "start_data" in scoreboard_data[player] ) and not ( scoreboard_data[player]["start_data"] is None ) ):
                    player_status = f"{st.session_state.emoji_driving}" #"Driving"
                elif "enter_data" in scoreboard_data[player]:
                    player_status = f"{st.session_state.emoji_ready}" #"Ready"
                else:
                    player_status = ""

                st.text("Detailed Statistics of " + str(scoreboard_data[player]["user_name"]) + " (Status: " + str(player_status) + ")")
                st.dataframe(df)

            time.sleep(0.5)
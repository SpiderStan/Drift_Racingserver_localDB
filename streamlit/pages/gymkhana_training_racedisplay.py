import streamlit as st
import time
import os
from os.path import exists
import time
#import socket
from zoneinfo import ZoneInfo #to set the timezone to german time
from datetime import timedelta, timezone, datetime
#import operator
import pandas as pd 
import numpy as np
import qrcode
from PIL import Image
from math import floor

from .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger
from .helper import get_model, get_tuning, get_app_game_mode, get_starttime, get_track_cond, get_track_bundle, get_wheels, get_setup, getGameInfo, getScoreBoard, getDetailedTargetData, showTime, showDistance, showMeanSpeed, decode_targets

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

    st.subheader("Statistics of Gymkhana Training (" + str(game["gymkhana_training_targets"]) + ") " + str(game_id) + " from Lobby " + str(lobby_id))
    
    os.makedirs("gymkhana_training/" + str(lobby_id) + "/" + str(game_id) + "/runs/", exist_ok=True)
    dir_name = "gymkhana_training/" + str(lobby_id) + "/" + str(game_id) + "/runs/"
    output_filename = "Gymkhana_Training_" + str(lobby_id) + "_" + str(game_id)
    zip_path = "gymkhana_training/" + str(lobby_id) + "/" + str(game_id) + "/"

    placeholder1 = st.empty()
    placeholder2 = st.empty()
    targetboard = st.empty()
    placeholder3 = st.empty()
    placeholder4 = st.empty()

    with placeholder1.container():
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            if st.button(f"Back {st.session_state.back_emoji}"):
                st.session_state.num_stages = 1
                st.session_state.nextpage = "main_page"
                st.session_state.game_track_images_set = False
                st.session_state.game_track_images = None
                placeholder1.empty()
                placeholder2.empty()
                targetboard.empty()
                placeholder3.empty()
                placeholder4.empty()
                time.sleep(0.1)
                st.experimental_rerun()

#        with col2:
#            if st.button(f"Remove Player {st.session_state.remove_emoji}"):
#                st.session_state.num_stages = 1
#                st.session_state.nextpage = "remove_player_from_race"
#                st.session_state.game_track_images_set = game_track_images_set
#                st.session_state.game_track_images = game_track_images
#                placeholder1.empty()
#                placeholder2.empty()
#                targetboard.empty()
#                placeholder3.empty()
#                placeholder4.empty()
#                time.sleep(0.1)
#                st.experimental_rerun()

        with col3:
            if len(os.listdir(str(dir_name))) != 0:
                with open(str(zip_path) + str(output_filename) + ".zip", 'rb') as fp:
                    btn = st.download_button(
                        label=f"Download Saved Runs as zip {st.session_state.download_emoji}",
                        data=fp,
                        file_name=output_filename  + ".zip",
                        mime="application/zip"
                    )

        with col4:
            if len(os.listdir(str(dir_name))) != 0:
                if st.button(f"Delete Saved Runs {st.session_state.delete_emoji}"):
                    for f in os.listdir(dir_name):
                        os.remove(os.path.join(dir_name, f))
                    if os.path.exists(str(zip_path) + str(output_filename) + ".zip"):
                        os.remove(str(zip_path) + str(output_filename) + ".zip")  
                    placeholder1.empty()
                    placeholder2.empty()
                    targetboard.empty()
                    placeholder3.empty()
                    placeholder4.empty()
                    time.sleep(0.1)
                    st.experimental_rerun()

        with col5:
            if st.button(f"High Scores {st.session_state.award_trophy_emoji}"):
                st.session_state.nextpage = "highscore_list"
                st.session_state.game_track_images_set = game_track_images_set
                st.session_state.game_track_images = game_track_images
                placeholder1.empty()
                placeholder2.empty()
                targetboard.empty()
                placeholder3.empty()
                placeholder4.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col6:
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
                placeholder1.empty()
                placeholder2.empty()
                targetboard.empty()
                placeholder3.empty()
                placeholder4.empty()
                time.sleep(0.1)
                st.experimental_rerun()

    with placeholder2.container():
        autosave = st.checkbox("AutoSave", value=False, key=None, help="if set, gymkhana runs will be saved", on_change=None)
    
    t_list = decode_targets(game["gymkhana_training_targets"])

    with placeholder3.container():
        with st.expander(f"Game Settings {st.session_state.show_game_emoji} - Join the game via URL: http://"+str(st.session_state.ip_address)+":8001/driftapi/game/"+str(lobby_id)+"/"+str(stage_id)+" and GAME ID: "+str(game_id), expanded=False):

            game_mode = get_app_game_mode(game["game_mode"])
            starttime = get_starttime(game["start_time"])
            if ( ("laps_app" in game) and not ( game["laps_app"] is None) ):
                laps_app = int(game["lap_count"])
            track_cond = get_track_cond(game["track_condition"])
            track_bundle = get_track_bundle(game["track_bundle"])
            wheels = get_wheels(game["wheels"])
            setup = get_setup(game["setup_mode"])

            col11, col12, col13, col14 = st.columns(4)
            with col11:
                st.markdown("**GAME MODE:**")
            with col12:
                st.markdown(str(game_mode))

            col21, col22, col23, col24 = st.columns(4)
            with col21:
                st.markdown("**STARTTIME:**")
            with col22:
                st.markdown(str(starttime))
                 
            if ( ("laps_app" in game) and not ( game["laps_app"] is None) ):
                col31, col32, col33, col34 = st.columns(4)
                with col31:
                    st.markdown("**LAPS:**")
                with col32:
                    st.markdown(str(laps_app))

            col41, col42, col43, col44 = st.columns(4)
            with col41:
                st.markdown("**TRACK CONDITION:**")
            with col42:
                st.markdown(str(track_cond))

            col51, col52, col53, col54 = st.columns(4)
            with col51:
                st.markdown("**TRACK MODE:**")
            with col52:
                st.markdown(str(track_bundle))
                        
            col61, col62, col63, col64 = st.columns(4)
            with col61:
                st.markdown("**WHEELS:**")
            with col62:
                st.markdown(str(wheels))                       

            col71, col72, col73, col74 = st.columns(4)
            with col71:
                st.markdown("**SETUP:**")
            with col72:
                st.markdown(str(setup))  

#            col81, col82, col83, col84 = st.columns(4)
#            with col81:
#                st.markdown("**MODEL:**")
#            with col82:
#                st.markdown(str(model)) 

#            col91, col92, col93, col94 = st.columns(4)
#            with col91:
#                st.markdown("**TUNING:**")
#            with col92:
#                st.markdown(str(tuning)) 
            
            submitUri:str = "http://"+str(st.session_state.ip_address)+":8001/driftapi/game/"+str(lobby_id)+"/"+str(stage_id)
            st.image(getqrcode(submitUri), clamp=True)
            st.write("URL: "+submitUri)
            st.write("GAME ID: "+game_id)

    with placeholder4.container():  
        with st.expander(f"Track Layout {st.session_state.show_game_emoji}", expanded=False):
            
            track_image = st.empty()
            track_image_upload = st.file_uploader("Here you can upload the track layout", type=['png', 'jpg'], accept_multiple_files=False, key=None, help=None, on_change=None, args=None, kwargs=None, disabled=False)

            if(game_track_images_set == False): # no track image upload so far
                if(track_image_upload != None): # user has supplied a track image
                    game_track_images_set = True
                    track_image.image(track_image_upload, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto") # Show Uploaded Track Image
                    game_track_images = track_image_upload # store in session state
            elif(game_track_images_set == True): # track image existing
                if(track_image_upload != None): # user has supplied a new track image
                    game_track_images_set = True
                    track_image.image(track_image_upload, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto") # Show Uploaded Track Image
                    game_track_images = track_image_upload # store in session state
                else:
                    track_image.image(game_track_images, caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto") # Show Prev. Uploaded Track Image

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

                                d = {}
                                d[str(targets_data[x]["user_name"]) + f" {st.session_state.target_emoji}"] = f"{st.session_state.remove_emoji}"
                                
                                d[f"{st.session_state.points_emoji}"] = f"{st.session_state.remove_emoji}"
                                d[f"∑ {st.session_state.points_emoji}"] = f"{st.session_state.remove_emoji}"

                                d[f"SECTOR - {st.session_state.distance_emoji}"] = f"{st.session_state.remove_emoji}"
                                d[f"SECTOR - {st.session_state.time_emoji}"] = f"{st.session_state.remove_emoji}"
                                d[f"SECTOR - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.remove_emoji}"

                                if(t_cnt == 3): #the fourth (last) target
                                    d[f"∑ SECTORS - {st.session_state.distance2_emoji}"] = f"{st.session_state.remove_emoji} {st.session_state.round_emoji}"
                                    d[f"∑ SECTORS - {st.session_state.time2_emoji}"] = f"{st.session_state.remove_emoji} {st.session_state.round_emoji}"
                                    d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.remove_emoji} {st.session_state.round_emoji}"
                                    d[f"{st.session_state.round_emoji} {st.session_state.points_emoji}"] = f"- {st.session_state.round_emoji}"
                                else:
                                    d[f"∑ SECTORS - {st.session_state.distance2_emoji}"] = f"{st.session_state.remove_emoji}"
                                    d[f"∑ SECTORS - {st.session_state.time2_emoji}"] = f"{st.session_state.remove_emoji}"
                                    d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.remove_emoji}"
                                    d[f"{st.session_state.round_emoji} {st.session_state.points_emoji}"] = ""
                                
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
                            d[f"SECTOR - {st.session_state.distance_emoji}"] = showDistance(section_distance)
                            d[f"SECTOR - {st.session_state.time_emoji}"] = showTime(section_time)
                            d[f"SECTOR - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(section_distance,section_time)
                            
                            last_driven_distance = targets_data[x]["target_data"]["driven_distance"]
                            last_driven_time = targets_data[x]["target_data"]["driven_time"]                 
                            
                            # show distance, time and cum. average speed from round to round
                            if(targets_data[x]["target_data"]["target_code"] == t_list[3]): #the fourth (last) target
                                round_distance = targets_data[x]["target_data"]["driven_distance"] - last_round_driven_distance
                                round_time = targets_data[x]["target_data"]["driven_time"] - last_round_driven_time
                                round_score = sum_score - last_round_score
                                d[f"∑ SECTORS - {st.session_state.distance2_emoji}"] = showDistance(round_distance) + f" {st.session_state.round_emoji}"
                                d[f"∑ SECTORS - {st.session_state.time2_emoji}"] = showTime(round_time) + f" {st.session_state.round_emoji}"
                                d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(round_distance,round_time) + f" {st.session_state.round_emoji}"
                                d[f"{st.session_state.round_emoji} {st.session_state.points_emoji}"] = str(round_score) + f" {st.session_state.round_emoji}"
                                last_round_driven_distance = targets_data[x]["target_data"]["driven_distance"]
                                last_round_driven_time = targets_data[x]["target_data"]["driven_time"]
                                last_round_score = last_round_score + round_score
                            else:
                                d[f"∑ SECTORS - {st.session_state.distance2_emoji}"] = showDistance(targets_data[x]["target_data"]["driven_distance"] - last_round_driven_distance)
                                d[f"∑ SECTORS - {st.session_state.time2_emoji}"] = showTime(targets_data[x]["target_data"]["driven_time"] - last_round_driven_time)
                                d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(targets_data[x]["target_data"]["driven_distance"] - last_round_driven_distance,targets_data[x]["target_data"]["driven_time"] - last_round_driven_time)
                                d[f"{st.session_state.round_emoji} {st.session_state.points_emoji}"] = ""
                                
                            targetboard_data.append(d)
                            
                            t_cnt = (t_cnt + 1) % 4
                        else:   # target is finish
                            d = {}
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
                            d[f"SECTOR - {st.session_state.distance_emoji}"] = showDistance(round_distance)
                            d[f"SECTOR - {st.session_state.time_emoji}"] = showTime(round_time)
                            d[f"SECTOR - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(round_distance,round_time)
                            
                            # show overall distance, time and cum. average speed
                            d[f"∑ SECTORS - {st.session_state.distance2_emoji}"] = showDistance(targets_data[x]["target_data"]["driven_distance"])
                            d[f"∑ SECTORS - {st.session_state.time2_emoji}"] = showTime(targets_data[x]["target_data"]["driven_time"])
                            d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(targets_data[x]["target_data"]["driven_distance"],targets_data[x]["target_data"]["driven_time"])
                            d[f"{st.session_state.round_emoji} {st.session_state.points_emoji}"] = str(round_score) + f" {st.session_state.finish_emoji}"
                            
                            last_driven_distance = targets_data[x]["target_data"]["driven_distance"]
                            last_driven_time = targets_data[x]["target_data"]["driven_time"]
                            
                            targetboard_data.append(d)
                            
                            t_cnt = (t_cnt + 1) % 4

                df = pd.DataFrame( targetboard_data )
                
                if ( ( "end_data" in scoreboard_data[player] ) and not ( scoreboard_data[player]["end_data"] is None ) ):               
                    if(scoreboard_data[player]["end_data"]["false_start"]):
                        player_status = f"{st.session_state.false_start_emoji}" #"False Start!"
                    else:
                        player_status = f"{st.session_state.finish_emoji}" #"Finished"
                    
                    if ( autosave ):
                    
                        time1 = datetime.now(tz=ZoneInfo("Europe/Berlin"))
                        timedelta_1 = time1.utcoffset()
                        correct_time = datetime.strptime(scoreboard_data[player]["end_data"]["finished_time"], '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(timezone.utc)+timedelta_1
                        filename = str(scoreboard_data[player]["user_name"]) + "_" + str(scoreboard_data[player]["total_score"]) + "_" + str(correct_time.strftime("%d_%m_%Y_%H_%M_%S")) + ".csv"
                        file_exists = exists("gymkhana_training/" + str(lobby_id) + "/" + str(game_id) + "/runs/" + str(filename))
                    
                        if ( not file_exists ):
                            df.to_csv(str(dir_name) + str(filename), encoding="utf-8")
                            shutil.make_archive(str(zip_path) + str(output_filename), 'zip', dir_name)
                            st.success("Gymkhana Run Saved to File " + str(filename))
                            time.sleep(2)
                            st.experimental_rerun()
                    
                elif ( ( "start_data" in scoreboard_data[player] ) and not ( scoreboard_data[player]["start_data"] is None ) ):
                    player_status = f"{st.session_state.driving_emoji}" #"Driving"
                elif "enter_data" in scoreboard_data[player]:
                    player_status = f"{st.session_state.ready_emoji}" #"Ready"
                else:
                    player_status = ""

                model = get_model(scoreboard_data[player]["enter_data"]["engine_type"],scoreboard_data[player]["enter_data"]["tuning_type"])
                tuning = get_tuning(scoreboard_data[player]["enter_data"]["tuning_type"])
               
                with st.expander("Detailed Statistics of " + str(scoreboard_data[player]["user_name"]) + "  " + str(player_status) + " (" + str(model) + " | " + str(tuning) + f") {st.session_state.show_game_emoji}", expanded=False):
                    st.table(df)

            time.sleep(0.5)
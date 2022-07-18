import streamlit as st
import time
#import socket
from backports.zoneinfo import ZoneInfo #to set the timezone to german time
from datetime import timedelta, timezone, datetime
import pandas as pd 
import numpy as np
import qrcode
from PIL import Image
from math import floor

from .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger
from .helper import get_bonus_target, get_game_mode, get_joker_lap_code, get_app_game_mode, get_starttime, get_track_cond, get_track_bundle, get_wheels, get_setup, get_bool, get_model, get_tuning, handleCurrentTrackCondition, getGameInfo, getScoreBoard, getDetailedTargetData, showTime, showDistance, showMeanSpeed

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
    game_id = st.session_state.game_id
    stage_id = st.session_state.stage_id
    num_stages = st.session_state.num_stages

    game_track_images_set = st.session_state.game_track_images_set
    game_track_images = st.session_state.game_track_images

    st.subheader("Game Statistics of Game " + str(game_id) + " from Lobby " + str(lobby_id))

    next_race = st.empty()

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

    placeholder1 = st.empty()
    placeholder2 = st.empty()
    scoreboard = st.empty()
    placeholder3 = st.empty()
    placeholder4 = st.empty()
    
    with placeholder1.container():  
        if( game["game_mode"] == "GYMKHANA" ):
            
            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

            with col1:
                if st.button(f"Back {st.session_state.back_emoji}"):
                    st.session_state.nextpage = "main_page"
                    st.session_state.game_track_images_set = False
                    st.session_state.game_track_images = None
                    next_race.empty()
                    scoreboard.empty()
                    placeholder1.empty()
                    placeholder2.empty()
                    placeholder3.empty()
                    placeholder4.empty()
                    time.sleep(0.1)
                    st.experimental_rerun()

            with col2:
                if st.button(f"Remove Player {st.session_state.remove_emoji}"):
                    st.session_state.nextpage = "remove_player_from_race"
                    st.session_state.game_track_images_set = game_track_images_set
                    st.session_state.game_track_images = game_track_images
                    next_race.empty()
                    scoreboard.empty()
                    placeholder1.empty()
                    placeholder2.empty()
                    placeholder3.empty()
                    placeholder4.empty()
                    time.sleep(0.1)
                    st.experimental_rerun()

            with col3:
                if st.button(f"Reset Game {st.session_state.reset_emoji}"):
                    result = fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/reset/{lobby_id}/{game_id}/{stage_id}")
                    st.session_state.new_game = False
                    next_race.empty()
                    scoreboard.empty()
                    placeholder1.empty()
                    placeholder2.empty()
                    placeholder3.empty()
                    placeholder4.empty()
                    time.sleep(0.1)
                    st.experimental_rerun()

            with col4:
                if st.button(f"Download Data {st.session_state.download_emoji}"):
                    st.session_state.nextpage = "download_race"
                    st.session_state.game_track_images_set = game_track_images_set
                    st.session_state.game_track_images = game_track_images
                    next_race.empty()
                    scoreboard.empty()
                    placeholder1.empty()
                    placeholder2.empty()
                    placeholder3.empty()
                    placeholder4.empty()
                    time.sleep(0.1)
                    st.experimental_rerun()

            with col5:
                if st.button(f"High Scores {st.session_state.award_trophy_emoji}"):
                    st.session_state.nextpage = "highscore_list"
                    st.session_state.game_track_images_set = game_track_images_set
                    st.session_state.game_track_images = game_track_images
                    next_race.empty()
                    scoreboard.empty()
                    placeholder1.empty()
                    placeholder2.empty()
                    placeholder3.empty()
                    placeholder4.empty()
                    time.sleep(0.1)
                    st.experimental_rerun()

            if( game["individual_trial"] ):                    
                with col6:
                    if st.button(f"Award Ceremony {st.session_state.award_1st_emoji}"):
                        st.session_state.show_awards = True
                        next_race.empty()
                        scoreboard.empty()
                        placeholder1.empty()
                        placeholder2.empty()
                        placeholder3.empty()
                        placeholder4.empty()
                        time.sleep(0.1)
                        st.experimental_rerun()

            with col7:
                if st.button(f"Delete Game {st.session_state.delete_emoji}"):
                    result = fetch_delete(f"{settings.driftapi_path}/driftapi/manage_game/delete/{lobby_id}/{game_id}")
                    st.session_state.game_id = None
                    st.session_state.stage_id = 1
                    st.session_state.num_stages = 1
                    st.session_state.game_track_images_set = False
                    st.session_state.game_track_images = None
                    st.session_state.nextpage = "main_page"
                    next_race.empty()
                    scoreboard.empty()
                    placeholder1.empty()
                    placeholder2.empty()
                    placeholder3.empty()
                    placeholder4.empty()
                    time.sleep(0.1)
                    st.experimental_rerun()

        else:
        
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

            with col1:
                if st.button(f"Back {st.session_state.back_emoji}"):
                    st.session_state.nextpage = "main_page"
                    st.session_state.game_track_images_set = False
                    st.session_state.game_track_images = None
                    next_race.empty()
                    scoreboard.empty()
                    placeholder1.empty()
                    placeholder2.empty()
                    placeholder3.empty()
                    placeholder4.empty()
                    time.sleep(0.1)
                    st.experimental_rerun()

            if ("num_sectors" in game) and (game["num_sectors"] is not None):
                with col2:
                    if st.button(f"Sector Display {st.session_state.driving_emoji}"):
                        st.session_state.nextpage = "sectordisplay"
                        st.session_state.game_track_images_set = game_track_images_set
                        st.session_state.game_track_images = game_track_images
                        next_race.empty()
                        scoreboard.empty()
                        placeholder1.empty()
                        placeholder2.empty()
                        placeholder3.empty()
                        placeholder4.empty()
                        time.sleep(0.1)
                        st.experimental_rerun()
                        
            with col3:
                if st.button(f"Remove Player {st.session_state.remove_emoji}"):
                    st.session_state.nextpage = "remove_player_from_race"
                    st.session_state.game_track_images_set = game_track_images_set
                    st.session_state.game_track_images = game_track_images
                    next_race.empty()
                    scoreboard.empty()
                    placeholder1.empty()
                    placeholder2.empty()
                    placeholder3.empty()
                    placeholder4.empty()
                    time.sleep(0.1)
                    st.experimental_rerun()

            with col4:
                if st.button(f"Reset Game {st.session_state.reset_emoji}"):
                    result = fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/reset/{lobby_id}/{game_id}/{stage_id}")
                    st.session_state.new_game = False
                    next_race.empty()
                    scoreboard.empty()
                    placeholder1.empty()
                    placeholder2.empty()
                    placeholder3.empty()
                    placeholder4.empty()
                    time.sleep(0.1)
                    st.experimental_rerun()

            with col5:
                if st.button(f"Download Data {st.session_state.download_emoji}"):
                    st.session_state.nextpage = "download_race"
                    st.session_state.game_track_images_set = game_track_images_set
                    st.session_state.game_track_images = game_track_images
                    next_race.empty()
                    scoreboard.empty()
                    placeholder1.empty()
                    placeholder2.empty()
                    placeholder3.empty()
                    placeholder4.empty()
                    time.sleep(0.1)
                    st.experimental_rerun()

            if( game["individual_trial"] ):
                with col6:
                    if st.button(f"Award Ceremony {st.session_state.award_1st_emoji}"):
                        st.session_state.show_awards = True

            with col7:
                if st.button(f"Delete Game {st.session_state.delete_emoji}"):
                    result = fetch_delete(f"{settings.driftapi_path}/driftapi/manage_game/delete/{lobby_id}/{game_id}")
                    st.session_state.game_id = None
                    st.session_state.stage_id = 1
                    st.session_state.num_stages = 1
                    st.session_state.game_track_images_set = False
                    st.session_state.game_track_images = None
                    st.session_state.nextpage = "main_page"
                    next_race.empty()
                    scoreboard.empty()
                    placeholder1.empty()
                    placeholder2.empty()
                    placeholder3.empty()
                    placeholder4.empty()
                    time.sleep(0.1)
                    st.experimental_rerun()   

    with placeholder2.container():  
        with st.expander(f"Game Settings {st.session_state.show_game_emoji} - Join the game via URL: http://"+str(st.session_state.ip_address)+":8001/driftapi/game/"+str(lobby_id)+"/"+str(stage_id)+" and GAME ID: "+str(game_id), expanded=False):

            game_mode = get_app_game_mode(game["game_mode"])
            starttime = get_starttime(game["start_time"])
            if ( ("laps_app" in game) and not ( game["laps_app"] is None) ):
                laps_app = int(game["lap_count"])
            track_cond = get_track_cond(game["track_condition"])
            track_bundle = get_track_bundle(game["track_bundle"])
            wheels = get_wheels(game["wheels"])
            setup = get_setup(game["setup_mode"])
            
            if ( (game["game_mode"] != "GYMKHANA") and (game["game_mode"] != "GYMKHANA_TRAINING") ):
                if ( ("joker_lap_code" in game) and not ( game["joker_lap_code"] is None) ):
                    joker_lap_code = get_joker_lap_code(game["joker_lap_code"])
                    if ( ("joker_lap_precondition_code" in game) and not ( game["joker_lap_precondition_code"] is None) ):
                        joker_lap_precondition_code = get_joker_lap_code(game["joker_lap_precondition_code"])
             
                if ( ("num_sectors" in game) and not ( game["num_sectors"] is None) ):
                    num_sectors = int(game["num_sectors"])

            if( game["game_mode"] == "GYMKHANA"):
                if ( ("bonus_target" in game) and not ( game["bonus_target"] is None) ):
                    bonus_target = get_bonus_target(game["bonus_target"])
                else:
                    bonus_target = "360"

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

            if ( (game["game_mode"] != "GYMKHANA") and (game["game_mode"] != "GYMKHANA_TRAINING") ):
                if ( ("joker_lap_code" in game) and not ( game["joker_lap_code"] is None) ):
                
                    col101, col102, col103, col104 = st.columns(4)
                    with col101:
                        st.markdown("**JOKER LAP TARGET:**")
                    with col102:
                        st.markdown(str(joker_lap_code)) 

                    if ( ("joker_lap_precondition_code" in game) and not ( game["joker_lap_precondition_code"] is None) ):

                        col111, col112, col113, col114 = st.columns(4)
                        with col111:
                            st.markdown("**JOKER LAP PRECONDITION TARGET:**")
                        with col112:
                            st.markdown(str(joker_lap_precondition_code)) 

                if ( ("num_sectors" in game) and not ( game["num_sectors"] is None) ):
                    col121, col122, col123, col124 = st.columns(4)
                    with col121:
                        st.markdown("**NUM SECTORS:**")
                    with col122:
                        st.markdown(str(num_sectors)) 


            if( game["game_mode"] == "GYMKHANA"):
                col131, col132, col133, col134 = st.columns(4)
                with col131:
                    st.markdown("**BONUS TARGET:**")
                with col132:
                    st.markdown(str(bonus_target)) 
            
            submitUri:str = "http://"+str(st.session_state.ip_address)+":8001/driftapi/game/"+str(lobby_id)+"/"+str(stage_id)
            st.image(getqrcode(submitUri), clamp=True)
            st.write("URL: "+submitUri)
            st.write("GAME ID: "+game_id)


    with placeholder3.container():  
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

        game = getGameInfo(lobby_id, game_id, stage_id)
        
        if(game["start_time"] != None):
            current_time = datetime.now().astimezone(timezone.utc)
            if (st.session_state.new_game == True):
                start_time = datetime.strptime(game["start_time"],'%Y-%m-%dT%H:%M:%S%z')
            else:
                try:
                    start_time = datetime.strptime(game["start_time"],'%Y-%m-%d %H:%M:%S.%f%z')
                except:
                    start_time = datetime.strptime(game["start_time"],'%Y-%m-%dT%H:%M:%S%z')
            time_delay = start_time - current_time
            if(current_time <= start_time):
                next_race.text("Game starts in approx. " + str(time_delay))
            else:
                next_race.text("Time elapsed! Please press Button 'Reset Game' and Sync. in Sturmkind App before entering the Game")

        scoreboard_data = getScoreBoard(lobby_id, game_id, stage_id)

        with scoreboard.container():
            
            # CSS to inject contained in a string
            hide_dataframe_row_index = """
                        <style>
                        .row_heading.level0 {display:none}
                        .blank {display:none}
                        </style>
            """
            # Inject CSS with Markdown
            st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                    
            def constructEntry(r:dict):
                d = {
                    "DRIVER":r["user_name"] if "user_name" in r else "",
                }
                        
# tracking track condition 
                current_track_condition = handleCurrentTrackCondition(r)
                d["TRACK"] = current_track_condition
                        
# differentiate between RACE and GYMKHANA game mode:
                if ( game["game_mode"] == "RACE" ):

# handle laps_completed:
                    if "enter_data" in r:
                        d["LAPS"] = r["laps_completed"]
                    else:
                        d["LAPS"] = "-"

                    if joker_lap_code != None:
                        d["JOKER"] = int(r["joker_laps_counter"]) if "joker_laps_counter" in r else 0

# handle best_lap:
                    if "best_lap" in r:
                        d["BEST"] = showTime(r["best_lap"])
                    else:
                        d["BEST"] = showTime(None)

# handle last_lap:
                    if "last_lap" in r:
                        d["LAST"] = showTime(r["last_lap"])
                    else:
                        d["LAST"] = showTime(None)
                        
# handle total_time:
                    if "total_time" in r:
                        d["TOTAL TIME"] = showTime(r["total_time"])
                    else:
                        d["TOTAL TIME"] = showTime(None)  

# handle total_driven_distance
                    if ( ( "end_data" in r ) and not ( r["end_data"] is None ) ):
                       d["TOTAL DISTANCE"] = showDistance(r["end_data"]["total_driven_distance"])
                    else:
                        d["TOTAL DISTANCE"] = ""               
                    
# changed to use emojis for status information
                    if ( ( "end_data" in r ) and not ( r["end_data"] is None ) ):
                        if(r["end_data"]["false_start"]):
                            d["STATUS"] = f"{st.session_state.false_start_emoji}" #"False Start!"
                            total_time_list.append(showTime(86400)) # fake 24h time
                            best_lap_list.append(showTime(86400)) # fake 24h time
                            shortest_distance_list.append(showDistance(9999999)) # fake 9999999 m
                        else:
                            d["STATUS"] = f"{st.session_state.finish_emoji}" #"Finished"
                            if(r["enter_data"]["lap_count"] == d["LAPS"]):
                                total_time_list.append(showTime(r["total_time"])) # real driven time
                                best_lap_list.append(showTime(r["best_lap"])) # real best lap/target time
                                shortest_distance_list.append(showDistance(r["end_data"]["total_driven_distance"])) # real total driven distance
                            else:
                                total_time_list.append(showTime(86400)) # fake 24h time
                                best_lap_list.append(showTime(86400)) # fake 24h time
                                shortest_distance_list.append(showDistance(9999999)) # fake 9999999 m
                    elif ( ( "start_data" in r ) and not ( r["start_data"] is None ) ):
                        d["STATUS"] = f"{st.session_state.driving_emoji}" #"Driving"
                    elif "enter_data" in r:
                        d["STATUS"] = f"{st.session_state.ready_emoji}" #"Ready"
                    else:
                        d["STATUS"] = ""

                elif ( game["game_mode"] == "GYMKHANA" ):
# changed way of building up d slightly so that more readable strings will be displayed
                    display_text_speed = f"BEST SPEED"
                    display_text_angle = f"BEST ANGLE"
                    display_text_360 = f"BEST 360"
                    display_text_180 = f"BEST 180"

# handle bonus target set:
                    if ( "bonus_target" in game ) and (not game["bonus_target"] is None):
                        if ( game["bonus_target"] == "SPEED" ):
                            display_text_speed = display_text_speed + f" ({st.session_state.award_trophy_emoji})"
                        elif ( game["bonus_target"] == "ANGLE" ):
                            display_text_angle = display_text_angle + f" ({st.session_state.award_trophy_emoji})"
                        elif ( game["bonus_target"] == "360" ):
                            display_text_360 = display_text_360 + f" ({st.session_state.award_trophy_emoji})"
                        elif ( game["bonus_target"] == "180" ):
                            display_text_180 = display_text_180 + f" ({st.session_state.award_trophy_emoji})"
                    else:
                        display_text_360 = display_text_360 + f" ({st.session_state.award_trophy_emoji})"

                    if ("best_speed_drift" in r) and (not (r["best_speed_drift"] is None)):
                        d[display_text_speed] = int(r["best_speed_drift"])
                    else:
                        d[display_text_speed] = 0

                    if ("best_angle_drift" in r) and (not (r["best_angle_drift"] is None)):
                        d[display_text_angle] = int(r["best_angle_drift"])
                    else:
                        d[display_text_angle] = 0

                    if ("best_360_angle" in r) and (not (r["best_360_angle"] is None)):
                        d[display_text_360] = int(r["best_360_angle"])
                    else:
                        d[display_text_360] = 0                   
                    
                    if ("best_180_speed" in r) and (not (r["best_180_speed"] is None)):
                        d[display_text_180] = int(r["best_180_speed"])
                    else:
                        d[display_text_180] = 0  

# handle total_score:
                    if ("total_score" in r) and (not (r["total_score"] is None)):
                        d["TOTAL POINTS"] = int(r["total_score"])
                    else:
                        d["TOTAL POINTS"] = 0

# changed to use emojis for status information
                    if ( ( "end_data" in r ) and not ( r["end_data"] is None ) ):
                        if ( "bonus_target" in game ) and (not game["bonus_target"] is None):
                            if ( game["bonus_target"] == "SPEED" ):
                                if (not r["best_speed_drift"] is None):
                                    best_target_set = int(r["best_speed_drift"])
                                else:
                                    best_target_set = 0
                            elif ( game["bonus_target"] == "ANGLE" ):
                                if (not r["best_angle_drift"] is None):
                                    best_target_set = int(r["best_angle_drift"])
                                else:
                                    best_target_set = 0
                            elif ( game["bonus_target"] == "360" ):
                                if (not r["best_360_angle"] is None):
                                    best_target_set = int(r["best_360_angle"])
                                else:
                                    best_target_set = 0
                            elif ( game["bonus_target"] == "180" ):
                                if (not r["best_180_speed"] is None):
                                    best_target_set = int(r["best_180_speed"])
                                else:
                                    best_target_set = 0
                        else:
                            if (not r["best_360_angle"] is None):
                                best_target_set = int(r["best_360_angle"]) # default
                            else:
                                best_target_set = 0
                        
                        if(r["end_data"]["false_start"]):
                            d["STATUS"] = f"{st.session_state.false_start_emoji}" #"False Start!"
                            total_score_list.append(int(r["total_score"]))
                            best_target_list.append(best_target_set) # best_target_set, default is 360
                            shortest_distance_list.append(showDistance(r["end_data"]["total_driven_distance"])) # real total driven distance
                        else:
                            d["STATUS"] = f"{st.session_state.finish_emoji}" #"Finished"
                            total_score_list.append(int(r["total_score"]))
                            best_target_list.append(best_target_set) # best_target_set, default is 360
                            shortest_distance_list.append(showDistance(r["end_data"]["total_driven_distance"])) # real total driven distance
                    elif ( ( "start_data" in r ) and not ( r["start_data"] is None ) ):
                        d["STATUS"] = f"{st.session_state.driving_emoji}" #"Driving"
                    elif "enter_data" in r:
                        d["STATUS"] = f"{st.session_state.ready_emoji}" #"Ready"
                    else:
                        d["STATUS"] = ""

                return (d)

# handle awards after the race (Race: 1st, 2nd, 3rd and bonus award for fastest lap)
            total_time_list = []
            best_lap_list = []
            total_score_list = []
            best_target_list = []
            shortest_distance_list = []
            scoreboard_display = [None] * len(scoreboard_data)
            (scoreboard_display) = [constructEntry(r) for r in scoreboard_data if (type(r) is dict)]

            #if there is no entry, just add an empty one by calling the construct Entry with an empty dict
            while len(scoreboard_display)<1:
                scoreboard_display.append(constructEntry({}))
  
            scoreboard_len = len(scoreboard_display)

            if( game["individual_trial"] ):
                if (st.session_state.show_awards):
                    if(len(total_time_list) == scoreboard_len): # all players finished race    
                        min_total_time_indices_list = get_minvalue(total_time_list)
                        min_total_time_indices_list_len = len(min_total_time_indices_list)
        # handle normal case: one player on 1st place
                        for x in min_total_time_indices_list:
                            if( (total_time_list[x] != "1440:00.000") ):
                                scoreboard_display[x]["POS"] = f"{st.session_state.award_1st_emoji}"
                                total_time_list[x] = showTime(172800)  # fake 48h time - meaning player has been handled
                            else:
                                scoreboard_display[x]["POS"] = "-"
        # cont. handle normal case: one player on 2nd place as well as special case more players on 2nd place
                        if min_total_time_indices_list_len == 1:
                            min_total_time_indices_list = get_minvalue(total_time_list)
                            min_total_time_indices_list_len = len(min_total_time_indices_list)
                            for x in min_total_time_indices_list:
                                if( (total_time_list[x] != "2880:00.000") ):
                                    if( (total_time_list[x] == "1440:00.000") ):
                                        scoreboard_display[x]["POS"] = "-"
                                    else:
                                        scoreboard_display[x]["POS"] = f"{st.session_state.award_2nd_emoji}"
                                        total_time_list[x] = showTime(172800)  # fake 48h time - meaning player has been handled
        # cont. handle normal case: one player on 3rd place as well as special case more players on 3rd place
                            if min_total_time_indices_list_len == 1:
                                min_total_time_indices_list = get_minvalue(total_time_list)
                                min_total_time_indices_list_len = len(min_total_time_indices_list)
                                for x in min_total_time_indices_list:
                                    if( (total_time_list[x] != "2880:00.000") ):
                                        if( (total_time_list[x] == "1440:00.000") ):
                                            scoreboard_display[x]["POS"] = "-"
                                        else:
                                            scoreboard_display[x]["POS"] = f"{st.session_state.award_3rd_emoji}"
                                            total_time_list[x] = showTime(172800)  # fake 48h time
        # handle special case: two players on 1st place as well as special case more players on 3rd place                                   
                        elif min_total_time_indices_list_len == 2:
                            min_total_time_indices_list = get_minvalue(total_time_list)
                            min_total_time_indices_list_len = len(min_total_time_indices_list)
                            for x in min_total_time_indices_list:
                                if( (total_time_list[x] != "2880:00.000") ):
                                    if( (total_time_list[x] == "1440:00.000") ):
                                        scoreboard_display[x]["POS"] = "-"
                                    else:
                                        scoreboard_display[x]["POS"] = f"{st.session_state.award_3rd_emoji}"
                                        total_time_list[x] = showTime(172800)  # fake 48h time

        # award for best lap / best bonus target score                        
                    if(len(best_lap_list) == scoreboard_len): # all players finished race
                        min_best_lap_indices_list = get_minvalue(best_lap_list)
                        for x in range(len(best_lap_list)):
                            if x in min_best_lap_indices_list:
                                if( (best_lap_list[x] != "1440:00.000") ):
                                    scoreboard_display[x]["BEST ROUND"] = f"{st.session_state.award_bonus_emoji}"
                                else:
                                    scoreboard_display[x]["BEST ROUND"] = "-"
                            else:
                                scoreboard_display[x]["BEST ROUND"] = "-"

                    if(len(total_score_list) == scoreboard_len): # all players finished race    
                        max_total_score_indices_list = get_maxvalue(total_score_list)
                        max_total_score_indices_list_len = len(max_total_score_indices_list)
        # handle normal case: one player on 1st place
                        for x in max_total_score_indices_list:
                            scoreboard_display[x]["POS"] = f"{st.session_state.award_1st_emoji}"
                            total_score_list[x] = 0  # fake 0 score - meaning player has been handled
        # cont. handle normal case: one player on 2nd place as well as special case more players on 2nd place
                        if max_total_score_indices_list_len == 1:
                            max_total_score_indices_list = get_maxvalue(total_score_list)
                            max_total_score_indices_list_len = len(max_total_score_indices_list)
                            for x in max_total_score_indices_list:
                                scoreboard_display[x]["POS"] = f"{st.session_state.award_2nd_emoji}"
                                total_score_list[x] = 0  # fake 0 score - meaning player has been handled
        # cont. handle normal case: one player on 3rd place as well as special case more players on 3rd place
                        if max_total_score_indices_list_len == 1:
                            max_total_score_indices_list = get_maxvalue(total_score_list)
                            max_total_score_indices_list_len = len(max_total_score_indices_list)
                            for x in max_total_score_indices_list:
                                scoreboard_display[x]["POS"] = f"{st.session_state.award_3rd_emoji}"
                                total_score_list[x] = 0  # fake 0 score - meaning player has been handled
        # handle special case: two players on 1st place as well as special case more players on 3rd place                                   
                        elif max_total_score_indices_list_len == 2:
                            max_total_score_indices_list = get_maxvalue(total_score_list)
                            max_total_score_indices_list_len = len(max_total_score_indices_list)
                            for x in max_total_score_indices_list:
                                scoreboard_display[x]["POS"] = f"{st.session_state.award_3rd_emoji}"
                                total_score_list[x] = 0  # fake 0 score - meaning player has been handled

                    if(len(best_target_list) == scoreboard_len): # all players finished race
                        max_best_target_indices_list = get_maxvalue(best_target_list)
                        for x in range(len(best_target_list)):
                            if x in max_best_target_indices_list:
                                scoreboard_display[x]["BONUS TARGET"] = f"{st.session_state.award_bonus_emoji}"
                            else:
                                scoreboard_display[x]["BONUS TARGET"] = "-"

        # award for shortest distance                        
                    if(len(shortest_distance_list) == scoreboard_len): # all players finished race
                        min_shortest_distance_list_indices_list = get_minvalue(shortest_distance_list)
                        for x in range(len(shortest_distance_list)):
                            if x in min_shortest_distance_list_indices_list:
                                if( (shortest_distance_list[x] != "9999km 999m") ):
                                    scoreboard_display[x]["SHORTEST DISTANCE"] = f"{st.session_state.award_bonus_emoji}"
                                else:
                                    scoreboard_display[x]["SHORTEST DISTANCE"] = "-"
                            else:
                                scoreboard_display[x]["SHORTEST DISTANCE"] = "-"

            else:

                if(len(total_time_list) == scoreboard_len): # all players finished race    
                    min_total_time_indices_list = get_minvalue(total_time_list)
                    min_total_time_indices_list_len = len(min_total_time_indices_list)
    # handle normal case: one player on 1st place
                    for x in min_total_time_indices_list:
                        if( (total_time_list[x] != "1440:00.000") ):
                            scoreboard_display[x]["POS"] = f"{st.session_state.award_1st_emoji}"
                            total_time_list[x] = showTime(172800)  # fake 48h time - meaning player has been handled
                        else:
                            scoreboard_display[x]["POS"] = "-"
    # cont. handle normal case: one player on 2nd place as well as special case more players on 2nd place
                    if min_total_time_indices_list_len == 1:
                        min_total_time_indices_list = get_minvalue(total_time_list)
                        min_total_time_indices_list_len = len(min_total_time_indices_list)
                        for x in min_total_time_indices_list:
                            if( (total_time_list[x] != "2880:00.000") ):
                                if( (total_time_list[x] == "1440:00.000") ):
                                    scoreboard_display[x]["POS"] = "-"
                                else:
                                    scoreboard_display[x]["POS"] = f"{st.session_state.award_2nd_emoji}"
                                    total_time_list[x] = showTime(172800)  # fake 48h time - meaning player has been handled
    # cont. handle normal case: one player on 3rd place as well as special case more players on 3rd place
                        if min_total_time_indices_list_len == 1:
                            min_total_time_indices_list = get_minvalue(total_time_list)
                            min_total_time_indices_list_len = len(min_total_time_indices_list)
                            for x in min_total_time_indices_list:
                                if( (total_time_list[x] != "2880:00.000") ):
                                    if( (total_time_list[x] == "1440:00.000") ):
                                        scoreboard_display[x]["POS"] = "-"
                                    else:
                                        scoreboard_display[x]["POS"] = f"{st.session_state.award_3rd_emoji}"
                                        total_time_list[x] = showTime(172800)  # fake 48h time
    # handle special case: two players on 1st place as well as special case more players on 3rd place                                   
                    elif min_total_time_indices_list_len == 2:
                        min_total_time_indices_list = get_minvalue(total_time_list)
                        min_total_time_indices_list_len = len(min_total_time_indices_list)
                        for x in min_total_time_indices_list:
                            if( (total_time_list[x] != "2880:00.000") ):
                                if( (total_time_list[x] == "1440:00.000") ):
                                    scoreboard_display[x]["POS"] = "-"
                                else:
                                    scoreboard_display[x]["POS"] = f"{st.session_state.award_3rd_emoji}"
                                    total_time_list[x] = showTime(172800)  # fake 48h time

    # award for best lap / best bonus target score                        
                if(len(best_lap_list) == scoreboard_len): # all players finished race
                    min_best_lap_indices_list = get_minvalue(best_lap_list)
                    for x in range(len(best_lap_list)):
                        if x in min_best_lap_indices_list:
                            if( (best_lap_list[x] != "1440:00.000") ):
                                scoreboard_display[x]["BEST ROUND"] = f"{st.session_state.award_bonus_emoji}"
                            else:
                                scoreboard_display[x]["BEST ROUND"] = "-"
                        else:
                            scoreboard_display[x]["BEST ROUND"] = "-"

                if(len(total_score_list) == scoreboard_len): # all players finished race    
                    max_total_score_indices_list = get_maxvalue(total_score_list)
                    max_total_score_indices_list_len = len(max_total_score_indices_list)
    # handle normal case: one player on 1st place
                    for x in max_total_score_indices_list:
                        scoreboard_display[x]["POS"] = f"{st.session_state.award_1st_emoji}"
                        total_score_list[x] = 0  # fake 0 score - meaning player has been handled
    # cont. handle normal case: one player on 2nd place as well as special case more players on 2nd place
                    if max_total_score_indices_list_len == 1:
                        max_total_score_indices_list = get_maxvalue(total_score_list)
                        max_total_score_indices_list_len = len(max_total_score_indices_list)
                        for x in max_total_score_indices_list:
                            scoreboard_display[x]["POS"] = f"{st.session_state.award_2nd_emoji}"
                            total_score_list[x] = 0  # fake 0 score - meaning player has been handled
    # cont. handle normal case: one player on 3rd place as well as special case more players on 3rd place
                    if max_total_score_indices_list_len == 1:
                        max_total_score_indices_list = get_maxvalue(total_score_list)
                        max_total_score_indices_list_len = len(max_total_score_indices_list)
                        for x in max_total_score_indices_list:
                            scoreboard_display[x]["POS"] = f"{st.session_state.award_3rd_emoji}"
                            total_score_list[x] = 0  # fake 0 score - meaning player has been handled
    # handle special case: two players on 1st place as well as special case more players on 3rd place                                   
                    elif max_total_score_indices_list_len == 2:
                        max_total_score_indices_list = get_maxvalue(total_score_list)
                        max_total_score_indices_list_len = len(max_total_score_indices_list)
                        for x in max_total_score_indices_list:
                            scoreboard_display[x]["POS"] = f"{st.session_state.award_3rd_emoji}"
                            total_score_list[x] = 0  # fake 0 score - meaning player has been handled

                if(len(best_target_list) == scoreboard_len): # all players finished race
                    max_best_target_indices_list = get_maxvalue(best_target_list)
                    for x in range(len(best_target_list)):
                        if x in max_best_target_indices_list:
                            scoreboard_display[x]["BONUS TARGET"] = f"{st.session_state.award_bonus_emoji}"
                        else:
                            scoreboard_display[x]["BONUS TARGET"] = "-"

    # award for shortest distance                        
                if(len(shortest_distance_list) == scoreboard_len): # all players finished race
                    min_shortest_distance_list_indices_list = get_minvalue(shortest_distance_list)
                    for x in range(len(shortest_distance_list)):
                        if x in min_shortest_distance_list_indices_list:
                            if( (shortest_distance_list[x] != "9999km 999m") ):
                                scoreboard_display[x]["SHORTEST DISTANCE"] = f"{st.session_state.award_bonus_emoji}"
                            else:
                                scoreboard_display[x]["SHORTEST DISTANCE"] = "-"
                        else:
                            scoreboard_display[x]["SHORTEST DISTANCE"] = "-"

            df = pd.DataFrame( scoreboard_display )
            df = df.style.set_properties(**{
                'font-size': '25pt',
                'font-family': 'IBM Plex Mono',
            })

#            st.dataframe(df)
            st.table(df)

        with placeholder4.container():
        
            def constructDetailedEntry(r:dict,last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time, section_condition, user_name, sum_score):
                
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

            for player in range(len(scoreboard_data)):

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
                    (targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition,sum_score) = constructDetailedEntry(targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"],sum_score)
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
                    targetboard_data.append(constructDetailedEntry({},last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"], sum_score)[0])

                detailed_df = pd.DataFrame( targetboard_data ) 

                model = get_model(scoreboard_data[player]["enter_data"]["engine_type"],scoreboard_data[player]["enter_data"]["tuning_type"])
                tuning = get_tuning(scoreboard_data[player]["enter_data"]["tuning_type"])
               
#                with st.expander(str(scoreboard_data[player]["user_name"]) + " (" + str(model) + " | " + str(tuning) + f") Config. {st.session_state.show_game_emoji}", expanded=False):
                with st.expander("Detailed Statistics of " + str(scoreboard_data[player]["user_name"]) + " (" + str(model) + " | " + str(tuning) + f") {st.session_state.show_game_emoji}", expanded=False):
                
                    game_mode = get_app_game_mode(scoreboard_data[player]["enter_data"]["game_mode"])
                    starttime = get_starttime(scoreboard_data[player]["enter_data"]["start_time"])
                    laps_app = scoreboard_data[player]["enter_data"]["lap_count"]
                    track_cond = get_track_cond(scoreboard_data[player]["enter_data"]["track_condition"])
                    track_bundle = get_track_bundle(scoreboard_data[player]["enter_data"]["track_bundle"])
                    wheels = get_wheels(scoreboard_data[player]["enter_data"]["wheels"])
                    setup = get_setup(scoreboard_data[player]["enter_data"]["setup_mode"])
                    s_angle = int(scoreboard_data[player]["enter_data"]["steering_angle"])
                    soft_s = get_bool(scoreboard_data[player]["enter_data"]["softsteering"])
                    drift_a = get_bool(scoreboard_data[player]["enter_data"]["driftassist"])

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
                        
                    col31, col32, col33, col34 = st.columns(4)
                    with col31:
                        st.markdown("**LAPS (IN APP):**")
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

                    col81, col82, col83, col84 = st.columns(4)
                    with col81:
                        st.markdown("**MODEL:**")
                    with col82:
                        st.markdown(str(model)) 

                    col91, col92, col93, col94 = st.columns(4)
                    with col91:
                        st.markdown("**TUNING:**")
                    with col92:
                        st.markdown(str(tuning)) 

                    col101, col102, col103, col104 = st.columns(4)
                    with col101:
                        st.markdown("**STEERING ANGLE:**")
                    with col102:
                        st.markdown(str(s_angle)) 

                    col111, col112, col113, col114 = st.columns(4)
                    with col111:
                        st.markdown("**SOFT STEERING:**")
                    with col112:
                        st.markdown(str(soft_s)) 

                    col121, col122, col123, col124 = st.columns(4)
                    with col121:
                        st.markdown("**DRIFT ASSISTANT:**")
                    with col122:
                        st.markdown(str(drift_a)) 

#                    st.dataframe(detailed_df)
                    st.table(detailed_df)

        time.sleep(0.5)

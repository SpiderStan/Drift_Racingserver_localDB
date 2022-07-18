import streamlit as st
import time
#import socket
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

    st.subheader("Game Statistics of Event " + str(game_id) + " from Lobby " + str(lobby_id))

    games = []
    joker_lap_code = [None] * 20
    scoreboard = []
    track_image_upload = []
    track_image = []
    
    next_race = st.empty()
    placeholder1 = st.empty()
    placeholder2 = st.empty()

    with placeholder1.container():
        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns(9)

        with col1:
            if st.button(f"Back {st.session_state.back_emoji}"):
                st.session_state.nextpage = "main_page"
                st.session_state.game_track_images_set = [False] * 20
                st.session_state.game_track_images = [None] * 20
                next_race.empty()
                placeholder1.empty()
                placeholder2.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col2:
            if st.button(f"Start in 1 Min. {st.session_state.driving_emoji}"):
                result = fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/start_stage/{lobby_id}/{game_id}/{stage_id}")
                st.session_state.new_stage_event = False
                next_race.empty()
                placeholder1.empty()
                placeholder2.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col3:
            if st.button(f"Rem. Player (Stage) {st.session_state.remove_emoji}"):
                st.session_state.nextpage = "remove_player_from_stage_part1"
                next_race.empty()
                placeholder1.empty()
                placeholder2.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col4:
            if st.button(f"Reset Stage {st.session_state.reset_emoji}"):
                st.session_state.nextpage = "reset_stage"
                next_race.empty()
                placeholder1.empty()
                placeholder2.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col5:
            if st.button(f"Rem. Player (Event) {st.session_state.remove_emoji}"):
                st.session_state.nextpage = "remove_player_from_race"
                next_race.empty()
                placeholder1.empty()
                placeholder2.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col6:
            if st.button(f"Reset Event {st.session_state.reset_emoji}"):
                result = fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/reset/{lobby_id}/{game_id}/{stage_id}")
                st.session_state.new_stage_event = False
                next_race.empty()
                placeholder1.empty()
                placeholder2.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col7:
            if st.button(f"Download Data {st.session_state.download_emoji}"):
                st.session_state.nextpage = "download_stagerace"
                next_race.empty()
                placeholder1.empty()
                placeholder2.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col8:
            if st.button(f"Detailed Statistics {st.session_state.statistics_emoji}"):
                st.session_state.nextpage = "statistics_stage"
                st.session_state.game_track_images_set = game_track_images_set
                st.session_state.game_track_images = game_track_images
                next_race.empty()
                placeholder1.empty()
                placeholder2.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col9:
            if st.button(f"Delete Event {st.session_state.delete_emoji}"):
                result = fetch_delete(f"{settings.driftapi_path}/driftapi/manage_game/delete/{lobby_id}/{game_id}")
                st.session_state.game_id = None
                st.session_state.stage_id = 1
                st.session_state.num_stages = 1
                st.session_state.nextpage = "main_page"
                st.session_state.game_track_images_set = [False] * 20
                st.session_state.game_track_images = [None] * 20
                next_race.empty()
                placeholder1.empty()
                placeholder2.empty()
                time.sleep(0.1)
                st.experimental_rerun()

    with placeholder2.container():
        for x in range(num_stages):
            game = getGameInfo(lobby_id, game_id, x+1)
            if not game:
                st.error("No Game with that id exists, going back to main menu...")
                time.sleep(1)
                st.session_state.nextpage = "main_page"
                st.experimental_rerun()
            if game:
                with st.expander(f"Game Statistics of Sage " + str(x+1) + " - " + str(game["game_mode"]) + " - Join the game via URL: http://"+str(st.session_state.ip_address)+":8001/driftapi/game/"+str(lobby_id)+"/"+str(x+1)+" and GAME ID: "+str(game_id) + "   " + str(game["track_id"]) +  f"{st.session_state.show_game_emoji}", expanded = False):

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

                    track_image.append(st.empty())

                    track_image_upload.append(st.file_uploader("Here you can upload the track layout", type=['png', 'jpg'], accept_multiple_files=False, key="The track layout upload of " + str(x+1), help=None, on_change=None, args=None, kwargs=None, disabled=False))

                    if(game_track_images_set[x] == False): # no track image upload so far
                        if(track_image_upload[x] != None): # user has supplied a track image
                            game_track_images_set[x] = True
                            track_image[x].image(track_image_upload[x], caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto") # Show Uploaded Track Image
                            game_track_images[x] = track_image_upload[x] # store in session state
                    elif(game_track_images_set[x] == True): # track image existing
                        if(track_image_upload[x] != None): # user has supplied a new track image
                            game_track_images_set[x] = True
                            track_image[x].image(track_image_upload[x], caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto") # Show Uploaded Track Image
                            game_track_images[x] = track_image_upload[x] # store in session state
                        else:
                            track_image[x].image(game_track_images[x], caption=None, width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto") # Show Prev. Uploaded Track Image
                    if st.button(f"Remove Image {st.session_state.remove_emoji}", key="Remove Image "+str(x+1)):
                        track_image[x].empty()
                        game_track_images_set[x] = False

                    submitUri:str = "http://"+str(st.session_state.ip_address)+":8001/driftapi/game/"+str(lobby_id)+"/"+str(stage_id)+"/"
                    st.image(getqrcode(submitUri), clamp=True)
                    st.write("URL: "+submitUri)
                    st.write("GAME ID: "+game_id)

                scoreboard.append(st.empty())
                
                if "joker_lap_code" in game:
                    joker_lap_code[x] = game["joker_lap_code"]
                    
            games.append(game)
 
    while True:

        # getting the info from one stage only is ok, since all stages have the same start_time
        game = getGameInfo(lobby_id, game_id, stage_id)
        current_time = datetime.now().astimezone(timezone.utc)
        if (st.session_state.new_stage_event == True):
            start_time = datetime.strptime(game["start_time"],'%Y-%m-%dT%H:%M:%S%z')
        else:
            try:
                start_time = datetime.strptime(game["start_time"],'%Y-%m-%d %H:%M:%S.%f%z')
            except:
                start_time = datetime.strptime(game["start_time"],'%Y-%m-%dT%H:%M:%S%z')
        time_delay = start_time - current_time
        if(current_time <= start_time):
            next_race.text("Stage starts in approx. " + str(time_delay))
        else:
            next_race.text("Time elapsed! Please press Button 'Start in 1 Min.' or 'Reset Event' and Sync. in Sturmkind App before entering a Stage")

        scoreboard_data = []
        scoreboard_len = []
        
        for x in range(num_stages):

            with scoreboard[x].container():
        
                scoreboard_data.append(getScoreBoard(lobby_id, game_id, x+1))
                
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
                    if ( games[x]["game_mode"] == "RACE" ):

# handle laps_completed:
                        if "enter_data" in r:
                            d["LAPS"] = r["laps_completed"]
                        else:
                            d["LAPS"] = "-"

                        if joker_lap_code[x] != None:
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

                    elif ( games[x]["game_mode"] == "GYMKHANA" ):
                        display_text_speed = f"BEST SPEED"
                        display_text_angle = f"BEST ANGLE"
                        display_text_360 = f"BEST 360"
                        display_text_180 = f"BEST 180"
# handle bonus target set:
                        if ( "bonus_target" in games[x] ) and (not games[x]["bonus_target"] is None):
                            if ( games[x]["bonus_target"] == "SPEED" ):
                                display_text_speed = display_text_speed + f" ({st.session_state.award_trophy_emoji})"
                            elif ( games[x]["bonus_target"] == "ANGLE" ):
                                display_text_angle = display_text_angle + f" ({st.session_state.award_trophy_emoji})"
                            elif ( games[x]["bonus_target"] == "360" ):
                                display_text_360 = display_text_360 + f" ({st.session_state.award_trophy_emoji})"
                            elif ( games[x]["bonus_target"] == "180" ):
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
                        if ( ( "end_data" in r ) and not ( r["end_data"] is None ) ):
                        
                            if ( "bonus_target" in games[x] ) and (not games[x]["bonus_target"] is None):
                                if ( games[x]["bonus_target"] == "SPEED" ):
                                    if (not r["best_speed_drift"] is None):
                                        best_target_set = int(r["best_speed_drift"])
                                    else:
                                        best_target_set = 0
                                elif ( games[x]["bonus_target"] == "ANGLE" ):
                                    if (not r["best_angle_drift"] is None):
                                        best_target_set = int(r["best_angle_drift"])
                                    else:
                                        best_target_set = 0
                                elif ( games[x]["bonus_target"] == "360" ):
                                    if (not r["best_360_angle"] is None):
                                        best_target_set = int(r["best_360_angle"])
                                    else:
                                        best_target_set = 0
                                elif ( games[x]["bonus_target"] == "180" ):
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
                (scoreboard_data[x]) = [constructEntry(r) for r in scoreboard_data[x] if (type(r) is dict)] # we have to handle up to 10 scoreboards

                #if there is no entry, just add an empty one by calling the construct Entry with an empty dict
                while len(scoreboard_data[x])<1:
                    scoreboard_data[x].append(constructEntry({}))

                scoreboard_len.append(len(scoreboard_data[x]))
                
                if(len(total_time_list) == scoreboard_len[x]): # all players finished race    
                    min_total_time_indices_list = get_minvalue(total_time_list)
                    min_total_time_indices_list_len = len(min_total_time_indices_list)
# handle normal case: one player on 1st place
                    for y in min_total_time_indices_list:
                        if( (total_time_list[y] != "1440:00.000") ):
                            scoreboard_data[x][y]["POS"] = f"{st.session_state.award_1st_emoji}"
                            total_time_list[y] = showTime(172800)  # fake 48h time - meaning player has been handled
                        else:
                            scoreboard_data[x][y]["POS"] = "-"
# cont. handle normal case: one player on 2nd place as well as special case more players on 2nd place
                    if min_total_time_indices_list_len == 1:
                        min_total_time_indices_list = get_minvalue(total_time_list)
                        min_total_time_indices_list_len = len(min_total_time_indices_list)
                        for y in min_total_time_indices_list:
                            if( (total_time_list[y] != "2880:00.000") ):
                                if( (total_time_list[y] == "1440:00.000") ):
                                    scoreboard_data[x][y]["POS"] = "-"
                                else:
                                    scoreboard_data[x][y]["POS"] = f"{st.session_state.award_2nd_emoji}"
                                    total_time_list[y] = showTime(172800)  # fake 48h time - meaning player has been handled
# cont. handle normal case: one player on 3rd place as well as special case more players on 3rd place
                        if min_total_time_indices_list_len == 1:
                            min_total_time_indices_list = get_minvalue(total_time_list)
                            min_total_time_indices_list_len = len(min_total_time_indices_list)
                            for y in min_total_time_indices_list:
                                if( (total_time_list[y] != "2880:00.000") ):
                                    if( (total_time_list[y] == "1440:00.000") ):
                                        scoreboard_data[x][y]["POS"] = "-"
                                    else:
                                        scoreboard_data[x][y]["POS"] = f"{st.session_state.award_3rd_emoji}"
                                        total_time_list[y] = showTime(172800)  # fake 48h time
# handle special case: two players on 1st place as well as special case more players on 3rd place                                   
                    elif min_total_time_indices_list_len == 2:
                        min_total_time_indices_list = get_minvalue(total_time_list)
                        min_total_time_indices_list_len = len(min_total_time_indices_list)
                        for y in min_total_time_indices_list:
                            if( (total_time_list[y] != "2880:00.000") ):
                                if( (total_time_list[y] == "1440:00.000") ):
                                    scoreboard_data[x][y]["POS"] = "-"
                                else:
                                    scoreboard_data[x][y]["POS"] = f"{st.session_state.award_3rd_emoji}"
                                    total_time_list[y] = showTime(172800)  # fake 48h time

# award for best lap / best bonus target score                        
                if(len(best_lap_list) == scoreboard_len[x]): # all players finished race
                    min_best_lap_indices_list = get_minvalue(best_lap_list)
                    for y in range(len(best_lap_list)):
                        if y in min_best_lap_indices_list:
                            if( (best_lap_list[y] != "1440:00.000") ):
                                scoreboard_data[x][y]["BEST ROUND"] = f"{st.session_state.award_bonus_emoji}"
                            else:
                                scoreboard_data[x][y]["BEST ROUND"] = "-"
                        else:
                            scoreboard_data[x][y]["BEST ROUND"] = "-"

                if(len(total_score_list) == scoreboard_len[x]): # all players finished race    
                    max_total_score_indices_list = get_maxvalue(total_score_list)
                    max_total_score_indices_list_len = len(max_total_score_indices_list)
# handle normal case: one player on 1st place
                    for y in max_total_score_indices_list:
                        scoreboard_data[x][y]["POS"] = f"{st.session_state.award_1st_emoji}"
                        total_score_list[y] = 0  # fake 0 score - meaning player has been handled
# cont. handle normal case: one player on 2nd place as well as special case more players on 2nd place
                    if max_total_score_indices_list_len == 1:
                        max_total_score_indices_list = get_maxvalue(total_score_list)
                        max_total_score_indices_list_len = len(max_total_score_indices_list)
                        for y in max_total_score_indices_list:
                            scoreboard_data[x][y]["POS"] = f"{st.session_state.award_2nd_emoji}"
                            total_score_list[y] = 0  # fake 0 score - meaning player has been handled
# cont. handle normal case: one player on 3rd place as well as special case more players on 3rd place
                    if max_total_score_indices_list_len == 1:
                        max_total_score_indices_list = get_maxvalue(total_score_list)
                        max_total_score_indices_list_len = len(max_total_score_indices_list)
                        for y in max_total_score_indices_list:
                            scoreboard_data[x][y]["POS"] = f"{st.session_state.award_3rd_emoji}"
                            total_score_list[y] = 0  # fake 0 score - meaning player has been handled
# handle special case: two players on 1st place as well as special case more players on 3rd place                                   
                    elif max_total_score_indices_list_len == 2:
                        max_total_score_indices_list = get_maxvalue(total_score_list)
                        max_total_score_indices_list_len = len(max_total_score_indices_list)
                        for y in max_total_score_indices_list:
                            scoreboard_data[x][y]["POS"] = f"{st.session_state.award_3rd_emoji}"
                            total_score_list[y] = 0  # fake 0 score - meaning player has been handled

                if(len(best_target_list) == scoreboard_len[x]): # all players finished race
                    max_best_target_indices_list = get_maxvalue(best_target_list)
                    for y in range(len(best_target_list)):
                        if y in max_best_target_indices_list:
                            scoreboard_data[x][y]["BONUS TARGET"] = f"{st.session_state.award_bonus_emoji}"
                        else:
                            scoreboard_data[x][y]["BONUS TARGET"] = "-"

# award for shortest distance                        
                if(len(shortest_distance_list) == scoreboard_len[x]): # all players finished race
                    min_shortest_distance_list_indices_list = get_minvalue(shortest_distance_list)
                    for y in range(len(shortest_distance_list)):
                        if y in min_shortest_distance_list_indices_list:
                            if( (shortest_distance_list[y] != "9999km 999m") ):
                                scoreboard_data[x][y]["SHORTEST DISTANCE"] = f"{st.session_state.award_bonus_emoji}"
                            else:
                                scoreboard_data[x][y]["SHORTEST DISTANCE"] = "-"
                        else:
                            scoreboard_data[x][y]["SHORTEST DISTANCE"] = "-"

                df = pd.DataFrame( scoreboard_data[x] )
                df = df.style.set_properties(**{
                    'font-size': '25pt',
                    'font-family': 'IBM Plex Mono',
                })

                st.table(df)

        time.sleep(0.5)

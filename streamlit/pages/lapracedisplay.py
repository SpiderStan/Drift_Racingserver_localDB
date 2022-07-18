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
from .helper import get_model, get_tuning, get_app_game_mode, get_starttime, get_track_cond, get_track_bundle, get_wheels, get_setup, get_joker_lap_code, get_bool, handleCurrentTrackCondition, getGameInfo, getScoreBoard, getDetailedTargetData, showTime, showDistance, showMeanSpeed

def highlight_min(data, color='green'):
    is_min = data == data.min().min()
    return pd.DataFrame(np.where(is_min, attr, ''), index=data.index, columns=data.columns)

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

def get_min_race_time_value(inputlist):
    #get the minimum value in the list
    try:
        min_value = min([x for x in inputlist if x != timedelta(int(0))])
    except:
        res = []
        return res
    #return the index of minimum value
    res = [i for i,val in enumerate(inputlist) if val==min_value]
    return res

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
    #return the index of maximum value 
    res = [i for i,val in enumerate(inputlist) if val==max_value]
    return res

def get_truevalue(inputlist):
    res = [i for i, val in enumerate(inputlist) if val==True]
    return res

def get_nonevalue(inputlist):
    res = [i for i, val in enumerate(inputlist) if val==None]
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

    game = getGameInfo(lobby_id, game_id, stage_id)

    if not game:
        st.error("No Game with that id exists, going back to main menu...")
        time.sleep(1)
        st.session_state.nextpage = "main_page"
        st.experimental_rerun()
 
    st.subheader("Lap Race " + str(game_id) + " in Lobby " + str(lobby_id) + " with " + str(game["lap_count"]) + " laps")

    next_race = st.empty()

    joker_lap_code = None
    if game:
        if "joker_lap_code" in game:
            joker_lap_code = game["joker_lap_code"]

    placeholder0 = st.empty()
    scoreboard = st.empty()
    placeholder1 = st.empty()
    placeholder2 = st.empty()
    placeholder3 = st.empty()

    with placeholder0.container():  
        
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

        with col1:
            if st.button(f"Back {st.session_state.back_emoji}"):
                st.session_state.nextpage = "main_page"
                st.session_state.game_track_images_set = False
                st.session_state.game_track_images = None
                next_race.empty()
                placeholder0.empty()
                scoreboard.empty()
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col2:
            if st.button(f"Start in 1 Min. {st.session_state.driving_emoji}"):
                result = fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/start_stage/{lobby_id}/{game_id}/{stage_id}")
                st.session_state.new_game = False
                next_race.empty()
                placeholder0.empty()
                scoreboard.empty()
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                time.sleep(0.1)
                st.experimental_rerun()
                        
        with col3:
            if st.button(f"Remove Player {st.session_state.remove_emoji}"):
                st.session_state.nextpage = "remove_player_from_race"
                st.session_state.game_track_images_set = game_track_images_set
                st.session_state.game_track_images = game_track_images
                next_race.empty()
                placeholder0.empty()
                scoreboard.empty()
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col4:
            if st.button(f"Reset Game {st.session_state.reset_emoji}"):
                result = fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/reset/{lobby_id}/{game_id}/{stage_id}")
                st.session_state.new_game = False
                next_race.empty()
                placeholder0.empty()
                scoreboard.empty()
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col5:
            if st.button(f"Download Data {st.session_state.download_emoji}"):
                st.session_state.nextpage = "download_laprace"
                st.session_state.game_track_images_set = game_track_images_set
                st.session_state.game_track_images = game_track_images
                next_race.empty()
                placeholder0.empty()
                scoreboard.empty()
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with col6:
            if st.button(f"Delete Game {st.session_state.delete_emoji}"):
                result = fetch_delete(f"{settings.driftapi_path}/driftapi/manage_game/delete/{lobby_id}/{game_id}")
                st.session_state.game_id = None
                st.session_state.stage_id = 1
                st.session_state.num_stages = 1
                st.session_state.game_track_images_set = False
                st.session_state.game_track_images = None
                st.session_state.nextpage = "main_page"
                next_race.empty()
                placeholder0.empty()
                scoreboard.empty()
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                time.sleep(0.1)
                st.experimental_rerun()

    with placeholder1.container():  
        with st.expander(f"Game Settings {st.session_state.show_game_emoji} - Join the game via URL: http://"+str(st.session_state.ip_address)+":8001/driftapi/game/"+str(lobby_id)+"/"+str(stage_id)+" and GAME ID: "+str(game_id), expanded=False):

            game_mode = get_game_mode(game["game_mode"])
            starttime = get_starttime(game["start_time"])
            laps_app = int(game["lap_count"])
            track_cond = get_track_cond(game["track_condition"])
            track_bundle = get_track_bundle(game["track_bundle"])
            wheels = get_wheels(game["wheels"])
            setup = get_setup(game["setup_mode"])
            
            if ( ("joker_lap_code" in game) and not ( game["joker_lap_code"] is None) ):
                joker_lap_code = get_joker_lap_code(game["joker_lap_code"])
                if ( ("joker_lap_precondition_code" in game) and not ( game["joker_lap_precondition_code"] is None) ):
                    joker_lap_precondition_code = get_joker_lap_code(game["joker_lap_precondition_code"])
             
            num_sectors = int(game["num_sectors"])

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

            col121, col122, col123, col124 = st.columns(4)
            with col121:
                st.markdown("**NUM SECTORS:**")
            with col122:
                st.markdown(str(num_sectors)) 

            submitUri:str = "http://"+str(st.session_state.ip_address)+":8001/driftapi/game/"+str(lobby_id)+"/"+str(stage_id)
            st.image(getqrcode(submitUri), clamp=True)
            st.write("URL: "+submitUri)
            st.write("GAME ID: "+game_id)

    with placeholder2.container():  
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

        if ( ( "start_time" in game ) and not ( game["start_time"] is None ) ):
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

        with scoreboard.container():
        
            scoreboard_data = getScoreBoard(lobby_id, game_id, stage_id)
            scoreboard_data_len = len(scoreboard_data)

            # CSS to inject contained in a string
            hide_dataframe_row_index = """
                        <style>
                        .row_heading.level0 {display:none}
                        .blank {display:none}
                        </style>
            """
            # Inject CSS with Markdown
            st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)
                    
            def constructEntry(r:dict, player_index, player_finished, player_finished_indices_list, player_finished_timestamp):

                d = {}
                
                #default value
                player_false_start = False

                if "user_name" in r:
                    if ( ( "end_data" in r ) and not ( r["end_data"] is None ) ):
                        if(r["end_data"]["false_start"]):
                            player_status = f"{st.session_state.false_start_emoji}" #"False Start!"
                        else:
                            player_status = f"{st.session_state.finish_emoji}" #"Finished"
                    elif ( ( "start_data" in r ) and not ( r["start_data"] is None ) ):
                        current_track_condition = handleCurrentTrackCondition(r)
                        if(r["laps_completed"] == r["enter_data"]["lap_count"]):
                            player_status = f"{st.session_state.finish_emoji}" #"Finished - Player completed all rounds"
                        else:
                            player_status = current_track_condition #Driving - show Track Condition here
                    elif "enter_data" in r:
                        player_status = f"{st.session_state.ready_emoji}" #"Ready"
                    else:
                        player_status = ""                    
                    d["DRIVER"] = r["user_name"]
                    d[f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] =  player_status
                else:
                    d["DRIVER"] = ""
                    d[f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] =  "-"

                if (player_finished == True):
# determine number of rounds and sector count based on target data and player_finished_timestamp
                    targetboard_data = getDetailedTargetData(lobby_id, game_id, stage_id, r["user_name"]) # get all targets of the player 
                    targetboard_data = (sorted(targetboard_data, key=operator.itemgetter('target_ctr')))
                    targetboard_data_len = len(targetboard_data)
                    
                    round_cnt = 0
                    sector_cnt = 0
                    if(targetboard_data_len>0):
                        for x in range(targetboard_data_len):
                            
                            if(targetboard_data[x]["target_data"]["false_start"] == True):
                                player_false_start = True
                        
                            if (targetboard_data[x]["target_data"]["crossing_time"] < player_finished_timestamp):
                            
                                current_time = datetime.now().astimezone(timezone.utc) 
                                start_time = datetime.strptime(r["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                                player_race_time = current_time - start_time 

                                if(targetboard_data[x]["target_data"]["target_code"] == 0):
                                    round_cnt+=1
                                    sector_cnt = 1
                                else:
                                    sector_cnt+=1
                            else:
                                if(targetboard_data[x]["target_data"]["target_code"] == 0):
                                    round_cnt+=1
                                    sector_cnt = game["num_sectors"]
                                    player_race_time = datetime.strptime(r["last_lap_timestamp"], '%Y-%m-%dT%H:%M:%S.%f').astimezone(timezone.utc) - datetime.strptime(r["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                                    d[f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] = f"{st.session_state.finish_emoji}" #"Finished"
                                    break
                                else:
                                    sector_cnt+=1
                                    
                                    current_time = datetime.now().astimezone(timezone.utc) 
                                    start_time = datetime.strptime(r["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                                    player_race_time = current_time - start_time
                    elif ( ( "start_data" in r ) and not ( r["start_data"] is None ) ):
                        current_time = datetime.now().astimezone(timezone.utc)
                        start_time = datetime.strptime(r["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                        player_race_time = current_time - start_time
                    else:
                        player_race_time = timedelta(seconds=int(0)) # fake 0 seconds

                    if(round_cnt>0):
                        d["LAPS"] = str(round_cnt-1)
                    else:
                        d["LAPS"] = str(0)
                    d["SECTOR"] = str(sector_cnt)
                    
                    if(round_cnt>0):
                        current_rounds_and_sectors_list[0].append(round_cnt-1)
                    else:
                        current_rounds_and_sectors_list[0].append(0)
                    current_rounds_and_sectors_list[1].append(sector_cnt)
                    
                else:
                    if "user_name" in r:

                        if ( ( "start_data" in r ) and not ( r["start_data"] is None ) ):
                            current_time = datetime.now().astimezone(timezone.utc)
                            start_time = datetime.strptime(r["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                            player_race_time = current_time - start_time
                        else:
                            player_race_time = timedelta(seconds=int(0)) # fake 0 seconds
                    
                        if ( ( "end_data" in r ) and not ( r["end_data"] is None ) ):
                            if(r["end_data"]["false_start"]):
                                completed_sectors_cnt = 0
                            else:
                                completed_sectors_cnt = 0
                        elif ( ( "start_data" in r ) and not ( r["start_data"] is None ) ):
                            if(r["last_recognized_target"] == 0): # start/finish
                                if(r["laps_completed"] == r["enter_data"]["lap_count"]):
                                    completed_sectors_cnt = game["num_sectors"]
                                else:
                                    completed_sectors_cnt = 1
                            elif(r["second_last_recognized_target"] == 0):
                                completed_sectors_cnt = 2
                            elif(r["third_last_recognized_target"] == 0):
                                completed_sectors_cnt = 3
                            elif(r["forth_last_recognized_target"] == 0):
                                completed_sectors_cnt = 4
                            elif(r["fith_last_recognized_target"] == 0):
                                completed_sectors_cnt = 5
                            elif(r["sixth_last_recognized_target"] == 0):
                                completed_sectors_cnt = 6
                            elif(r["seventh_last_recognized_target"] == 0):
                                completed_sectors_cnt = 7
                            elif(r["eighth_last_recognized_target"] == 0):
                                completed_sectors_cnt = 8
                            elif(r["ninth_last_recognized_target"] == 0):
                                completed_sectors_cnt = 9
                            else:
                                completed_sectors_cnt = 0
                        elif "enter_data" in r:
                            completed_sectors_cnt = 0
                        else:
                            completed_sectors_cnt = 0  
# handle laps:
                    if "enter_data" in r:
                        if ( ( "end_data" in r ) and not ( r["end_data"] is None ) ): # EndEvent
                            if ( r["enter_data"]["lap_count"] == r["laps_completed"]): # finished Race (all laps completed)
                                d["LAPS"] = str(r["laps_completed"])
                            else: # not all laps completed
                                d["LAPS"] = str(r["laps_completed"])
                        elif ( ( "start_data" in r ) and not ( r["start_data"] is None ) ): # driving
                            if( r["target_code_counter"]["0"] == 0 ): # player not driven over start/finish so far
                                d["LAPS"] = str(0)
                            elif( r["enter_data"]["lap_count"] == r["laps_completed"]):
                                d["LAPS"] = str(r["laps_completed"])
                            else: # player driven over start/finish
                                d["LAPS"] = str(r["laps_completed"])
                        elif "enter_data" in r: #"Ready"
                            d["LAPS"] = str(0)
                    else:       
                        d["LAPS"] = ""

                    if "num_sectors" in game:
                        if "enter_data" in r:
                            if ( ( "end_data" in r ) and not ( r["end_data"] is None ) ):
                                d["SECTOR"] = str(completed_sectors_cnt)
                            elif(r["laps_completed"] == r["enter_data"]["lap_count"]):
                                d["SECTOR"] = str(game["num_sectors"])
                            else:
                                d["SECTOR"] = str(completed_sectors_cnt)
                        else:
                            d["SECTOR"] = str(completed_sectors_cnt)

                    current_rounds_and_sectors_list[0].append(r["laps_completed"])
                    current_rounds_and_sectors_list[1].append(completed_sectors_cnt)

                return (d,player_race_time,player_false_start)

            racedisplay_data = [{}] * scoreboard_data_len            
            current_rounds_and_sectors_list = [[],[]]

            player_finished_list = []
            player_race_time_list = []
            for x in range(scoreboard_data_len): # number of players
                if (scoreboard_data[x]["laps_completed"] == game["lap_count"]): # check if one or more player finished lap race and calc race time
                    player_finished_list.append(True)
                    player_race_time_list.append((datetime.strptime(scoreboard_data[x]["last_lap_timestamp"], '%Y-%m-%dT%H:%M:%S.%f').astimezone(timezone.utc)) - (datetime.strptime(scoreboard_data[x]["start_data"]["signal_time"], '%Y-%m-%dT%H:%M:%S.%f%z')))
                else:
                    player_finished_list.append(False)
                    player_race_time_list.append(timedelta(seconds=int(0))) # fake 0 seconds
            player_finished_indices_list = get_truevalue(player_finished_list)
            player_finished_indices_list_len = len(player_finished_indices_list)
            
            if( player_finished_indices_list_len > 0 ):
                player_finished = True
            else:
                player_finished = False

            player_race_time_list_len = len(player_race_time_list)
            if(player_race_time_list_len > 0):
                player_min_race_time_indices_list = get_min_race_time_value(player_race_time_list)
                player_min_race_time_indices_list_len = len(player_min_race_time_indices_list)
                if(player_min_race_time_indices_list_len > 0):
                    player_finished_timestamp = scoreboard_data[player_min_race_time_indices_list[0]]["last_lap_timestamp"]
                else:
                    player_finished_timestamp = None

            player_false_start_list = [None] * scoreboard_data_len 

            # construct main part of racedisplay_data here
            for x in range(scoreboard_data_len): # number of players
                (racedisplay_data[x], player_race_time_list[x], player_false_start_list[x]) = constructEntry(scoreboard_data[x], x, player_finished, player_finished_indices_list, player_finished_timestamp)

            if(scoreboard_data_len >= 1):

                for x in range(scoreboard_data_len): # number of players
# first signal players disqualified due to false start (even if engine is still running)
                    if(player_false_start_list[x] == True):
                        racedisplay_data[x]["DRIVER"] = scoreboard_data[x]["user_name"] + f"{st.session_state.false_start_emoji}"
                
                    if(racedisplay_data[x][f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] == f"{st.session_state.finish_emoji}"):
                        player_finished_list[x] = True
                    elif(racedisplay_data[x][f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] == f"{st.session_state.false_start_emoji}"):
                        player_finished_list[x] = True
                    else:
                        player_finished_list[x] = False
                
                player_finished_indices_list = get_truevalue(player_finished_list)
                player_finished_indices_list_len = len(player_finished_indices_list)
                
                handled_players = 0
                handled_finished_players = 0
                position = 1

                if(handled_players < scoreboard_data_len):

                    best_player_handled = False

# second handle players already finished here
                    while handled_finished_players < player_finished_indices_list_len:
                        shortest_race_time_indices_list = get_min_race_time_value(player_race_time_list)
                        shortest_race_time_indices_list_len = len(shortest_race_time_indices_list)

                        for x in range(shortest_race_time_indices_list_len):
                            racedisplay_data[shortest_race_time_indices_list[x]]["POS"] = str(position)
                            if(best_player_handled == False):
                                racedisplay_data[shortest_race_time_indices_list[x]]["TIME"] = showTime(player_race_time_list[shortest_race_time_indices_list[x]].total_seconds())
                                best_time = player_race_time_list[shortest_race_time_indices_list[x]]
                                best_player_handled = True
                            else:
                                racedisplay_data[shortest_race_time_indices_list[x]]["TIME"] = showTime(best_time.total_seconds()) + " + " + showTime((player_race_time_list[shortest_race_time_indices_list[x]]-best_time).total_seconds()) #"+ " + str(datetime.strptime(scoreboard_data[shortest_race_time_indices_list[x]]["last_lap_timestamp"],'%Y-%m-%dT%H:%M:%S.%f') - datetime.strptime(player_finished_timestamp,'%Y-%m-%dT%H:%M:%S.%f'))
                            current_rounds_and_sectors_list[0][shortest_race_time_indices_list[x]] = -1 # fake -1 rounds - meaning player has been handled
                            handled_finished_players+=1
                            player_race_time_list[shortest_race_time_indices_list[x]] = timedelta(seconds=int(0)) # fake 0 seconds
                                
                        position+=1
                       
                    handled_players+=player_finished_indices_list_len

# third handle rest of players
                    while handled_players < scoreboard_data_len:
                        max_rounds_indices_list = get_maxvalue(current_rounds_and_sectors_list[0])
                        max_rounds_indices_list_len = len(max_rounds_indices_list)

                        max_round_sectors_list = []
                        for x in max_rounds_indices_list:
                            max_round_sectors_list.append(current_rounds_and_sectors_list[1][x])
                            
                        max_sectors_indices_list = get_maxvalue(max_round_sectors_list)
                        max_sectors_indices_list_len = len(max_sectors_indices_list)         

# last step: handle last_target_timestamp here for players in the same sector to find youngest time stamps
                        time_list = []
                        for x in max_sectors_indices_list:
                            if ( ( "last_target_timestamp" in scoreboard_data[x] ) and not ( scoreboard_data[x]["last_target_timestamp"] is None ) ):
                                time_list.append(datetime.strptime(scoreboard_data[x]["last_target_timestamp"],'%Y-%m-%dT%H:%M:%S.%f').astimezone(timezone.utc))
                            elif( ( "start_data" in scoreboard_data[x] ) and not ( scoreboard_data[x]["start_data"] is None ) ):
                                time_list.append(datetime.strptime(scoreboard_data[x]["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z'))
                            else:
                                time_list.append(datetime.now().astimezone(timezone.utc))

                        youngest_time_indices_list = get_minvalue(time_list)
                        youngest_time_indices_list_len = len(youngest_time_indices_list)
                            
                        for x in youngest_time_indices_list:
                            racedisplay_data[max_rounds_indices_list[max_sectors_indices_list[x]]]["POS"] = str(position)
                            if( ( "start_data" in scoreboard_data[max_rounds_indices_list[max_sectors_indices_list[x]]] ) and not ( scoreboard_data[max_rounds_indices_list[max_sectors_indices_list[x]]]["start_data"] is None ) ):
                                current_time = datetime.now().astimezone(timezone.utc) 
                                start_time = datetime.strptime(scoreboard_data[max_rounds_indices_list[max_sectors_indices_list[x]]]["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                                race_time = current_time - start_time                            
                                racedisplay_data[max_rounds_indices_list[max_sectors_indices_list[x]]]["TIME"] = showTime(race_time.total_seconds())
                            else:
                                racedisplay_data[max_rounds_indices_list[max_sectors_indices_list[x]]]["TIME"] = showTime(timedelta(seconds=int(0)).total_seconds())
                            current_rounds_and_sectors_list[0][max_rounds_indices_list[max_sectors_indices_list[x]]] = -1 # fake -1 rounds - meaning player has been handled
                            handled_players+=1

                        position+=1
                        
                racedisplay_data = (sorted(racedisplay_data, key=operator.itemgetter('POS')))
                
                if(player_finished_indices_list_len == scoreboard_data_len): # all players finished race - award ceremony can take place now
                    if(scoreboard_data_len >= 1):
                        racedisplay_data[0]["AWARD"] = f"{st.session_state.award_1st_emoji}"
                    if(scoreboard_data_len >= 2):
                        racedisplay_data[1]["AWARD"] = f"{st.session_state.award_2nd_emoji}"
                    if(scoreboard_data_len >= 3):
                        racedisplay_data[2]["AWARD"] = f"{st.session_state.award_3rd_emoji}"     

            else:
                racedisplay_data = [{"DRIVER": "-", f"{st.session_state.status_emoji} / {st.session_state.track_emoji}": "-", "LAPS": "-", "SECTOR": "-", "POS": "-", "TIME":"-"}]

            df = pd.DataFrame( racedisplay_data )
            df = df.style.set_properties(**{
                'font-size': '40pt',
                'font-family': 'IBM Plex Mono',
            })

#            df = df.style.applymap(lambda x: 'color:green;')\
#                         .applymap(lambda x: 'font-size:40pt;')\
#                         .applymap(lambda x: 'font-family:IBM Plex Mono;')\

            st.table(df)

        with placeholder3.container():

            def constructDetailedEntry(r:dict,last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time, section_condition, user_name):
                
                d_detailed = { } # new dict

                next_section_condition = section_condition

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
                            d_detailed[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = showDistance(section_distance)
                            d_detailed[f"SECTOR - {st.session_state.time_emoji}"] = showTime(section_time)
                            d_detailed[f"SECTOR - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(section_distance,section_time)
                            d_detailed[f"SECTOR - {st.session_state.track_emoji}"] = section_condition
                        else: # this occurs if after finish further targets will be crossed
                            d_detailed[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d_detailed[f"SECTOR - {st.session_state.time_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d_detailed[f"SECTOR - {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d_detailed[f"SECTOR - {st.session_state.track_emoji}"] = f"{st.session_state.false_start_emoji}"
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
                            d_detailed[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = showDistance(section_distance)
                            d_detailed[f"SECTOR - {st.session_state.time_emoji}"] = showTime(section_time)
                            d_detailed[f"SECTOR - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(section_distance,section_time)
                            d_detailed[f"SECTOR - {st.session_state.track_emoji}"] = section_condition
                        else: # this occurs if after finish further targets will be crossed
                            d_detailed[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d_detailed[f"SECTOR - {st.session_state.time_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d_detailed[f"SECTOR - {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d_detailed[f"SECTOR - {st.session_state.track_emoji}"] = f"{st.session_state.false_start_emoji}"
                        last_driven_distance = r["target_data"]["driven_distance"]
                        last_driven_time = r["target_data"]["driven_time"]
                    else:
                        section_distance = r["target_data"]["driven_distance"] - last_driven_distance
                        section_time = r["target_data"]["driven_time"] - last_driven_time
                        if(section_time != 0): # normal case
                            d_detailed[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = showDistance(section_distance)
                            d_detailed[f"SECTOR - {st.session_state.time_emoji}"] = showTime(section_time)
                            d_detailed[f"SECTOR - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(section_distance,section_time)
                            d_detailed[f"SECTOR - {st.session_state.track_emoji}"] = section_condition
                        else: # this occurs if after finish further targets will be crossed
                            d_detailed[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d_detailed[f"SECTOR - {st.session_state.time_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d_detailed[f"SECTOR - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d_detailed[f"SECTOR - {st.session_state.track_emoji}"] = f"{st.session_state.false_start_emoji}"
                        last_driven_distance = r["target_data"]["driven_distance"]
                        last_driven_time = r["target_data"]["driven_time"]  

                    if(r["target_data"]["target_code"] == 0):
                        if(section_time != 0): # normal case
                            round_distance = r["target_data"]["driven_distance"] - last_round_driven_distance
                            round_time = r["target_data"]["driven_time"] - last_round_driven_time
                            d_detailed[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = showDistance(round_distance) + f" {st.session_state.round_emoji}"
                            d_detailed[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = showTime(round_time) + f" {st.session_state.round_emoji}"
                            d_detailed[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(round_distance,round_time) + f" {st.session_state.round_emoji}"
                            last_round_driven_distance = r["target_data"]["driven_distance"]
                            last_round_driven_time = r["target_data"]["driven_time"]
                        else:
                            d_detailed[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d_detailed[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d_detailed[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                    else:
                        if(section_time != 0): # normal case
                            d_detailed[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = showDistance(r["target_data"]["driven_distance"] - last_round_driven_distance)
                            d_detailed[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = showTime(r["target_data"]["driven_time"] - last_round_driven_time)
                            d_detailed[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(r["target_data"]["driven_distance"] - last_round_driven_distance,r["target_data"]["driven_time"] - last_round_driven_time)
                        else:
                            d_detailed[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d_detailed[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d_detailed[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"

                return (d_detailed,last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,next_section_condition)

            for player in range(scoreboard_data_len):
                targetboard_data = getDetailedTargetData(lobby_id, game_id, stage_id, scoreboard_data[player]["user_name"])
#                targetboard_data = (sorted(targetboard_data, key=operator.itemgetter('target_ctr')))
                targetboard_data_len = len(targetboard_data)            

                detailed_targetboard_data = []

                last_driven_distance = float(0)
                last_driven_time = float(0)
                last_round_driven_distance = float(0)
                last_round_driven_time = float(0)

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
                
                    if(player_finished == True):
                
                        if (targetboard_data[x]["target_data"]["crossing_time"] < player_finished_timestamp): # use all those targets

                            (targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition) = constructDetailedEntry(targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"])
                            if ( game["game_mode"] == "LAP_RACE" ) and (x == 0):
                                last_driven_distance = float(0)
                                last_driven_time = float(0)
                                last_round_driven_distance = float(0)
                                last_round_driven_time = float(0)

                        else:
                            if(targetboard_data[x]["target_data"]["target_code"] == 0):
                                player_total_driven_distance = targetboard_data[x]["target_data"]["driven_distance"]
                                player_total_time = targetboard_data[x]["target_data"]["driven_time"]
                                (targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition) = constructDetailedEntry(targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"])
                                detailed_targetboard_data.append(targetboard_data[x])
                                break
                            else:
                                (targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition) = constructDetailedEntry(targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"])
                    
                        detailed_targetboard_data.append(targetboard_data[x])
                    else:
                        (targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition) = constructDetailedEntry(targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"])
                        if ( game["game_mode"] == "LAP_RACE" ) and (x == 0):
                            last_driven_distance = float(0)
                            last_driven_time = float(0)
                            last_round_driven_distance = float(0)
                            last_round_driven_time = float(0)    
                        
                        detailed_targetboard_data.append(targetboard_data[x])
                        
#                    if ( ( "end_data" in scoreboard_data[player] ) and not ( scoreboard_data[player]["end_data"] is None ) ):
# use new determination if player finished here:
                if (player_finished_list[player] == True):
                    if( game["game_mode"] == "LAP_RACE" ):
                        d_detailed = {}
#                            d_detailed[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = f"∑ {st.session_state.distance2_emoji} " + showDistance(scoreboard_data[player]["end_data"]["total_driven_distance"])
#                            d_detailed[f"SECTOR - {st.session_state.time_emoji}"] = f"∑ {st.session_state.time2_emoji} " + showTime(scoreboard_data[player]["total_time"])
#                            d_detailed[f"SECTOR - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.average_speed_emoji} " + showMeanSpeed(scoreboard_data[player]["end_data"]["total_driven_distance"],scoreboard_data[player]["total_time"])
                        d_detailed[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = f"∑ {st.session_state.distance2_emoji} " + showDistance(player_total_driven_distance)
                        d_detailed[f"SECTOR - {st.session_state.time_emoji}"] = f"∑ {st.session_state.time2_emoji} " + showTime(player_total_time)
                        d_detailed[f"SECTOR - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.average_speed_emoji} " + showMeanSpeed(player_total_driven_distance,player_total_time)
                        d_detailed[f"SECTOR - {st.session_state.track_emoji}"] = ""
                        if(scoreboard_data[player]["laps_completed"] != 0):
#                                d_detailed[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = f"Ø {st.session_state.distance2_emoji} / {st.session_state.round_emoji} " + showDistance(float(float(scoreboard_data[player]["end_data"]["total_driven_distance"])/float(scoreboard_data[player]["laps_completed"]))) 
#                                d_detailed[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = f"Ø {st.session_state.time2_emoji} / {st.session_state.round_emoji} " + showTime(float(float(scoreboard_data[player]["total_time"])/float(scoreboard_data[player]["laps_completed"])))
                            d_detailed[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = f"Ø {st.session_state.distance2_emoji} / {st.session_state.round_emoji} " + showDistance(float(float(player_total_driven_distance)/float(scoreboard_data[player]["laps_completed"]))) 
                            d_detailed[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = f"Ø {st.session_state.time2_emoji} / {st.session_state.round_emoji} " + showTime(float(float(player_total_time)/float(scoreboard_data[player]["laps_completed"])))
                        else:
                            d_detailed[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = ""
                            d_detailed[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = ""
                        d_detailed[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = ""
                        detailed_targetboard_data.append(d_detailed)
                        
                #if there is no entry, just add an empty one by calling the construct Entry with an empty dict
                while len(targetboard_data)<1:
                    detailed_targetboard_data.append(constructDetailedEntry({},last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"])[0])

                df_detailed = pd.DataFrame( detailed_targetboard_data ) 
                df_detailed = df_detailed.style.set_properties(**{
                    'font-size': '20pt',
                    'font-family': 'IBM Plex Mono',
                })

#                    st.dataframe(df_detailed)
#                    st.table(df_detailed)
                
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

#                    st.dataframe(df_detailed)
                    st.table(df_detailed)
                        

        time.sleep(0.2)

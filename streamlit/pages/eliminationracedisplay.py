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
 
    st.subheader("Elimination Game " + str(game_id) + " in Lobby " + str(lobby_id) + f" --- {st.session_state.skull_emoji} each " + str(int(game["time_limit"])) + " minute(s)")

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
                st.session_state.nextpage = "download_eliminationgame"
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
            time_limit = int(game["time_limit"])
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
                st.markdown("**ELIMINATION TIMER:**")
            with col32:
                st.markdown(str(time_limit))

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
                    
            def constructEntry(r:dict, scoreboard_data_len, player_index):

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
                        if(r["laps_completed"] == r["enter_data"]["lap_count"]): # this should not happen in elimination game
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
    
                if ( ( "start_data" in r ) and not ( r["start_data"] is None ) ):
                    current_time = datetime.now().astimezone(timezone.utc) 
                    start_time = datetime.strptime(r["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                    race_time = current_time - start_time
                else:
                    race_time = timedelta(seconds=int(0)) # fake 0 seconds

                if(race_time.total_seconds() >= (int(game["time_limit"])*60)): #check if at least one elimination due

                    race_time_minutes = race_time.total_seconds() / 60
                    num_eliminations = min(int(np.floor(race_time_minutes/game["time_limit"])),scoreboard_data_len-1) # this gives the total count of eliminations that must be done

                    targetboard_data = getDetailedTargetData(lobby_id, game_id, stage_id, r["user_name"]) # get all targets of the player 
                    targetboard_data = (sorted(targetboard_data, key=operator.itemgetter('target_ctr')))
                    targetboard_data_len = len(targetboard_data)
                    
                    round_cnt = 0
                    sector_cnt = 0
                    elim_cnt = 1
                    elim_round_cnt = 0
                    elim_sector_cnt = 0
                    
                    if( ( "last_target_timestamp" in r ) and not ( r["last_target_timestamp"] is None ) ):
                        youngest_elim_timestamp = datetime.strptime(r["last_target_timestamp"],'%Y-%m-%dT%H:%M:%S.%f').astimezone(timezone.utc)
                    else:
                        youngest_elim_timestamp = datetime.now().astimezone(timezone.utc)
                    
                    if(targetboard_data_len>0):
                        for x in range(targetboard_data_len):
                            
                            if(targetboard_data[x]["target_data"]["false_start"] == True):
                                player_false_start = True

                            start_time = datetime.strptime(r["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                            start_time+=timedelta(minutes=int(int(game["time_limit"])*elim_cnt))
                            if(targetboard_data[x]["target_data"]["crossing_time"] > start_time.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f%z')):
                            
                                elim_cnt+=1         
                                
                                if(elim_round_cnt>0):
                                    elim_rounds_sectors_times_list[player_index][0].append(elim_round_cnt-1)  # rounds
                                else:
                                    elim_rounds_sectors_times_list[player_index][0].append(0)
                                    
                                elim_rounds_sectors_times_list[player_index][1].append(elim_sector_cnt)  # sectors
                                elim_rounds_sectors_times_list[player_index][2].append(youngest_elim_timestamp)  # last sector timestamp

                            youngest_elim_timestamp = datetime.strptime(targetboard_data[x]["target_data"]["crossing_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                            
                            current_time = datetime.now().astimezone(timezone.utc) 
                            start_time = datetime.strptime(r["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                            player_race_time = current_time - start_time 

                            if(targetboard_data[x]["target_data"]["target_code"] == 0):
                                round_cnt+=1
                                elim_round_cnt+=1
                                sector_cnt = 1
                                elim_sector_cnt = 1
                            else:
                                sector_cnt+=1
                                elim_sector_cnt+=1
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

                    if(elim_round_cnt>0):
                        elim_rounds_sectors_times_list[player_index][0].append(elim_round_cnt-1)  # rounds
                    else:
                        elim_rounds_sectors_times_list[player_index][0].append(0)
                    elim_rounds_sectors_times_list[player_index][1].append(elim_sector_cnt)  # sectors
                    elim_rounds_sectors_times_list[player_index][2].append(youngest_elim_timestamp)  # last sector timestamp
                 
                else:   # meaning that no elimination done so far
                
                    num_eliminations = 0
                
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

                    if ( ( "last_target_timestamp" in r ) and not ( r["last_target_timestamp"] is None ) ):
                        youngest_timestamp = datetime.strptime(r["last_target_timestamp"],'%Y-%m-%dT%H:%M:%S.%f').astimezone(timezone.utc)
                    elif( ( "start_data" in r ) and not ( r["start_data"] is None ) ):
                        youngest_timestamp = datetime.strptime(r["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                    else:
                        youngest_timestamp = datetime.now().astimezone(timezone.utc)
                    
                    elim_rounds_sectors_times_list[player_index][0].append(r["laps_completed"])  # rounds
                    elim_rounds_sectors_times_list[player_index][1].append(completed_sectors_cnt)  # sectors
                    elim_rounds_sectors_times_list[player_index][2].append(youngest_timestamp)  # last sector timestamp
                    

                return (d,player_race_time,player_false_start,num_eliminations)

            racedisplay_data = [{}] * scoreboard_data_len            
            elim_rounds_sectors_times_list = [[[] for x in range(3)] for i in range(scoreboard_data_len)]
            
            player_race_time_list = [None] * scoreboard_data_len
            player_false_start_list = [None] * scoreboard_data_len
            num_eliminations = 0

            # construct main part of racedisplay_data here
            for x in range(scoreboard_data_len): # number of players
                (racedisplay_data[x], player_race_time_list[x], player_false_start_list[x], num_eliminations) = constructEntry(scoreboard_data[x], scoreboard_data_len, x)

            if(scoreboard_data_len >= 1):

# add new way of determination here

                handled_players = 0
                elim_cnt = 0
                position = scoreboard_data_len
                
# this piece of code handles the eliminated players
                if(num_eliminations>0):
                
                    for elim in range(num_eliminations):

                        player_rounds = []
                        player_sectors = []
                        player_time = []

                        sub_player_sectors = []
                        sub_player_time = []

                        for x in range(len(elim_rounds_sectors_times_list)):
                            player_rounds.append(elim_rounds_sectors_times_list[x][0][elim_cnt])
                            player_sectors.append(elim_rounds_sectors_times_list[x][1][elim_cnt])
                            player_time.append(elim_rounds_sectors_times_list[x][2][elim_cnt])

                        min_rounds_indices_list = get_minvalue(player_rounds)   # rounds
                        min_rounds_indices_list_len = len(min_rounds_indices_list)
                        
                        if(min_rounds_indices_list_len>1): # more players share same amount of rounds

                            for index in min_rounds_indices_list:
                                sub_player_sectors.append(player_sectors[index])

                            min_sectors_indices_list = get_minvalue(sub_player_sectors)   # sectors
                            min_sectors_indices_list_len = len(min_sectors_indices_list)
                            
                            if(min_sectors_indices_list_len>1): # more players share same amount of sectors
                            
                                for index in min_sectors_indices_list:
                                    sub_player_time.append(player_time[index])
                            
                                max_time_indices_list = get_maxvalue(sub_player_time)   # timestamp
                                max_time_indices_list_len = len(max_time_indices_list)
                                
                                if(max_time_indices_list_len>1): # more players share same last sector timestamp (should not be the case)
                                
                                    # well also here we will only eliminate one player
                                    for y in  range(len(elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]][0])):
                                        elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]][0][y] = 9999 # fake 9999 rounds - indicating player has been handled
                                    
                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]][f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] = f"{st.session_state.skull_emoji}"
                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["POS"] = str(position)
                                    if( ( "start_data" in scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]] ) and not ( scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]] is None ) ):
                                        racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["TIME"] = showTime(int(elim_cnt+1)*int(game["time_limit"])*int(60))
                                    else:
                                        racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["TIME"] = showTime(timedelta(seconds=int(0)).total_seconds())

                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["LAPS"] = str(player_rounds[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]])
                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["SECTOR"] = str(player_sectors[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]])
                                    
                                    handled_players+=1
                                    position-=1
                                
                                else: # only one player has the youngest sector timestamp - so eliminate him...
                                
                                    for y in  range(len(elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]][0])):
                                        elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]][0][y] = 9999 # fake 9999 rounds - indicating player has been handled
                                    
                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]][f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] = f"{st.session_state.skull_emoji}"
                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["POS"] = str(position)
                                    if( ( "start_data" in scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]] ) and not ( scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]] is None ) ):
                                        racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["TIME"] = showTime(int(elim_cnt+1)*int(game["time_limit"])*int(60))
                                    else:
                                        racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["TIME"] = showTime(timedelta(seconds=int(0)).total_seconds())

                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["LAPS"] = str(player_rounds[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]])
                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["SECTOR"] = str(player_sectors[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]])

                                    handled_players+=1
                                    position-=1
                                    
                            else: # only one player has the least amount of sectors - so eliminate him...
                                
                                for y in  range(len(elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[0]]][0])):
                                    elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[0]]][0][y] = 9999 # fake 9999 rounds - indicating player has been handled
                                
                                racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[0]]][f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] = f"{st.session_state.skull_emoji}"
                                racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[0]]]["POS"] = str(position)
                                if( ( "start_data" in scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[0]]] ) and not ( scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[0]]] is None ) ):
                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[0]]]["TIME"] = showTime(int(elim_cnt+1)*int(game["time_limit"])*int(60))
                                else:
                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[0]]]["TIME"] = showTime(timedelta(seconds=int(0)).total_seconds())

                                racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[0]]]["LAPS"] = str(player_rounds[min_rounds_indices_list[min_sectors_indices_list[0]]])
                                racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[0]]]["SECTOR"] = str(player_sectors[min_rounds_indices_list[min_sectors_indices_list[0]]])

                                handled_players+=1
                                position-=1
                                
                        else: # only one player has the least amount of rounds - so eliminate him...

                            for y in  range(len(elim_rounds_sectors_times_list[min_rounds_indices_list[0]][0])):
                                elim_rounds_sectors_times_list[min_rounds_indices_list[0]][0][y] = 9999 # fake 9999 rounds - indicating player has been handled
                            
                            racedisplay_data[min_rounds_indices_list[0]][f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] = f"{st.session_state.skull_emoji}"
                            racedisplay_data[min_rounds_indices_list[0]]["POS"] = str(position)
                            if( ( "start_data" in scoreboard_data[min_rounds_indices_list[0]] ) and not ( scoreboard_data[min_rounds_indices_list[0]] is None ) ):
                                racedisplay_data[min_rounds_indices_list[0]]["TIME"] = showTime(int(elim_cnt+1)*int(game["time_limit"])*int(60))
                            else:
                                racedisplay_data[min_rounds_indices_list[0]]["TIME"] = showTime(timedelta(seconds=int(0)).total_seconds())
                            
                            racedisplay_data[min_rounds_indices_list[0]]["LAPS"] = str(player_rounds[min_rounds_indices_list[0]])
                            racedisplay_data[min_rounds_indices_list[0]]["SECTOR"] = str(player_sectors[min_rounds_indices_list[0]])

                            handled_players+=1
                            position-=1

                        elim_cnt+=1
                    
    # now we will have to handle the rest of the players

                    player_eliminated_list = [None] * scoreboard_data_len

                    for x in range(scoreboard_data_len): # number of players
    # first signal players disqualified due to false start (even if engine is still running)
                        if(player_false_start_list[x] == True):
                            racedisplay_data[x]["DRIVER"] = scoreboard_data[x]["user_name"] + f"{st.session_state.false_start_emoji}"
                    
                        if(racedisplay_data[x][f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] == f"{st.session_state.skull_emoji}"):
                            player_eliminated_list[x] = True
                        elif(racedisplay_data[x][f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] == f"{st.session_state.finish_emoji}"):
                            player_eliminated_list[x] = False
                        elif(racedisplay_data[x][f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] == f"{st.session_state.false_start_emoji}"):
                            player_eliminated_list[x] = True
                        else:
                            player_eliminated_list[x] = False
                    
                    player_elinimated_indices_list = get_truevalue(player_eliminated_list)
                    player_elinimated_indices_list_len = len(player_elinimated_indices_list)
                    
                    rem_players_indices_list = [x for x in range(scoreboard_data_len) if x not in player_elinimated_indices_list]
                    rem_players_indices_list_len = len(rem_players_indices_list)
                    
                    if(rem_players_indices_list_len == 1): # only one last player - game over
                    
                        racedisplay_data[rem_players_indices_list[0]][f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] = f"{st.session_state.finish_emoji}"
                        racedisplay_data[rem_players_indices_list[0]]["POS"] = str(position)
                        if( ( "start_data" in scoreboard_data[rem_players_indices_list[0]] ) and not ( scoreboard_data[rem_players_indices_list[0]] is None ) ):
                            racedisplay_data[rem_players_indices_list[0]]["TIME"] = showTime(int(num_eliminations)*int(game["time_limit"])*int(60))
                        else:
                            racedisplay_data[rem_players_indices_list[0]]["TIME"] = showTime(timedelta(seconds=int(0)).total_seconds())

                        player_eliminated_list[rem_players_indices_list[0]] = True

                        handled_players+=1
                        position-=1
                    
                    elif(rem_players_indices_list_len > 1): # more players left - handle
                    
                        elim_cnt-=1
                    
                        while(handled_players<scoreboard_data_len):
                            
                            player_rounds = []
                            player_sectors = []
                            player_time = []

                            sub_player_sectors = []
                            sub_player_time = []

                            for x in range(len(elim_rounds_sectors_times_list)):
                                player_rounds.append(elim_rounds_sectors_times_list[x][0][elim_cnt])
                                player_sectors.append(elim_rounds_sectors_times_list[x][1][elim_cnt])
                                player_time.append(elim_rounds_sectors_times_list[x][2][elim_cnt])

                            min_rounds_indices_list = get_minvalue(player_rounds)   # rounds
                            min_rounds_indices_list_len = len(min_rounds_indices_list)
                            
                            if(min_rounds_indices_list_len>1): # more players share same amount of rounds

                                for index in min_rounds_indices_list:
                                    sub_player_sectors.append(player_sectors[index])

                                min_sectors_indices_list = get_minvalue(sub_player_sectors)   # sectors
                                min_sectors_indices_list_len = len(min_sectors_indices_list)
                                
                                if(min_sectors_indices_list_len>1): # more players share same amount of sectors
                                
                                    for index in min_sectors_indices_list:
                                        sub_player_time.append(player_time[index])
                                
                                    max_time_indices_list = get_minvalue(sub_player_time)   # timestamp
                                    max_time_indices_list_len = len(max_time_indices_list)
                                    
                                    if(max_time_indices_list_len>1): # more players share same last sector timestamp (should not be the case)
                                    
                                        for y in  range(len(elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]][0])):
                                            elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]][0][y] = 9999 # fake 9999 rounds - indicating player has been handled
                                        
                                        racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["POS"] = str(position)
                                        if( ( "start_data" in scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]] ) and not ( scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]] is None ) ):
                                            current_time = datetime.now().astimezone(timezone.utc) 
                                            start_time = datetime.strptime(scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                                            race_time = current_time - start_time                            
                                            racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["TIME"] = showTime(race_time.total_seconds())
                                        else:
                                            racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["TIME"] = showTime(timedelta(seconds=int(0)).total_seconds())

                                        handled_players+=1
                                        position-=1
                                    
                                    else:
                                    
                                        for y in  range(len(elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]][0])):
                                            elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]][0][y] = 9999 # fake 9999 rounds - indicating player has been handled
                                        
                                        racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["POS"] = str(position)
                                        if( ( "start_data" in scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]] ) and not ( scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]] is None ) ):
                                            current_time = datetime.now().astimezone(timezone.utc) 
                                            start_time = datetime.strptime(scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                                            race_time = current_time - start_time                            
                                            racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["TIME"] = showTime(race_time.total_seconds())
                                        else:
                                            racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["TIME"] = showTime(timedelta(seconds=int(0)).total_seconds())

                                        handled_players+=1
                                        position-=1
                                        
                                else:
                                    
                                    for y in  range(len(elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[0]]][0])):
                                        elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[0]]][0][y] = 9999 # fake 9999 rounds - indicating player has been handled
                                    
                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[0]]]["POS"] = str(position)
                                    if( ( "start_data" in scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[0]]] ) and not ( scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[0]]] is None ) ):
                                        current_time = datetime.now().astimezone(timezone.utc) 
                                        start_time = datetime.strptime(scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[0]]]["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                                        race_time = current_time - start_time                            
                                        racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[0]]]["TIME"] = showTime(race_time.total_seconds())
                                    else:
                                        racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[0]]]["TIME"] = showTime(timedelta(seconds=int(0)).total_seconds())

                                    handled_players+=1
                                    position-=1
                                    
                            else:

                                for y in  range(len(elim_rounds_sectors_times_list[min_rounds_indices_list[0]][0])):
                                    elim_rounds_sectors_times_list[min_rounds_indices_list[0]][0][y] = 9999 # fake 9999 rounds - indicating player has been handled
                                
                                racedisplay_data[min_rounds_indices_list[0]]["POS"] = str(position)
                                if( ( "start_data" in scoreboard_data[min_rounds_indices_list[0]] ) and not ( scoreboard_data[min_rounds_indices_list[0]] is None ) ):
                                    current_time = datetime.now().astimezone(timezone.utc) 
                                    start_time = datetime.strptime(scoreboard_data[min_rounds_indices_list[0]]["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                                    race_time = current_time - start_time                            
                                    racedisplay_data[min_rounds_indices_list[0]]["TIME"] = showTime(race_time.total_seconds())
                                else:
                                    racedisplay_data[min_rounds_indices_list[0]]["TIME"] = showTime(timedelta(seconds=int(0)).total_seconds())

                                handled_players+=1
                                position-=1
                    
# here we have to handle the case in which no elimination has been carried out so far...
                else:

                    player_elinimated_indices_list_len = 0

                    while(handled_players<scoreboard_data_len):
                            
                        player_rounds = []
                        player_sectors = []
                        player_time = []

                        sub_player_sectors = []
                        sub_player_time = []

                        for x in range(len(elim_rounds_sectors_times_list)):
                            player_rounds.append(elim_rounds_sectors_times_list[x][0][0])
                            player_sectors.append(elim_rounds_sectors_times_list[x][1][0])
                            player_time.append(elim_rounds_sectors_times_list[x][2][0])

                        min_rounds_indices_list = get_minvalue(player_rounds)   # rounds
                        min_rounds_indices_list_len = len(min_rounds_indices_list)
                            
                        if(min_rounds_indices_list_len>1): # more players share same amount of rounds

                            for index in min_rounds_indices_list:
                                sub_player_sectors.append(player_sectors[index])

                            min_sectors_indices_list = get_minvalue(sub_player_sectors)   # sectors
                            min_sectors_indices_list_len = len(min_sectors_indices_list)
                                
                            if(min_sectors_indices_list_len>1): # more players share same amount of sectors
                                
                                for index in min_sectors_indices_list:
                                    sub_player_time.append(player_time[index])
                                
                                max_time_indices_list = get_maxvalue(sub_player_time)   # timestamp
                                max_time_indices_list_len = len(max_time_indices_list)
                                    
                                if(max_time_indices_list_len>1): # more players share same last sector timestamp (should not be the case)
                                    
                                    for y in  range(len(elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]][0])):
                                        elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]][0][y] = 9999 # fake 9999 rounds - indicating player has been handled
                                        
                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["POS"] = str(position)
                                    if( ( "start_data" in scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]] ) and not ( scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["start_data"] is None ) ):
                                        current_time = datetime.now().astimezone(timezone.utc) 
                                        start_time = datetime.strptime(scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                                        race_time = current_time - start_time                            
                                        racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["TIME"] = showTime(race_time.total_seconds())
                                    else:
                                        racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["TIME"] = showTime(timedelta(seconds=int(0)).total_seconds())

                                    handled_players+=1
                                    position-=1
                                    
                                else:
                                    
                                    for y in  range(len(elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]][0])):
                                        elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]][0][y] = 9999 # fake 9999 rounds - indicating player has been handled
                                        
                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["POS"] = str(position)
                                    if( ( "start_data" in scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]] ) and not ( scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["start_data"] is None ) ):
                                        current_time = datetime.now().astimezone(timezone.utc) 
                                        start_time = datetime.strptime(scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                                        race_time = current_time - start_time                            
                                        racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["TIME"] = showTime(race_time.total_seconds())
                                    else:
                                        racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[max_time_indices_list[0]]]]["TIME"] = showTime(timedelta(seconds=int(0)).total_seconds())

                                    handled_players+=1
                                    position-=1
                                        
                            else:
                                  
                                for y in  range(len(elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[0]]][0])):
                                    elim_rounds_sectors_times_list[min_rounds_indices_list[min_sectors_indices_list[0]]][0][y] = 9999 # fake 9999 rounds - indicating player has been handled
                                    
                                racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[0]]]["POS"] = str(position)
                                if( ( "start_data" in scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[0]]] ) and not ( scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[0]]]["start_data"] is None ) ):
                                    current_time = datetime.now().astimezone(timezone.utc) 
                                    start_time = datetime.strptime(scoreboard_data[min_rounds_indices_list[min_sectors_indices_list[0]]]["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                                    race_time = current_time - start_time                            
                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[0]]]["TIME"] = showTime(race_time.total_seconds())
                                else:
                                    racedisplay_data[min_rounds_indices_list[min_sectors_indices_list[0]]]["TIME"] = showTime(timedelta(seconds=int(0)).total_seconds())
                                    
                                handled_players+=1
                                position-=1
                                    
                        else:

                            for y in  range(len(elim_rounds_sectors_times_list[min_rounds_indices_list[0]][0])):
                                elim_rounds_sectors_times_list[min_rounds_indices_list[0]][0][y] = 9999 # fake 9999 rounds - indicating player has been handled
                                
                            racedisplay_data[min_rounds_indices_list[0]]["POS"] = str(position)
                            if( ( "start_data" in scoreboard_data[min_rounds_indices_list[0]] ) and not ( scoreboard_data[min_rounds_indices_list[0]]["start_data"] is None ) ):
                                current_time = datetime.now().astimezone(timezone.utc) 
                                start_time = datetime.strptime(scoreboard_data[min_rounds_indices_list[0]]["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                                race_time = current_time - start_time                            
                                racedisplay_data[min_rounds_indices_list[0]]["TIME"] = showTime(race_time.total_seconds())
                            else:
                                racedisplay_data[min_rounds_indices_list[0]]["TIME"] = showTime(timedelta(seconds=int(0)).total_seconds())

                            handled_players+=1
                            position-=1
                    
                racedisplay_data = (sorted(racedisplay_data, key=operator.itemgetter('POS')))
                
                if(player_elinimated_indices_list_len != 0):
                    if(player_elinimated_indices_list_len+1 == scoreboard_data_len): # game over - award ceremony can take place now
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

#            st.dataframe(df)
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

            player_elinimated_indices_list = get_truevalue(player_eliminated_list)
            player_elinimated_indices_list_len = len(player_elinimated_indices_list)

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
                    
                player_position = next(item for item in racedisplay_data if item["DRIVER"] == scoreboard_data[player]["user_name"])["POS"]
                player_status = next(item for item in racedisplay_data if item["DRIVER"] == scoreboard_data[player]["user_name"])[f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"]
                    
                if(int(player_position) == 1):
                    if(player_status == f"{st.session_state.finish_emoji}"): # Finished
                        num_elim = int(int(scoreboard_data_len) - int(player_position))
                    else:
                        num_elim = 0
                else:
                    if(player_status == f"{st.session_state.skull_emoji}"): # Eliminated
                        num_elim = int(int(scoreboard_data_len+1) - int(player_position))
                    else:
                        num_elim = 0

                if ( ( "start_data" in scoreboard_data[player] ) and not ( scoreboard_data[player]["start_data"] is None ) ):
                    start_time = datetime.strptime(scoreboard_data[player]["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                    start_time+=timedelta(minutes=(game["time_limit"]*num_elim))
                else:
                    start_time = timedelta(seconds=int(0)) # fake 0 seconds
                        
                for x in range(targetboard_data_len):                  

                    if(num_elim == 0): # evaluate all targets
                        (targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition) = constructDetailedEntry(targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"])
                        if ( game["game_mode"] == "ELIMINATION" ) and (x == 0):
                            last_driven_distance = float(0)
                            last_driven_time = float(0)
                            last_round_driven_distance = float(0)
                            last_round_driven_time = float(0)
                            
                        detailed_targetboard_data.append(targetboard_data[x])
                        
                    else: # evaluate a subset of targets 
                        
                        if(targetboard_data[x]["target_data"]["crossing_time"] < start_time.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f%z')):
                  
                            (targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition) = constructDetailedEntry(targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"])
                            if ( game["game_mode"] == "ELIMINATION" ) and (x == 0):
                                last_driven_distance = float(0)
                                last_driven_time = float(0)
                                last_round_driven_distance = float(0)
                                last_round_driven_time = float(0) 

                            detailed_targetboard_data.append(targetboard_data[x])

                #if there is no entry, just add an empty one by calling the construct Entry with an empty dict
                while len(targetboard_data)<1:
                    detailed_targetboard_data.append(constructDetailedEntry({},last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"])[0])

                df_detailed = pd.DataFrame( detailed_targetboard_data ) 
                df_detailed = df_detailed.style.set_properties(**{
                    'font-size': '20pt',
                    'font-family': 'IBM Plex Mono',
                })

                model = get_model(scoreboard_data[player]["enter_data"]["engine_type"],scoreboard_data[player]["enter_data"]["tuning_type"])
                tuning = get_tuning(scoreboard_data[player]["enter_data"]["tuning_type"])
                
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

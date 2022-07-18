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

#streamlit-aggrid
#plotly
#from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
#import plotly.graph_objects as go

from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger
from .helper import handleCurrentTrackCondition, getGameInfo, getScoreBoard, showTime, showDistance

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

    st.subheader("Sector Display of Game " + str(game_id) + " from Lobby " + str(lobby_id))

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

    num_sectors = game["num_sectors"]

    placeholder1 = st.empty()
    scoreboard = st.empty()
    
    with placeholder1.container():
        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
        
        with col1:
            if st.button(f"Back {st.session_state.back_emoji}"):
                st.session_state.nextpage = "racedisplay"
                scoreboard.empty()
                placeholder1.empty()
                time.sleep(0.1)
                st.experimental_rerun()

    x_toggle = [1,2,3,4,5,6,7,0]
#    x_toggle = [1,2,3,0]
    toggle=0

    while True:

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
                        
#            def constructEntry(r:dict,current_sector):
            def constructEntry(r:dict):
            
                d = {}

                if "user_name" in r:
                    if ( ( "end_data" in r ) and not ( r["end_data"] is None ) ):
                        if(r["end_data"]["false_start"]):
                            player_status = f"{st.session_state.false_start_emoji}" #"False Start!"
                            completed_sectors_cnt = 0
                        else:
                            player_status = f"{st.session_state.finish_emoji}" #"Finished"
                            completed_sectors_cnt = 0
                    elif ( ( "start_data" in r ) and not ( r["start_data"] is None ) ):
                        current_track_condition = handleCurrentTrackCondition(r)
                        if(r["laps_completed"] == r["enter_data"]["lap_count"]):
                            player_status = f"{st.session_state.finish_emoji}" #"Finished - Player completed all rounds"
                        else:
                            player_status = current_track_condition #Driving - show Track Condition here

# add determination of sectors here
                        if(r["last_recognized_target"] == 0): # start/finish
                            if(r["laps_completed"] == r["enter_data"]["lap_count"]):
                                completed_sectors_cnt = 0
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
                        player_status = f"{st.session_state.ready_emoji}" #"Ready"
                        completed_sectors_cnt = 0
                    else:
                        player_status = ""
                        completed_sectors_cnt = 0
                    
                    d["DRIVER"] = r["user_name"]
                    d[f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] =  player_status
#                    d[f""] = current_track_condition
                else:
                    d["DRIVER"] = ""
#                    d[f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] = ""
                    
    # differentiate between RACE and GYMKHANA game mode:
                if ( game["game_mode"] == "RACE" ):

    # handle laps:
                    if "enter_data" in r:
                        if ( ( "end_data" in r ) and not ( r["end_data"] is None ) ): # EndEvent
                            if ( r["enter_data"]["lap_count"] == r["laps_completed"]): # finished Race (all laps completed)
                                d["LAP"] = str(r["laps_completed"]) + "/" + str(r["enter_data"]["lap_count"])
                            else: # not all laps completed
                                d["LAP"] = str(r["laps_completed"]+1) + "/" + str(r["enter_data"]["lap_count"])
                        elif ( ( "start_data" in r ) and not ( r["start_data"] is None ) ): # driving
                            if( r["target_code_counter"]["0"] == 0 ): # player not driven over start/finish so far
                                d["LAP"] = str(0) + "/" + str(r["enter_data"]["lap_count"])
                            elif( r["enter_data"]["lap_count"] == r["laps_completed"]):
                                d["LAP"] = str(r["laps_completed"]) + "/" + str(r["enter_data"]["lap_count"])
                            else: # player driven over start/finish
                                d["LAP"] = str(r["laps_completed"]+1) + "/" + str(r["enter_data"]["lap_count"])
                        elif "enter_data" in r: #"Ready"
                            d["LAP"] = str(0) + "/" + str(r["enter_data"]["lap_count"])
                    else:       
                        d["LAP"] = ""

                    if "enter_data" in r:
                        if(toggle < 4):
#                        if(toggle < 2):
                            current_sector = f"{st.session_state.current_sector_emoji}"
                        else:
                            current_sector = f"{st.session_state.noncompleted_sector_emoji}"

                        if(completed_sectors_cnt == 0):
                            if ( ( "end_data" in r ) and not ( r["end_data"] is None ) ):
                                d["SECTOR"] = f"{st.session_state.completed_sector_emoji}" * num_sectors
                                if(r["end_data"]["false_start"] == True):
                                    player_finished_list.append(None)
                                elif(r["laps_completed"] != r["enter_data"]["lap_count"]):
                                    player_finished_list.append(None)
                                else:
                                    player_finished_list.append(True)
                            elif(r["laps_completed"] == r["enter_data"]["lap_count"]):
                                d["SECTOR"] = f"{st.session_state.completed_sector_emoji}" * num_sectors
                                player_finished_list.append(False)
                            else:
                                d["SECTOR"] = f"{st.session_state.noncompleted_sector_emoji}" * num_sectors
                                player_finished_list.append(False)
                        else:
                            d["SECTOR"] = f"{st.session_state.completed_sector_emoji}" * (completed_sectors_cnt-1) + current_sector + f"{st.session_state.noncompleted_sector_emoji}" * (num_sectors-completed_sectors_cnt)
                            player_finished_list.append(False)
                    else:
                        d["SECTOR"] = f"{st.session_state.noncompleted_sector_emoji}" * num_sectors
                        player_finished_list.append(False)

                    if ("last_target_timestamp" in r) and (not r["last_target_timestamp"] is None):
                        if ( ( "end_data" in r ) and not ( r["end_data"] is None ) ): # EndEvent
                            d["SECTOR TIME"] = "0:00:00.000000"
                        else:
                            if( r["enter_data"]["lap_count"] == r["laps_completed"]):
                                d["SECTOR TIME"] = "0:00:00.000000"
                            else:
                                current_time = datetime.now()#.astimezone(timezone.utc) 
                                sector_start_time = datetime.strptime(r["last_target_timestamp"],'%Y-%m-%dT%H:%M:%S.%f')
                                sector_time = current_time - sector_start_time
                                d["SECTOR TIME"] = str(sector_time)
                    else:
                        d["SECTOR TIME"] = "0:00:00.000000"
                        
                    if ("second_last_target_timestamp" in r) and (not r["second_last_target_timestamp"] is None):
                        d["LAST SECTOR TIME"] = str(datetime.strptime(r["last_target_timestamp"],'%Y-%m-%dT%H:%M:%S.%f') - datetime.strptime(r["second_last_target_timestamp"],'%Y-%m-%dT%H:%M:%S.%f'))
                    else:
                        d["LAST SECTOR TIME"] = "0:00:00.000000"

                elif ( game["game_mode"] == "GYMKHANA" ):
                    pass

                current_rounds_and_sectors_list[0].append(r["laps_completed"])
                current_rounds_and_sectors_list[1].append(completed_sectors_cnt)

                return (d)
                 
            racedisplay_data = [{}] * scoreboard_data_len            
            current_rounds_and_sectors_list = [[],[]]
            player_finished_list = []

            for x in range(scoreboard_data_len): # number of players
                (racedisplay_data[x]) = constructEntry(scoreboard_data[x])

            if(scoreboard_data_len >= 1):

                handled_players = 0
                position = 1

#first handle players disqualified due to false start
                for player in range(scoreboard_data_len):
                    if ( ( "end_data" in scoreboard_data[player] ) and not ( scoreboard_data[player]["end_data"] is None ) ):
                        if(scoreboard_data[player]["end_data"]["false_start"] == True):
                            racedisplay_data[player]["POS"] = f"{st.session_state.false_start_emoji}"
                            current_rounds_and_sectors_list[0][player] = -1 # fake -1 rounds - meaning player has been handled
                            handled_players+=1

                if(handled_players < scoreboard_data_len):

                    handled_finished_players = 0

# second handle players already finished here
                    player_finished_indices_list = get_truevalue(player_finished_list)
                    player_finished_indices_list_len = len(player_finished_indices_list)

                    player_race_time_list = []

                    for player in range(scoreboard_data_len):
                        if (player in player_finished_indices_list):
                            player_race_time_list.append(float(scoreboard_data[player]["total_time"]))
                        else:
                            player_race_time_list.append(float(9999.999))

                    while handled_finished_players < player_finished_indices_list_len:
                        shortest_race_time_indices_list = get_minvalue(player_race_time_list)
                        shortest_race_time_indices_list_len = len(shortest_race_time_indices_list)

                        for x in range(shortest_race_time_indices_list_len):
                            racedisplay_data[shortest_race_time_indices_list[x]]["POS"] = str(position)
                            current_rounds_and_sectors_list[0][shortest_race_time_indices_list[x]] = -1 # fake -1 rounds - meaning player has been handled
                            handled_finished_players+=1
                            player_race_time_list[shortest_race_time_indices_list[x]] = float(9999.999) # fake time - meaning player has been handled
                            
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
                                time_list.append(datetime.strptime(scoreboard_data[x]["last_target_timestamp"],'%Y-%m-%dT%H:%M:%S.%f'))
                            elif( ( "start_data" in scoreboard_data[x] ) and not ( scoreboard_data[x]["start_data"] is None ) ):
                                time_list.append(datetime.strptime(scoreboard_data[x]["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z'))
                            else:
                                time_list.append(datetime.now())

                        youngest_time_indices_list = get_minvalue(time_list)
                        youngest_time_indices_list_len = len(youngest_time_indices_list)
                        
                        for x in youngest_time_indices_list:
                            racedisplay_data[max_rounds_indices_list[max_sectors_indices_list[x]]]["POS"] = str(position)
                            current_rounds_and_sectors_list[0][max_rounds_indices_list[max_sectors_indices_list[x]]] = -1 # fake -1 rounds - meaning player has been handled
                            handled_players+=1

                        position+=1

                racedisplay_data = (sorted(racedisplay_data, key=operator.itemgetter('POS')))

            df = pd.DataFrame( racedisplay_data )
            df = df.style.set_properties(**{
                'font-size': '25pt',
                'font-family': 'IBM Plex Mono',
            })

#            st.dataframe(df)
            st.table(df)
            
            toggle=x_toggle[toggle]
            time.sleep(0.1)

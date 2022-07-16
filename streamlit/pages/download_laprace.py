import streamlit as st
import time
from datetime import timedelta, timezone, datetime
import pandas as pd 
import numpy as np
import operator
from PIL import Image
from math import floor

from .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger

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
    return f"{km:01d}km {m:03d}m" #{cm:02d}"

def showMeanSpeed(d,t):
    if ((d is None) or d==''):
        return ''
    if ((t is None) or t==''):
        return ''
    d = float(d)
    t = float(t)
    kmh = d/t*3.6
    return f"{kmh:03.2f}km/h"

# added function for track condition tracking (quite quick and dirty)
def handleCurrentTrackCondition(r:dict):
    if ( ( "enter_data" in r ) and not ( r["enter_data"] is None ) ):
        if ( ("last_recognized_target" in r ) and not ( r["last_recognized_target"] is None ) ):
# handle rally-cross here
            if( r["enter_data"]["track_bundle"] == "rally_cross" ):
                if( r["last_recognized_target"] == 4 ):
                    current_track_condition = f"{st.session_state.track_dry_emoji}"
                elif( r["last_recognized_target"] == 5 ):
                    current_track_condition = f"{st.session_state.track_wet_emoji}"
                elif( r["last_recognized_target"] == 6 ):
                    current_track_condition = f"{st.session_state.track_gravel_emoji}"
                elif( r["last_recognized_target"] == 7 ):
                    delay = datetime.now() - datetime.strptime(r["last_target_timestamp"],'%Y-%m-%dT%H:%M:%S.%f')
                    if(delay.total_seconds() <= 3):
                        current_track_condition = f"{st.session_state.track_gravel_trap_emoji}"
                    else:
                        if( r["second_last_recognized_target"] == 4 ):
                            current_track_condition = f"{st.session_state.track_dry_emoji}"
                        elif( r["second_last_recognized_target"] == 5 ):
                            current_track_condition = f"{st.session_state.track_wet_emoji}"
                        elif( r["second_last_recognized_target"] == 6 ):
                            current_track_condition = f"{st.session_state.track_gravel_emoji}"
                        else:
                            if( r["third_last_recognized_target"] == 4 ):
                                current_track_condition = f"{st.session_state.track_dry_emoji}"
                            elif( r["third_last_recognized_target"] == 5 ):
                                current_track_condition = f"{st.session_state.track_wet_emoji}"
                            elif( r["third_last_recognized_target"] == 6 ):
                                current_track_condition = f"{st.session_state.track_gravel_emoji}"
                            else:
                                if( r["forth_last_recognized_target"] == 4 ):
                                    current_track_condition = f"{st.session_state.track_dry_emoji}"
                                elif( r["forth_last_recognized_target"] == 5 ):
                                    current_track_condition = f"{st.session_state.track_wet_emoji}"
                                elif( r["forth_last_recognized_target"] == 6 ):
                                    current_track_condition = f"{st.session_state.track_gravel_emoji}"
                                else:
                                    if( r["fith_last_recognized_target"] == 4 ):
                                        current_track_condition = f"{st.session_state.track_dry_emoji}"
                                    elif( r["fith_last_recognized_target"] == 5 ):
                                        current_track_condition = f"{st.session_state.track_wet_emoji}"
                                    elif( r["fith_last_recognized_target"] == 6 ):
                                        current_track_condition = f"{st.session_state.track_gravel_emoji}"
                                    else: # be aware this might be wrong
                                        if(r["enter_data"]["track_condition"] == "drift_asphalt"):
                                            current_track_condition = f"{st.session_state.track_dry_emoji}"
                                        elif(r["enter_data"]["track_condition"] == "drift_asphalt_wet"):
                                            current_track_condition = f"{st.session_state.track_wet_emoji}"
                                        elif(r["enter_data"]["track_condition"] == "drift_dirt"):
                                            current_track_condition = f"{st.session_state.track_gravel_emoji}"
                                        elif(r["enter_data"]["track_condition"] == "drift_ice"):
                                            current_track_condition = f"{st.session_state.track_snow_emoji}"
                                        else:
                                            current_track_condition = f"{st.session_state.track_gravel_trap_emoji}"
# handle rally-cross here when last target has been start/finish
                else:
                    if( r["second_last_recognized_target"] == None):
                        if(r["enter_data"]["track_condition"] == "drift_asphalt"):
                            current_track_condition = f"{st.session_state.track_dry_emoji}"
                        elif(r["enter_data"]["track_condition"] == "drift_asphalt_wet"):
                            current_track_condition = f"{st.session_state.track_wet_emoji}"
                        elif(r["enter_data"]["track_condition"] == "drift_dirt"):
                            current_track_condition = f"{st.session_state.track_gravel_emoji}"
                        elif(r["enter_data"]["track_condition"] == "drift_ice"):
                            current_track_condition = f"{st.session_state.track_snow_emoji}"
                        else:
                            current_track_condition = f"{st.session_state.track_gravel_trap_emoji}"
                    elif( r["second_last_recognized_target"] == 4 ):
                        current_track_condition = f"{st.session_state.track_dry_emoji}"
                    elif( r["second_last_recognized_target"] == 5 ):
                        current_track_condition = f"{st.session_state.track_wet_emoji}"
                    elif( r["second_last_recognized_target"] == 6 ):
                        current_track_condition = f"{st.session_state.track_gravel_emoji}"
                    else:
# handle rally-cross here when last two target have been start/finish
                        if( r["third_last_recognized_target"] == None):
                            if(r["enter_data"]["track_condition"] == "drift_asphalt"):
                                current_track_condition = f"{st.session_state.track_dry_emoji}"
                            elif(r["enter_data"]["track_condition"] == "drift_asphalt_wet"):
                                current_track_condition = f"{st.session_state.track_wet_emoji}"
                            elif(r["enter_data"]["track_condition"] == "drift_dirt"):
                                current_track_condition = f"{st.session_state.track_gravel_emoji}"
                            elif(r["enter_data"]["track_condition"] == "drift_ice"):
                                current_track_condition = f"{st.session_state.track_snow_emoji}"
                            else:
                                current_track_condition = f"{st.session_state.track_gravel_trap_emoji}"
                        elif( r["third_last_recognized_target"] == 4 ):
                            current_track_condition = f"{st.session_state.track_dry_emoji}"
                        elif( r["third_last_recognized_target"] == 5 ):
                            current_track_condition = f"{st.session_state.track_wet_emoji}"
                        elif( r["third_last_recognized_target"] == 6 ):
                            current_track_condition = f"{st.session_state.track_gravel_emoji}"
                        else:
# handle rally-cross here when last three target have been start/finish
                            if( r["forth_last_recognized_target"] == None):
                                if(r["enter_data"]["track_condition"] == "drift_asphalt"):
                                    current_track_condition = f"{st.session_state.track_dry_emoji}"
                                elif(r["enter_data"]["track_condition"] == "drift_asphalt_wet"):
                                    current_track_condition = f"{st.session_state.track_wet_emoji}"
                                elif(r["enter_data"]["track_condition"] == "drift_dirt"):
                                    current_track_condition = f"{st.session_state.track_gravel_emoji}"
                                elif(r["enter_data"]["track_condition"] == "drift_ice"):
                                    current_track_condition = f"{st.session_state.track_snow_emoji}"
                                else:
                                    current_track_condition = f"{st.session_state.track_gravel_trap_emoji}"
                            elif( r["forth_last_recognized_target"] == 4 ):
                                current_track_condition = f"{st.session_state.track_dry_emoji}"
                            elif( r["forth_last_recognized_target"] == 5 ):
                                current_track_condition = f"{st.session_state.track_wet_emoji}"
                            elif( r["forth_last_recognized_target"] == 6 ):
                                current_track_condition = f"{st.session_state.track_gravel_emoji}"
                            else:
# handle rally-cross here when last four target have been start/finish
                                if( r["fith_last_recognized_target"] == None):
                                    if(r["enter_data"]["track_condition"] == "drift_asphalt"):
                                        current_track_condition = f"{st.session_state.track_dry_emoji}"
                                    elif(r["enter_data"]["track_condition"] == "drift_asphalt_wet"):
                                        current_track_condition = f"{st.session_state.track_wet_emoji}"
                                    elif(r["enter_data"]["track_condition"] == "drift_dirt"):
                                        current_track_condition = f"{st.session_state.track_gravel_emoji}"
                                    elif(r["enter_data"]["track_condition"] == "drift_ice"):
                                        current_track_condition = f"{st.session_state.track_snow_emoji}"
                                    else:
                                        current_track_condition = f"{st.session_state.track_gravel_trap_emoji}"
                                elif( r["fith_last_recognized_target"] == 4 ):
                                    current_track_condition = f"{st.session_state.track_dry_emoji}"
                                elif( r["fith_last_recognized_target"] == 5 ):
                                    current_track_condition = f"{st.session_state.track_wet_emoji}"
                                elif( r["fith_last_recognized_target"] == 6 ):
                                    current_track_condition = f"{st.session_state.track_gravel_emoji}"
                                else:
# finaly give up... nobody should come to this point...
                                    if(r["enter_data"]["track_condition"] == "drift_asphalt"):
                                        current_track_condition = f"{st.session_state.track_dry_emoji}"
                                    elif(r["enter_data"]["track_condition"] == "drift_asphalt_wet"):
                                        current_track_condition = f"{st.session_state.track_wet_emoji}"
                                    elif(r["enter_data"]["track_condition"] == "drift_dirt"):
                                        current_track_condition = f"{st.session_state.track_gravel_emoji}"
                                    elif(r["enter_data"]["track_condition"] == "drift_ice"):
                                        current_track_condition = f"{st.session_state.track_snow_emoji}"
                                    else:
                                        current_track_condition = f"{st.session_state.track_gravel_trap_emoji}"
# handle rally here
            elif( r["enter_data"]["track_bundle"] == "rally" ):
                if( r["last_recognized_target"] == 4 ):
                    current_track_condition = f"{st.session_state.track_dry_emoji}"
                elif( r["last_recognized_target"] == 5 ):
                    current_track_condition = f"{st.session_state.track_wet_emoji}"
                elif( r["last_recognized_target"] == 6 ):
                    current_track_condition = f"{st.session_state.track_gravel_emoji}"
                elif( r["last_recognized_target"] == 7 ):
                    current_track_condition = f"{st.session_state.track_snow_emoji}"
# handle rally here when last target has been start/finish
                else:
                    if( r["second_last_recognized_target"] == None):
                        if(r["enter_data"]["track_condition"] == "drift_asphalt"):
                            current_track_condition = f"{st.session_state.track_dry_emoji}"
                        elif(r["enter_data"]["track_condition"] == "drift_asphalt_wet"):
                            current_track_condition = f"{st.session_state.track_wet_emoji}"
                        elif(r["enter_data"]["track_condition"] == "drift_dirt"):
                            current_track_condition = f"{st.session_state.track_gravel_emoji}"
                        elif(r["enter_data"]["track_condition"] == "drift_ice"):
                            current_track_condition = f"{st.session_state.track_snow_emoji}"
                        else:
                            current_track_condition = f"{st.session_state.track_gravel_trap_emoji}"
                    elif( r["second_last_recognized_target"] == 4 ):
                        current_track_condition = f"{st.session_state.track_dry_emoji}"
                    elif( r["second_last_recognized_target"] == 5 ):
                        current_track_condition = f"{st.session_state.track_wet_emoji}"
                    elif( r["second_last_recognized_target"] == 6 ):
                        current_track_condition = f"{st.session_state.track_gravel_emoji}"
                    elif( r["second_last_recognized_target"] == 7 ):
                        current_track_condition = f"{st.session_state.track_snow_emoji}"
                    else:
# handle rally here when last two target have been start/finish
                        if( r["third_last_recognized_target"] == None):
                            if(r["enter_data"]["track_condition"] == "drift_asphalt"):
                                current_track_condition = f"{st.session_state.track_dry_emoji}"
                            elif(r["enter_data"]["track_condition"] == "drift_asphalt_wet"):
                                current_track_condition = f"{st.session_state.track_wet_emoji}"
                            elif(r["enter_data"]["track_condition"] == "drift_dirt"):
                                current_track_condition = f"{st.session_state.track_gravel_emoji}"
                            elif(r["enter_data"]["track_condition"] == "drift_ice"):
                                current_track_condition = f"{st.session_state.track_snow_emoji}"
                            else:
                                current_track_condition = f"{st.session_state.track_gravel_trap_emoji}"
                        elif( r["third_last_recognized_target"] == 4 ):
                            current_track_condition = f"{st.session_state.track_dry_emoji}"
                        elif( r["third_last_recognized_target"] == 5 ):
                            current_track_condition = f"{st.session_state.track_wet_emoji}"
                        elif( r["third_last_recognized_target"] == 6 ):
                            current_track_condition = f"{st.session_state.track_gravel_emoji}"
                        elif( r["third_last_recognized_target"] == 7 ):
                            current_track_condition = f"{st.session_state.track_snow_emoji}"
                        else:
# handle rally here when last three target have been start/finish
                            if( r["forth_last_recognized_target"] == None):
                                if(r["enter_data"]["track_condition"] == "drift_asphalt"):
                                    current_track_condition = f"{st.session_state.track_dry_emoji}"
                                elif(r["enter_data"]["track_condition"] == "drift_asphalt_wet"):
                                    current_track_condition = f"{st.session_state.track_wet_emoji}"
                                elif(r["enter_data"]["track_condition"] == "drift_dirt"):
                                    current_track_condition = f"{st.session_state.track_gravel_emoji}"
                                elif(r["enter_data"]["track_condition"] == "drift_ice"):
                                    current_track_condition = f"{st.session_state.track_snow_emoji}"
                                else:
                                    current_track_condition = f"{st.session_state.track_gravel_trap_emoji}"
                            elif( r["forth_last_recognized_target"] == 4 ):
                                current_track_condition = f"{st.session_state.track_dry_emoji}"
                            elif( r["forth_last_recognized_target"] == 5 ):
                                current_track_condition = f"{st.session_state.track_wet_emoji}"
                            elif( r["forth_last_recognized_target"] == 6 ):
                                current_track_condition = f"{st.session_state.track_gravel_emoji}"
                            elif( r["forth_last_recognized_target"] == 7 ):
                                current_track_condition = f"{st.session_state.track_snow_emoji}"
                            else:
# handle rally here when last four target have been start/finish
                                if( r["fith_last_recognized_target"] == None):
                                    if(r["enter_data"]["track_condition"] == "drift_asphalt"):
                                        current_track_condition = f"{st.session_state.track_dry_emoji}"
                                    elif(r["enter_data"]["track_condition"] == "drift_asphalt_wet"):
                                        current_track_condition = f"{st.session_state.track_wet_emoji}"
                                    elif(r["enter_data"]["track_condition"] == "drift_dirt"):
                                        current_track_condition = f"{st.session_state.track_gravel_emoji}"
                                    elif(r["enter_data"]["track_condition"] == "drift_ice"):
                                        current_track_condition = f"{st.session_state.track_snow_emoji}"
                                    else:
                                        current_track_condition = f"{st.session_state.track_gravel_trap_emoji}"
                                elif( r["fith_last_recognized_target"] == 4 ):
                                    current_track_condition = f"{st.session_state.track_dry_emoji}"
                                elif( r["fith_last_recognized_target"] == 5 ):
                                    current_track_condition = f"{st.session_state.track_wet_emoji}"
                                elif( r["fith_last_recognized_target"] == 6 ):
                                    current_track_condition = f"{st.session_state.track_gravel_emoji}"
                                elif( r["fith_last_recognized_target"] == 7 ):
                                    current_track_condition = f"{st.session_state.track_snow_emoji}"
                                else:
# finaly give up... nobody should come to this point...
                                    if(r["enter_data"]["track_condition"] == "drift_asphalt"):
                                        current_track_condition = f"{st.session_state.track_dry_emoji}"
                                    elif(r["enter_data"]["track_condition"] == "drift_asphalt_wet"):
                                        current_track_condition = f"{st.session_state.track_wet_emoji}"
                                    elif(r["enter_data"]["track_condition"] == "drift_dirt"):
                                        current_track_condition = f"{st.session_state.track_gravel_emoji}"
                                    elif(r["enter_data"]["track_condition"] == "drift_ice"):
                                        current_track_condition = f"{st.session_state.track_snow_emoji}"
                                    else:
                                        current_track_condition = f"{st.session_state.track_gravel_trap_emoji}"
# handle none here
            else:
                if(r["enter_data"]["track_condition"] == "drift_asphalt"):
                    current_track_condition = f"{st.session_state.track_dry_emoji}"
                elif(r["enter_data"]["track_condition"] == "drift_asphalt_wet"):
                    current_track_condition = f"{st.session_state.track_wet_emoji}"
                elif(r["enter_data"]["track_condition"] == "drift_dirt"):
                    current_track_condition = f"{st.session_state.track_gravel_emoji}"
                elif(r["enter_data"]["track_condition"] == "drift_ice"):
                    current_track_condition = f"{st.session_state.track_snow_emoji}"
                else:
                    current_track_condition = f"{st.session_state.track_gravel_trap_emoji}"
# handle car in starting position here                                
        else:
            if(r["enter_data"]["track_condition"] == "drift_asphalt"):
                current_track_condition = f"{st.session_state.track_dry_emoji}"
            elif(r["enter_data"]["track_condition"] == "drift_asphalt_wet"):
                current_track_condition = f"{st.session_state.track_wet_emoji}"
            elif(r["enter_data"]["track_condition"] == "drift_dirt"):
                current_track_condition = f"{st.session_state.track_gravel_emoji}"
            elif(r["enter_data"]["track_condition"] == "drift_ice"):
                current_track_condition = f"{st.session_state.track_snow_emoji}"
            else:
                current_track_condition = f"{st.session_state.track_gravel_trap_emoji}"
    else: 
        current_track_condition = "-"
    return current_track_condition

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

    lobby_id = st.session_state.lobby_id
    game_id = st.session_state.game_id
    stage_id = st.session_state.stage_id
    num_stages = st.session_state.num_stages

    st.header("Download Game Data of Game " + str(game_id) + " from Lobby " + str(lobby_id))

    placeholder1 = st.empty()
    placeholder2 = st.empty()

    with placeholder1.container(): 
        if st.button(f"Back to Lap Race {st.session_state.back_emoji}"):
            st.session_state.nextpage = "lapracedisplay"
            placeholder1.empty()
            placeholder2.empty()
            time.sleep(0.1)
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

    with placeholder2.container(): 

        scoreboard_data = getScoreBoard(lobby_id, game_id, stage_id)
        scoreboard_data_len = len(scoreboard_data)

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
                d["Spieler"] = r["user_name"]
                d[f"{st.session_state.status_emoji} / {st.session_state.track_emoji}"] =  player_status
            else:
                d["Spieler"] = ""
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
                    d["Abg. Runden"] = str(round_cnt-1)
                else:
                    d["Abg. Runden"] = str(0)
                d["Sektor"] = str(sector_cnt)
                
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
                            d["Abg. Runden"] = str(r["laps_completed"])
                        else: # not all laps completed
                            d["Abg. Runden"] = str(r["laps_completed"])
                    elif ( ( "start_data" in r ) and not ( r["start_data"] is None ) ): # driving
                        if( r["target_code_counter"]["0"] == 0 ): # player not driven over start/finish so far
                            d["Abg. Runden"] = str(0)
                        elif( r["enter_data"]["lap_count"] == r["laps_completed"]):
                            d["Abg. Runden"] = str(r["laps_completed"])
                        else: # player driven over start/finish
                            d["Abg. Runden"] = str(r["laps_completed"])
                    elif "enter_data" in r: #"Ready"
                        d["Abg. Runden"] = str(0)
                else:       
                    d["Abg. Runden"] = ""

                if "num_sectors" in game:
                    if "enter_data" in r:
                        if ( ( "end_data" in r ) and not ( r["end_data"] is None ) ):
                            d["Sektor"] = str(completed_sectors_cnt)
                        elif(r["laps_completed"] == r["enter_data"]["lap_count"]):
                            d["Sektor"] = str(game["num_sectors"])
                        else:
                            d["Sektor"] = str(completed_sectors_cnt)
                    else:
                        d["Sektor"] = str(completed_sectors_cnt)

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
                    racedisplay_data[x]["Spieler"] = scoreboard_data[x]["user_name"] + f"{st.session_state.false_start_emoji}"
            
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
                        racedisplay_data[shortest_race_time_indices_list[x]]["Platz"] = str(position)
                        if(best_player_handled == False):
                            racedisplay_data[shortest_race_time_indices_list[x]]["Zeit"] = showTime(player_race_time_list[shortest_race_time_indices_list[x]].total_seconds())
                            best_time = player_race_time_list[shortest_race_time_indices_list[x]]
                            best_player_handled = True
                        else:
                            racedisplay_data[shortest_race_time_indices_list[x]]["Zeit"] = showTime(best_time.total_seconds()) + " + " + showTime((player_race_time_list[shortest_race_time_indices_list[x]]-best_time).total_seconds()) #"+ " + str(datetime.strptime(scoreboard_data[shortest_race_time_indices_list[x]]["last_lap_timestamp"],'%Y-%m-%dT%H:%M:%S.%f') - datetime.strptime(player_finished_timestamp,'%Y-%m-%dT%H:%M:%S.%f'))
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
                        racedisplay_data[max_rounds_indices_list[max_sectors_indices_list[x]]]["Platz"] = str(position)
                        if( ( "start_data" in scoreboard_data[max_rounds_indices_list[max_sectors_indices_list[x]]] ) and not ( scoreboard_data[max_rounds_indices_list[max_sectors_indices_list[x]]]["start_data"] is None ) ):
                            current_time = datetime.now().astimezone(timezone.utc) 
                            start_time = datetime.strptime(scoreboard_data[max_rounds_indices_list[max_sectors_indices_list[x]]]["start_data"]["signal_time"],'%Y-%m-%dT%H:%M:%S.%f%z')
                            race_time = current_time - start_time                            
                            racedisplay_data[max_rounds_indices_list[max_sectors_indices_list[x]]]["Zeit"] = showTime(race_time.total_seconds())
                        else:
                            racedisplay_data[max_rounds_indices_list[max_sectors_indices_list[x]]]["Zeit"] = showTime(timedelta(seconds=int(0)).total_seconds())
                        current_rounds_and_sectors_list[0][max_rounds_indices_list[max_sectors_indices_list[x]]] = -1 # fake -1 rounds - meaning player has been handled
                        handled_players+=1

                    position+=1
                    
            racedisplay_data = (sorted(racedisplay_data, key=operator.itemgetter('Platz')))

            if(player_finished_indices_list_len == scoreboard_data_len): # all players finished race - award ceremony can take place now
                if(scoreboard_data_len >= 1):
                    racedisplay_data[0]["Auszeichnung"] = f"{st.session_state.award_1st_emoji}"
                if(scoreboard_data_len >= 2):
                    racedisplay_data[1]["Auszeichnung"] = f"{st.session_state.award_2nd_emoji}"
                if(scoreboard_data_len >= 3):
                    racedisplay_data[2]["Auszeichnung"] = f"{st.session_state.award_3rd_emoji}"
            
        else:
            racedisplay_data = [{"Spieler": "-", f"{st.session_state.status_emoji} / {st.session_state.track_emoji}": "-", "Abg. Runden": "-", "Sektor": "-", "Platz": "-", "Zeit":"-"}]

        df = pd.DataFrame( racedisplay_data )

        st.download_button(
            f"Press to Download Lap Race Result as csv {st.session_state.download_emoji}",
            df.to_csv(index = False).encode('utf-8'),
            "Game_" + str(lobby_id) + "_" + str(game_id) + "_" + str(stage_id)+".csv",
            "text/csv",
            key='download-csv'
        )
        '''
        st.download_button(
            f"Press to Download Lap Race Result as html {st.session_state.download_emoji}",
            df.to_html(),
            "Game_" + str(lobby_id) + "_" + str(game_id) + "_" + str(stage_id)+".html",
            "text/html",
            key='download-html'
        )
        '''

        st.download_button(
            f"Press to Download Lap Race Result as json {st.session_state.download_emoji}",
            df.to_json(orient='records'),
            "Game_" + str(lobby_id) + "_" + str(game_id) + "_" + str(stage_id)+".json",
            "text/json",
            key='download-json'
        )

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
                        d_detailed[str(scoreboard_data[player]["user_name"]) + f" Sektor - {st.session_state.distance_emoji}"] = showDistance(section_distance)
                        d_detailed[f"Sektor - {st.session_state.time_emoji}"] = showTime(section_time)
                        d_detailed[f"Sektor - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(section_distance,section_time)
                        d_detailed[f"Sektor - {st.session_state.track_emoji}"] = section_condition
                    else: # this occurs if after finish further targets will be crossed
                        d_detailed[str(scoreboard_data[player]["user_name"]) + f" Sektor - {st.session_state.distance_emoji}"] = f"{st.session_state.false_start_emoji}"
                        d_detailed[f"Sektor - {st.session_state.time_emoji}"] = f"{st.session_state.false_start_emoji}"
                        d_detailed[f"Sektor - {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                        d_detailed[f"Sektor - {st.session_state.track_emoji}"] = f"{st.session_state.false_start_emoji}"
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
                        d_detailed[str(scoreboard_data[player]["user_name"]) + f" Sektor - {st.session_state.distance_emoji}"] = showDistance(section_distance)
                        d_detailed[f"Sektor - {st.session_state.time_emoji}"] = showTime(section_time)
                        d_detailed[f"Sektor - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(section_distance,section_time)
                        d_detailed[f"Sektor - {st.session_state.track_emoji}"] = section_condition
                    else: # this occurs if after finish further targets will be crossed
                        d_detailed[str(scoreboard_data[player]["user_name"]) + f" Sektor - {st.session_state.distance_emoji}"] = f"{st.session_state.false_start_emoji}"
                        d_detailed[f"Sektor - {st.session_state.time_emoji}"] = f"{st.session_state.false_start_emoji}"
                        d_detailed[f"Sektor - {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                        d_detailed[f"Sektor - {st.session_state.track_emoji}"] = f"{st.session_state.false_start_emoji}"
                    last_driven_distance = r["target_data"]["driven_distance"]
                    last_driven_time = r["target_data"]["driven_time"]
                else:
                    section_distance = r["target_data"]["driven_distance"] - last_driven_distance
                    section_time = r["target_data"]["driven_time"] - last_driven_time
                    if(section_time != 0): # normal case
                        d_detailed[str(scoreboard_data[player]["user_name"]) + f" Sektor - {st.session_state.distance_emoji}"] = showDistance(section_distance)
                        d_detailed[f"Sektor - {st.session_state.time_emoji}"] = showTime(section_time)
                        d_detailed[f"Sektor - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(section_distance,section_time)
                        d_detailed[f"Sektor - {st.session_state.track_emoji}"] = section_condition
                    else: # this occurs if after finish further targets will be crossed
                        d_detailed[str(scoreboard_data[player]["user_name"]) + f" Sektor - {st.session_state.distance_emoji}"] = f"{st.session_state.false_start_emoji}"
                        d_detailed[f"Sektor - {st.session_state.time_emoji}"] = f"{st.session_state.false_start_emoji}"
                        d_detailed[f"Sektor - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                        d_detailed[f"Sektor - {st.session_state.track_emoji}"] = f"{st.session_state.false_start_emoji}"
                    last_driven_distance = r["target_data"]["driven_distance"]
                    last_driven_time = r["target_data"]["driven_time"]  

                if(r["target_data"]["target_code"] == 0):
                    if(section_time != 0): # normal case
                        round_distance = r["target_data"]["driven_distance"] - last_round_driven_distance
                        round_time = r["target_data"]["driven_time"] - last_round_driven_time
                        d_detailed[f" ∑ Sektoren - {st.session_state.distance2_emoji}"] = showDistance(round_distance) + f" {st.session_state.round_emoji}"
                        d_detailed[f" ∑ Sektoren - {st.session_state.time2_emoji}"] = showTime(round_time) + f" {st.session_state.round_emoji}"
                        d_detailed[f"Cum. Sektoren - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(round_distance,round_time) + f" {st.session_state.round_emoji}"
                        last_round_driven_distance = r["target_data"]["driven_distance"]
                        last_round_driven_time = r["target_data"]["driven_time"]
                    else:
                        d_detailed[f" ∑ Sektoren - {st.session_state.distance2_emoji}"] = f"{st.session_state.false_start_emoji}"
                        d_detailed[f" ∑ Sektoren - {st.session_state.time2_emoji}"] = f"{st.session_state.false_start_emoji}"
                        d_detailed[f"Cum. Sektoren - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                else:
                    if(section_time != 0): # normal case
                        d_detailed[f" ∑ Sektoren - {st.session_state.distance2_emoji}"] = showDistance(r["target_data"]["driven_distance"] - last_round_driven_distance)
                        d_detailed[f" ∑ Sektoren - {st.session_state.time2_emoji}"] = showTime(r["target_data"]["driven_time"] - last_round_driven_time)
                        d_detailed[f"Cum. Sektoren - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(r["target_data"]["driven_distance"] - last_round_driven_distance,r["target_data"]["driven_time"] - last_round_driven_time)
                    else:
                        d_detailed[f" ∑ Sektoren - {st.session_state.distance2_emoji}"] = f"{st.session_state.false_start_emoji}"
                        d_detailed[f" ∑ Sektoren - {st.session_state.time2_emoji}"] = f"{st.session_state.false_start_emoji}"
                        d_detailed[f"Cum. Sektoren - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"

            return (d_detailed,last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,next_section_condition)

        for player in range(scoreboard_data_len):
            targetboard_data = getDetailedTargetData(lobby_id, game_id, stage_id, scoreboard_data[player]["user_name"])
    #                targetboard_data = (sorted(targetboard_data, key=operator.itemgetter('target_ctr')))
            targetboard_data_len = len(targetboard_data)            
           
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
                            break
                        else:
                            (targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition) = constructDetailedEntry(targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"])
                else:
                    (targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition) = constructDetailedEntry(targetboard_data[x],last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"])
                    if ( game["game_mode"] == "LAP_RACE" ) and (x == 0):
                        last_driven_distance = float(0)
                        last_driven_time = float(0)
                        last_round_driven_distance = float(0)
                        last_round_driven_time = float(0)    
                    
    #                    if ( ( "end_data" in scoreboard_data[player] ) and not ( scoreboard_data[player]["end_data"] is None ) ):
    # use new determination if player finished here:
            if (player_finished_list[player] == True):
                if( game["game_mode"] == "LAP_RACE" ):
                    d_detailed = {}
    #                            d_detailed[str(scoreboard_data[player]["user_name"]) + f" Sektor - {st.session_state.distance_emoji}"] = f"∑ {st.session_state.distance2_emoji} " + showDistance(scoreboard_data[player]["end_data"]["total_driven_distance"])
    #                            d_detailed[f"Sektor - {st.session_state.time_emoji}"] = f"∑ {st.session_state.time2_emoji} " + showTime(scoreboard_data[player]["total_time"])
    #                            d_detailed[f"Sektor - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.average_speed_emoji} " + showMeanSpeed(scoreboard_data[player]["end_data"]["total_driven_distance"],scoreboard_data[player]["total_time"])
                    d_detailed[str(scoreboard_data[player]["user_name"]) + f" Sektor - {st.session_state.distance_emoji}"] = f"∑ {st.session_state.distance2_emoji} " + showDistance(player_total_driven_distance)
                    d_detailed[f"Sektor - {st.session_state.time_emoji}"] = f"∑ {st.session_state.time2_emoji} " + showTime(player_total_time)
                    d_detailed[f"Sektor - Ø {st.session_state.average_speed_emoji}"] = f"{st.session_state.average_speed_emoji} " + showMeanSpeed(player_total_driven_distance,player_total_time)
                    d_detailed[f"Sektor - {st.session_state.track_emoji}"] = ""
                    if(scoreboard_data[player]["laps_completed"] != 0):
    #                                d_detailed[f" ∑ Sektoren - {st.session_state.distance2_emoji}"] = f"Ø {st.session_state.distance2_emoji} / {st.session_state.round_emoji} " + showDistance(float(float(scoreboard_data[player]["end_data"]["total_driven_distance"])/float(scoreboard_data[player]["laps_completed"]))) 
    #                                d_detailed[f" ∑ Sektoren - {st.session_state.time2_emoji}"] = f"Ø {st.session_state.time2_emoji} / {st.session_state.round_emoji} " + showTime(float(float(scoreboard_data[player]["total_time"])/float(scoreboard_data[player]["laps_completed"])))
                        d_detailed[f" ∑ Sektoren - {st.session_state.distance2_emoji}"] = f"Ø {st.session_state.distance2_emoji} / {st.session_state.round_emoji} " + showDistance(float(float(player_total_driven_distance)/float(scoreboard_data[player]["laps_completed"]))) 
                        d_detailed[f" ∑ Sektoren - {st.session_state.time2_emoji}"] = f"Ø {st.session_state.time2_emoji} / {st.session_state.round_emoji} " + showTime(float(float(player_total_time)/float(scoreboard_data[player]["laps_completed"])))
                    else:
                        d_detailed[f" ∑ Sektoren - {st.session_state.distance2_emoji}"] = ""
                        d_detailed[f" ∑ Sektoren - {st.session_state.time2_emoji}"] = ""
                    d_detailed[f"Cum. Sektoren - Ø {st.session_state.average_speed_emoji}"] = ""
                    targetboard_data.append(d_detailed)
                    
            #if there is no entry, just add an empty one by calling the construct Entry with an empty dict
            while len(targetboard_data)<1:
                targetboard_data.append(constructDetailedEntry({},last_driven_distance,last_driven_time,last_round_driven_distance,last_round_driven_time,section_condition, scoreboard_data[player]["user_name"])[0])

            df_detailed = pd.DataFrame( targetboard_data ) 

            st.download_button(
                f"Press to Download Stats of " + str(scoreboard_data[player]["user_name"]) + f" as csv {st.session_state.download_emoji}",
                df_detailed.to_csv(index = False).encode('utf-8'),
                "Stats_" + str(lobby_id) + "_" + str(game_id) + "_" + str(stage_id) + "_" + str(scoreboard_data[player]["user_name"])+".csv",
                "text/csv",
                key='download-csv'
            )
            '''
            st.download_button(
                f"Press to Download Stats of " + str(scoreboard_data[player]["user_name"]) + f"  as html {st.session_state.download_emoji}",
                df_detailed.to_html(),
                "Stats_" + str(lobby_id) + "_" + str(game_id) + "_" + str(stage_id) + "_" + str(scoreboard_data[player]["user_name"])+".html",
                "text/html",
                key='download-html'
            )
            '''

            st.download_button(
                f"Press to Download Stats of " + str(scoreboard_data[player]["user_name"]) + f"  as json {st.session_state.download_emoji}",
                df_detailed.to_json(orient='records'),
                "Stats_" + str(lobby_id) + "_" + str(game_id) + "_" + str(stage_id) + "_" + str(scoreboard_data[player]["user_name"])+".json",
                "text/json",
                key='download-json'
            )





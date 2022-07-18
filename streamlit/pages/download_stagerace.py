import streamlit as st
import time
from datetime import timedelta
import pandas as pd 
import numpy as np
from PIL import Image
from math import floor

from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger
from .helper import get_game_mode, get_joker_lap_code, get_app_game_mode, get_starttime, get_track_cond, get_track_bundle, get_wheels, get_setup, get_bool, get_model, get_tuning, handleCurrentTrackCondition, getGameInfo, getScoreBoard, getDetailedTargetData, showTime, showDistance, showMeanSpeed

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

    st.subheader("Download Game Data of Event " + str(game_id) + " from Lobby " + str(lobby_id))

    placeholder1 = st.empty()
    placeholder2 = st.empty()
    
    with placeholder1.container():
        if st.button(f"Back to Event {st.session_state.back_emoji}"):
            st.session_state.nextpage = "stage_racedisplay"
            placeholder1.empty()
            placeholder2.empty()
            time.sleep(0.1)
            st.experimental_rerun()

    games = []
    joker_lap_code = [None] * 20
    scoreboard_data = []
    scoreboard_len = []
    
    for x in range(num_stages):
        game = getGameInfo(lobby_id, game_id, x+1)
        if not game:
            st.error("No Game with that id exists, going back to main menu...")
            time.sleep(1)
            st.session_state.nextpage = "main_page"
            st.experimental_rerun()
        if game:
            if "joker_lap_code" in game:
                joker_lap_code[x] = game["joker_lap_code"]
        games.append(game)


    with placeholder1.container():

        for x in range(num_stages):

            scoreboard_data.append(getScoreBoard(lobby_id, game_id, x+1))

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

            col11, col12 = st.columns(2)
            
            with col11:
                st.download_button(
                    f"Download Stage " + str(x+1) + f" as csv {st.session_state.download_emoji}",
                    df.to_csv(index = False).encode('utf-8'),
                    "Game_" + str(lobby_id) + "_" + str(game_id) + "_" +str(x+1)+".csv",
                    "text/csv",
                    key='download-csv'
                )

            with col11:
                st.download_button(
                    f"Download Stage " + str(x+1) + f" as json {st.session_state.download_emoji}",
                    df.to_json(orient='records'),
                    "Game_" + str(lobby_id) + "_" + str(game_id) + "_" +str(x+1)+".json",
                    "text/json",
                    key='download-json'
                )

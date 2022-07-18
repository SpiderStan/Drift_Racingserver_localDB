import streamlit as st
import time
from datetime import timedelta
import pandas as pd 
import numpy as np
from PIL import Image
from math import floor

from .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger
from .helper import handleCurrentTrackCondition, getGameInfo, getScoreBoard, getDetailedTargetData, showTime, showDistance, showMeanSpeed

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

    st.subheader("Download Game Data of Game " + str(game_id) + " from Lobby " + str(lobby_id))

    placeholder1 = st.empty() 
    placeholder2 = st.empty()
    placeholder3 = st.empty()

    with placeholder1.container(): 
        if st.button(f"Back to Race {st.session_state.back_emoji}"):
            st.session_state.nextpage = "racedisplay"
            placeholder1.empty()
            placeholder2.empty()
            placeholder3.empty()
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

        col11, col12 = st.columns(2)
        
        with col11:
            st.download_button(
                f"Download as csv {st.session_state.download_emoji}",
                df.to_csv(index = False).encode('utf-8'),
                "Game_" + str(lobby_id) + "_" + str(game_id) + "_" + str(stage_id)+".csv",
                "text/csv",
                key='download-csv'
            )

        with col12:
            st.download_button(
                f"Download as json {st.session_state.download_emoji}",
                df.to_json(orient='records'),
                "Game_" + str(lobby_id) + "_" + str(game_id) + "_" + str(stage_id)+".json",
                "text/json",
                key='download-json'
            )

    with placeholder3.container():

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
                            d[f"SECTOR - {st.session_state.average_speed_emoji}"] = f"Ø " + showMeanSpeed(section_distance,section_time)
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
                        if(r["target_data"]["target_code"] == 4):
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
                            d[f"SECTOR - {st.session_state.average_speed_emoji}"] = f"Ø " + showMeanSpeed(section_distance,section_time)
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
                            d[f"SECTOR - {st.session_state.average_speed_emoji}"] = f"Ø " + showMeanSpeed(section_distance,section_time)
                            d[f"SECTOR - {st.session_state.track_emoji}"] = section_condition
                        else: # this occurs if after finish further targets will be crossed
                            d[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d[f"SECTOR - {st.session_state.time_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d[f"SECTOR - {st.session_state.average_speed_emoji}"] = f"{st.session_state.false_start_emoji}"
                            d[f"SECTOR - {st.session_state.track_emoji}"] = f"{st.session_state.false_start_emoji}"
                        last_driven_distance = r["target_data"]["driven_distance"]
                        last_driven_time = r["target_data"]["driven_time"]  

                    if(r["target_data"]["target_code"] == 0):
                        round_distance = r["target_data"]["driven_distance"] - last_round_driven_distance
                        round_time = r["target_data"]["driven_time"] - last_round_driven_time
                        d[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = showDistance(round_distance) + f" {st.session_state.round_emoji}"
                        d[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = showTime(round_time) + f" {st.session_state.round_emoji}"
                        d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(round_distance,round_time) + f" {st.session_state.round_emoji}"
                        last_round_driven_distance = r["target_data"]["driven_distance"]
                        last_round_driven_time = r["target_data"]["driven_time"]
                    else:
                        d[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = showDistance(r["target_data"]["driven_distance"] - last_round_driven_distance)
                        d[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = showTime(r["target_data"]["driven_time"] - last_round_driven_time)
                        d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = showMeanSpeed(r["target_data"]["driven_distance"] - last_round_driven_distance,r["target_data"]["driven_time"] - last_round_driven_time)
                                
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
    #        targetboard_data = (sorted(targetboard_data, key=operator.itemgetter('target_ctr')))
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

            if( game["game_mode"] == "RACE" ):
                d = {}
                d[str(scoreboard_data[player]["user_name"]) + f" SECTOR - {st.session_state.distance_emoji}"] = f"∑ {st.session_state.distance2_emoji} " + showDistance(scoreboard_data[player]["end_data"]["total_driven_distance"])
                d[f"SECTOR - {st.session_state.time_emoji}"] = f"∑ {st.session_state.time2_emoji} " + showTime(scoreboard_data[player]["total_time"])
                d[f"SECTOR - {st.session_state.average_speed_emoji}"] = f"Ø {st.session_state.average_speed_emoji} " + showMeanSpeed(scoreboard_data[player]["end_data"]["total_driven_distance"],scoreboard_data[player]["total_time"])
                d[f"SECTOR - {st.session_state.track_emoji}"] = ""
                d[f" ∑ SECTORS - {st.session_state.distance2_emoji}"] = f"Ø {st.session_state.distance2_emoji} / {st.session_state.round_emoji} " + showDistance(float(float(scoreboard_data[player]["end_data"]["total_driven_distance"])/float(scoreboard_data[player]["laps_completed"]))) 
                d[f" ∑ SECTORS - {st.session_state.time2_emoji}"] = f"Ø {st.session_state.time2_emoji} / {st.session_state.round_emoji} " + showTime(float(float(scoreboard_data[player]["total_time"])/float(scoreboard_data[player]["laps_completed"])))
                d[f"CUM. SECTORS - Ø {st.session_state.average_speed_emoji}"] = ""
                targetboard_data.append(d)

            #if there is no entry, just add an empty one by calling the construct Entry with an empty dict
            while len(targetboard_data)<1:
                targetboard_data.append(constructEntry({}))

            df = pd.DataFrame( targetboard_data ) 

            col11, col12 = st.columns(2)
            
            with col11:
                st.download_button(
                    f"Download Stats of " + str(scoreboard_data[player]["user_name"]) + f" as csv {st.session_state.download_emoji}",
                    df.to_csv(index = False).encode('utf-8'),
                    "Stats_" + str(lobby_id) + "_" + str(game_id) + "_" + str(stage_id) + "_" + str(scoreboard_data[player]["user_name"])+".csv",
                    "text/csv",
                    key='download-csv'
                )
            
            with col12:
                st.download_button(
                    f"Download Stats of " + str(scoreboard_data[player]["user_name"]) + f"  as json {st.session_state.download_emoji}",
                    df.to_json(orient='records'),
                    "Stats_" + str(lobby_id) + "_" + str(game_id) + "_" + str(stage_id) + "_" + str(scoreboard_data[player]["user_name"])+".json",
                    "text/json",
                    key='download-json'
                )





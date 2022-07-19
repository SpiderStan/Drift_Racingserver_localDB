import streamlit as st
import time
from zoneinfo import ZoneInfo #to set the timezone to german time
from datetime import timedelta, timezone, datetime
from math import floor

from .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger

def get_game_mode(game_mode):

    game_mode_dict = {
        "RACE":"Race",
        "LAP_RACE": "Lap Race", 
        "TIME_RACE": "Time Race",
        "ELIMINATION": "Elimination",
        "GYMKHANA":"Gymkhana",
        "GYMKHANA_TRAINING": "Gymkhana Training",
    }

    game_mode = game_mode_dict.get(str(game_mode))

    if(game_mode == None):
        return "--"

    return game_mode

def get_joker_lap_code(joker_lap_code):

    get_joker_lap_code_dict = {
        "0":"Start/Finish",
        "4":"Speed Drift",
        "5": "Angle Drift",
        "6": "180 Speed",
        "7": "360 Angle",
    }

    joker_lap_code = get_joker_lap_code_dict.get(str(joker_lap_code))

    if(joker_lap_code == None):
        return "--"

    return joker_lap_code

def get_bonus_target(bonus_target):

    get_bonus_target_dict = {
        "SPEED":"Speed Drift",
        "ANGLE":"Angle Drift",
        "360": "360 Angle",
        "180": "180 Speed",
    }

    bonus_target = get_bonus_target_dict.get(str(bonus_target))

    if(bonus_target == None):
        return "--"

    return bonus_target

def get_app_game_mode(game_mode):

    game_mode_dict = {
        "RACE":"Race",
        "GYMKHANA":"Gymkhana",
    }

    game_mode = game_mode_dict.get(str(game_mode))

    if(game_mode == None):
        return "--"

    return game_mode

def get_starttime(starttime):

    if(starttime == None):
        return "--"
        
    # e.g. 2022-07-16T17:39:00+00:00
    time1 = datetime.now(tz=ZoneInfo("Europe/Berlin"))
    timedelta_1 = time1.utcoffset()
    try:
        starttime = datetime.strptime(starttime,'%Y-%m-%dT%H:%M:%S%z').astimezone(timezone.utc)+timedelta_1
    except:
        starttime = datetime.strptime(starttime,'%Y-%m-%d %H:%M:%S.%f%z').astimezone(timezone.utc)+timedelta_1
    starttime = starttime.strftime("%d.%m.%Y, %H:%M:%S")

    return starttime

def get_track_cond(track_cond):

    track_cond_dict = {
        "drift_asphalt":"Asphalt (Dry)",
        "drift_asphalt_wet":"Asphalt (Wet)",
        "drift_dirt":"Dirt",
        "drift_ice":"Ice",
        "drift_sand":"Sand",
    }

    track_cond = track_cond_dict.get(str(track_cond))

    if(track_cond == None):
        return "--"

    return track_cond
    
def get_track_bundle(track_bundle):

    track_bundle_dict = {
        "none":"No Trackmode",
        "rally":"Rally",
        "rally_cross":"Rally Cross",
    }

    track_bundle = track_bundle_dict.get(str(track_bundle))

    if(track_bundle == None):
        return "--"

    return track_bundle

def get_wheels(wheels):

    get_wheels_dict = {
        "normal":"Normal Tires",
        "spikes":"Spikes",
        "gravel_tires":"Gravel Tires",
    }

    wheels = get_wheels_dict.get(str(wheels))

    if(wheels == None):
        return "--"

    return wheels

def get_setup(setup):

    get_setup_dict = {
        "RACE":"Race-Setup",
        "DRIFT":"Drift-Setup",
    }

    setup = get_setup_dict.get(str(setup))

    if(setup == None):
        return "--"

    return setup

def get_bool(value):

    get_value_dict = {
        "False":"Off",
        "True":"On",
    }

    value = get_value_dict.get(str(value))

    if(value == None):
        return "N/A"

    return value

def get_model(engine_type, tuning_type):

    model_dict = {
        "V8 CLUBSPORT SETUP":"D1 V8",
        "V8 BASIC SETUP 550 PS":"D1 V8",
        "V8 PERFORMANCE-KIT 700 PS":"D1 V8",
        "V8 SUPERCHARGER 920 PS":"D1 V8",
        "V8 4-WHEEL BASIC 550 PS":"D1 V8",
        "V8 4-WHEEL DRIVE 920 PS":"D1 V8",
        "V8 FWD 300 PS":"D1 V8",
        "V8 FWD 550 PS":"D1 V8",

        "V6 CLUBSPORT SETUP":"D1 TURBO",
        "V6 BASIC SETUP 565 PS":"D1 TURBO",
        "V6 DTE-CHIPTUNING 750 PS":"D1 TURBO",
        "V6 SINGLE-TURBO 1000 PS":"D1 TURBO",
        "V6 4-WHEEL BASIC 565 PS":"D1 TURBO",
        "V6 4-WHEEL DRIVE 750 PS":"D1 TURBO",
        "V6 4-WHEEL DRIVE 1000 PS":"D1 TURBO",
        "V6 FWD 303 PS":"D1 TURBO",
        "V6 FWD 565 PS":"D1 TURBO",

        "V12 CLUBSPORT SETUP":"D1 V12",
        "V12 BASIC SETUP 533":"D1 V12",
        "V12 PERFORMANCE-KIT 710 PS":"D1 V12",
        "V12 HIGH RPM BOOST 980 PS":"D1 V12",
        "V12 4-WHEEL BASIC 533 PS":"D1 V12",
        "V12 4-WHEEL DRIVE 710 PS":"D1 V12",
        "V12 4-WHEEL DRIVE 980 PS":"D1 V12",

        "mercedes_r416v_stock CLUBSPORT SETUP":"190 Evo II STOCK",
        "mercedes_r416v_stock BASIC SETUP 280 PS":"190 Evo II STOCK",
        "mercedes_r416v_stock TUNED 350 PS":"190 Evo II STOCK",
        
        "mercedes_r416v_dtm CLUBSPORT SETUP":"190 Evo II DTM",
        "mercedes_r416v_dtm BASIC SETUP 373 PS":"190 Evo II DTM",
        "mercedes_r416v_dtm RACE SETUP 390 PS":"190 Evo II DTM",

        "mercedes_v6 BASIC SETUP 450 PS":"190 Evo II TURBO",
        "mercedes_v6 DTE-CHIPTUNING 633 PS":"190 Evo II TURBO",
        "mercedes_v6 SINGLE-TURBO 800 PS":"190 Evo II TURBO",

        "mercedes_v8 BASIC SETUP 440 PS":"190 Evo II V8",
        "mercedes_v8 PERFORMANCE-KIT 620 PS":"190 Evo II V8",
        "mercedes_v8 SUPERCHARGER 780 PS":"190 Evo II V8",
        
        "bmw_r416v_stock CLUBSPORT SETUP":"BMW E30 STOCK",
        "bmw_r416v_stock BASIC SETUP 275 PS":"BMW E30 STOCK",
        "bmw_r416v_stock TUNED 320 PS":"BMW E30 STOCK",

        "bmw_r416v_dtm CLUBSPORT SETUP":"BMW E30 DTM",
        "bmw_r416v_dtm BASIC SETUP 375 PS":"BMW E30 DTM",
        "bmw_r416v_dtm RACE SETUP 390 PS":"BMW E30 DTM",

        "bmw_v6 BASIC SETUP 450 PS":"BMW E30 TURBO",
        "bmw_v6 DTE-CHIPTUNING 633 PS":"BMW E30 TURBO",
        "bmw_v6 SINGLE-TURBO 800 PS":"BMW E30 TURBO",

        "bmw_v8 BASIC SETUP 440 PS":"BMW E30 V8",
        "bmw_v8 PERFORMANCE-KIT 620 PS":"BMW E30 V8",
        "bmw_v8 SUPERCHARGER 780 PS":"BMW E30 V8",

        "bmw_mahle CLUBSPORT SETUP":"BMW E30 Mahle TURBO",
        "bmw_mahle SINGLE-TURBO 850 PS":"BMW E30 Mahle TURBO",
        "bmw_mahle SINGLE-TURBO 950 PS":"BMW E30 Mahle TURBO",

    #   "bmw_r416v_dtm CLUBSPORT SETUP":"BMW E30 Mahle DTM",
    #    "bmw_r416v_dtm BASIC SETUP 375 PS":"BMW E30 Mahle DTM",
    #    "bmw_r416v_dtm RACE SETUP 390 PS":"BMW E30 Mahle DTM",

    #    "bmw_v8 BASIC SETUP 440 PS":"BMW E30 Mahle V8",
    #    "bmw_v8 PERFORMANCE-KIT 620 PS":"BMW E30 Mahle V8",
    #    "bmw_v8 SUPERCHARGER 780 PS":"BMW E30 Mahle V8",

        "porsche_992_carrera CLUB SPORT":"Porsche 911 (992) 911 Carrera",
        "porsche_992_carrera BASIC":"Porsche 911 (992) 911 Carrera",
        "porsche_992_carrera SPORT CHRONO-PAKET":"Porsche 911 (992) 911 Carrera",

        "porsche_992_carrera_s CLUB SPORT":"Porsche 911 (992) 911 Carrera S",
        "porsche_992_carrera_s BASIC":"Porsche 911 (992) 911 Carrera S",
        "porsche_992_carrera_s SPORT CHRONO-PAKET":"Porsche 911 (992) 911 Carrera S",   

        "porsche_992_carrera_4 CLUB SPORT":"Porsche 911 (992) 911 Carrera 4",
        "porsche_992_carrera_4 BASIC":"Porsche 911 (992) 911 Carrera 4",
        "porsche_992_carrera_4 SPORT CHRONO-PAKET":"Porsche 911 (992) 911 Carrera 4", 
        
        "porsche_992_carrera_4s CLUB SPORT":"Porsche 911 (992) 911 Carrera 4S",
        "porsche_992_carrera_4s BASIC":"Porsche 911 (992) 911 Carrera 4S",
        "porsche_992_carrera_4s SPORT CHRONO-PAKET":"Porsche 911 (992) 911 Carrera 4S", 

        "nissan_gtr_rwd CLUB SPORT":"Nissan GT-R (35) GT-R RWD",
        "nissan_gtr_rwd BASIC 550 PS":"Nissan GT-R (35) GT-R RWD",
        "nissan_gtr_rwd NISMO TUNED 600 PS":"Nissan GT-R (35) GT-R RWD",
        "nissan_gtr_rwd TURBO UPGRADE 700 PS":"Nissan GT-R (35) GT-R RWD",
        "nissan_gtr_rwd WORLD RECORD 1190 PS":"Nissan GT-R (35) GT-R RWD",
        
        "nissan_gtr_awd BASIC 550 PS":"Nissan GT-R (35) GT-R AWD",
        "nissan_gtr_awd NISMO TUNED 600 PS":"Nissan GT-R (35) GT-R AWD",
        "nissan_gtr_awd TURBO UPGRADE 700 PS":"Nissan GT-R (35) GT-R AWD",
        "nissan_gtr_awd WORLD RECORD 1190 PS":"Nissan GT-R (35) GT-R AWD",

        "nissan_v8_rwd 5.2L 480 PS":"Nissan GT-R (35) V8 RWD",
        "nissan_v8_rwd 5.2L 510 PS":"Nissan GT-R (35) V8 RWD",
        "nissan_v8_rwd 5.6L FAI-GT1 600 PS":"Nissan GT-R (35) V8 RWD",
        "nissan_v8_rwd 5.6L TWIN TURBO 650 PS":"Nissan GT-R (35) V8 RWD",
        "nissan_v8_rwd 5.6 BIG BOOST 1000 PS":"Nissan GT-R (35) V8 RWD",
    }

    model = model_dict.get(str(engine_type) + " " +str(tuning_type))

    if(model == None):
        return "--"

    return (model)
    
def get_tuning(tuning_type):

    tuning_type_dict = {
        "CLUBSPORT SETUP":"Clubsport",
        "CLUB SPORT":"Clubsport",
        "BASIC SETUP 550 PS":"Basic Setup 550 PS",
        "PERFORMANCE-KIT 700 PS":"Performance-Kit 700 PS",
        "SUPERCHARGER 920 PS":"Supercharger 920 PS",
        "4-WHEEL BASIC 550 PS":"4-Wheel Basic 550 PS",
        "4-WHEEL DRIVE 920 PS":"4-Wheel Drive 920 PS",
        "FWD 300 PS":"FWD 300 PS",
        "FWD 550 PS":"FWD 550 PS",

        "BASIC SETUP 565 PS":"Basic Setup 565 PS",
        "DTE-CHIPTUNING 750 PS":"DTE-Chiptuning 750 PS",
        "SINGLE-TURBO 1000 PS":"Single-Turbo 1000 PS",
        "4-WHEEL BASIC 565 PS":"4-Wheel Basic 565 PS",
        "4-WHEEL DRIVE 750 PS":"4-Wheel Drive 750 PS",
        "4-WHEEL DRIVE 1000 PS":"4-Wheel Drive 1000 PS",
        "FWD 303 PS":"FWD 303 PS",
        "FWD 565 PS":"FWD 565 PS",

        "BASIC SETUP 533":"Basic Setup 533 PS",
        "PERFORMANCE-KIT 710 PS":"Performance-Kit 710 PS",
        "HIGH RPM BOOST 980 PS":"High RPM Boost 980 PS",
        "4-WHEEL BASIC 533 PS":"4-Wheel Basic 533 PS",
        "4-WHEEL DRIVE 710 PS":"4-Wheel Drive 710 PS",
        "4-WHEEL DRIVE 980 PS":"4-Wheel Drive 980 PS",

        "BASIC SETUP 280 PS":"Basic Setup 280 PS",
        "TUNED 350 PS":"Tuned 350 PS",
        
        "BASIC SETUP 373 PS":"Basic Setup 373 PS",
        "RACE SETUP 390 PS":"Race Setup 390 PS",

        "BASIC SETUP 450 PS":"Basic Setup 450 PS",
        "DTE-CHIPTUNING 633 PS":"DTE-Chiptuning 633 PS",
        "SINGLE-TURBO 800 PS":"Single-Turbo 800 PS",

        "BASIC SETUP 440 PS":"Basic Setup 440 PS",
        "PERFORMANCE-KIT 620 PS":"Performance-Kit 620 PS",
        "SUPERCHARGER 780 PS":"Supercharger 780 PS",
        
        "BASIC SETUP 275 PS":"Basic Setup 275 PS",
        "TUNED 320 PS":"Tuned 320 PS",

        "BASIC SETUP 375 PS":"Basic Setup 375 PS",

        "SINGLE-TURBO 850 PS":"Single-Turbo 850 PS",
        "SINGLE-TURBO 950 PS":"Single-Turbo 950 PS",

        "BASIC":"Basic",
        "SPORT CHRONO-PAKET":"Sport Chrono-Paket",

        "BASIC 550 PS":"Basic 550 PS",
        "NISMO TUNED 600 PS":"Nismo Tuned 600 PS",
        "TURBO UPGRADE 700 PS":"Tubo Upgrade 700 PS",
        "WORLD RECORD 1190 PS":"World Record 1190 PS",

        "5.2L 480 PS":"5.2L 480 PS",
        "5.2L 510 PS":"5.2L 510 PS",
        "5.6L FAI-GT1 600 PS":"5.6L FAI-GT1 600 PS",
        "5.6L TWIN TURBO 650 PS":"5.6L Twin Turbo 650 PS",
        "5.6 BIG BOOST 1000 PS":"5.6 Big Boost 1000 PS",
    }

    tuning_type = tuning_type_dict.get(str(tuning_type))

    if(tuning_type == None):
        return "--"

    return (tuning_type)
    
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
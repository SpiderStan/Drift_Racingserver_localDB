
"""
Module defining the driftapi core and enum classes.
Note: for a complete server implementation, you probably want to also define some additional classes.

"""
from pydantic import BaseModel, ValidationError, Field

from enum import Enum
from time import time
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
from .driftapi import track_condition, track_bundle, wheels, setup_mode, EnterData, StartData, EndData, TargetData, target_code, game_mode, bonus_target, gymkhana_training_targets

class LobbySchema(BaseModel):
    lobby_id:str = Field(...)
    password:Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "lobby_id": "Lobby1",
                "password": "1234",
            }
        }

class GameSchema(BaseModel):
    lobby_id:str = Field(...)
    game_id:str = Field(...)
    #password_sh3:Optional[str]
    num_stages:Optional[int] = Field(None, title="number of stages")
    stage_id:Optional[int] = Field(None, title="the current stage number")
    start_time:Optional[datetime] = Field(None, title="the the start time for the run")
    track_id:Optional[str]
    time_limit:Optional[float] = Field(None, title="the time limit for the run, in seconds")
    lap_count:Optional[int] = Field(None, title="number of rounds (for the race mode)")
    #future: add more conditions (race conditions)  
    track_condition:Optional[track_condition]
    track_bundle:Optional[track_bundle]
    wheels:Optional[wheels]
    setup_mode:Optional[setup_mode]
    game_mode:Optional[game_mode]
    bonus_target:Optional[bonus_target]
    joker_lap_code:Optional[int] = Field(None, title="if set, this target code counter is displayed to be used for joker-laps etc.")
    joker_lap_precondition_code:Optional[int] = Field(None, title="if set, this target code is required to be detected before the joker-lap code to count as actual joker lap.")
    individual_trial:bool = Field(False, title="enable/disable individual time/score trial")
    gymkhana_training_targets:Optional[gymkhana_training_targets]

    class Config:
        schema_extra = {
            "example": {
                "lobby_id": "Lobby1",
                "game_id": "Race1",
                "num_stages": 1,
                "stage_id": 1,
                "start_time": "2022-06-09T19:37:48.357000+00:00",
                "track_id": "Track1",
                "time_limit": 10,
                "lap_count": 20,
				"track_condition": "drift_asphalt",
				"track_bundle": "none",
				"wheels": "normal",
				"setup_mode": "RACE",
				"game_mode": "RACE",
				"bonus_target": "SPEED",
				"joker_lap_code": 0,
				"joker_lap_precondition_code": 0,
                "individual_trial": False,
                "gymkhana_training_targets": "ANGLE -> 180° -> SPEED -> 360°"
            }
        }

#Note: uuid is the players uuid, timestamp is the last update to the player status, where timestamp refers to the app-time, not the server time.
class PlayerStatusSchema(BaseModel):
    lobby_id:str = Field(...)
    game_id:str = Field(...)
    user_id:UUID = Field(...)
    user_name:str = Field(...)
    stage_id:int = Field(...)
    laps_completed:Optional[int]
    target_code_counter:Optional[dict]
    total_score:Optional[int]
    total_time:Optional[str]
    best_lap:Optional[str]
    last_lap:Optional[str]
    last_lap_timestamp:Optional[datetime]
    last_target_timestamp:Optional[datetime]
    best_speed_drift:Optional[int]
    best_angle_drift:Optional[int]
    best_360_angle:Optional[int]
    best_180_speed:Optional[int]
    last_recognized_target:Optional[target_code]
    second_last_recognized_target:Optional[target_code]
    third_last_recognized_target:Optional[target_code]
    forth_last_recognized_target:Optional[target_code]
    fith_last_recognized_target:Optional[target_code]
    joker_laps_counter:Optional[int]
    enter_data:Optional[EnterData]
    start_data:Optional[StartData]
    end_data:Optional[EndData]

    class Config:
        schema_extra = {
            "example": {
                "lobby_id": "Lobby1",
                "game_id": "Race1",
                "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "user_name": "PlayerNo1",
                "stage_id": 1,
                "target_code_counter": {},
                "total_score": 0,
				"total_time": "-", 
				"best_lap": "-",
				"last_lap": "-",
				"last_lap_timestamp": "2022-06-09T19:37:48.357000+00:00",
				"last_target_timestamp": "2022-06-09T19:37:48.357000+00:00",
				"best_speed_drift": 0,
				"best_angle_drift": 0,
				"best_360_angle": 0,
				"best_180_speed": 0,
				"last_recognized_target": 0,
				"second_last_recognized_target": 0,
				"third_last_recognized_target": 0,
				"forth_last_recognized_target": 0,
				"fith_last_recognized_target": 0,
				"joker_laps_counter": 0,
				"enter_data": {},
				"start_data": {},
				"end_data": {},
            }
        }

class PlayerTargetsSchema(BaseModel):
    lobby_id:str = Field(...)
    game_id:str = Field(...)
    user_id:UUID = Field(...)
    user_name:str = Field(...)
    stage_id:int = Field(...)
    target_ctr:Optional[int]
    target_data:Optional[TargetData]
    
    class Config:
        schema_extra = {
                "lobby_id": "Lobby1",
                "game_id": "Race1",
                "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "user_name": "PlayerNo1",
                "stage_id": 1,
                "target_ctr": 1,
                "target_data": {},
        }

class PlayerGymkhanaHighScoreSchema(BaseModel):
    lobby_id:str = Field(...)   
    user_id:UUID = Field(...)
    user_name:str = Field(...)
    engine_type: str = Field(None, title="The id of the motor type. No ENUM because this might get extended. Example: 'DTM', 'V8' etc.", example="V8") 
    tuning_type: str = Field(None, title="The id of the motor setup. No ENUM because this might get extended.", example="BASIC SETUP 550 PS")
    steering_angle: float = Field(None, title="the choosen steering angle as set in the settings menu of the app", example=70.0)
    driftassist:bool = Field(None, title="if driftassist is enabled in the settings menu of the app.", example=True)
    softsteering:bool = Field(None, title="if softsteering is enabled in the settings menu of the app.", example=False)
    setup_mode: setup_mode
    wheels: wheels
    track_condition: track_condition
    high_score_timestamp:Optional[datetime] 
    high_score:Optional[int]
    class Config:
        schema_extra = {
                "lobby_id": "Lobby1",
                "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "user_name": "PlayerNo1",
                "engine_type": "V8",
                "tuning_type": "BASIC SETUP 550 PS",
                "steering_angle": 70.0,
                "driftassist": True,
                "softsteering": False,
                "setup_mode": "DRIFT",
                "wheels": "normal",
                "track_condition": "drift_asphalt",
                "high_score_timestamp": "2022-06-09T19:37:48.357000+00:00",
                "high_score": 30000,
        }
        
def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }
	
def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
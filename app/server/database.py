from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder

from backports.zoneinfo import ZoneInfo #to set the timezone to german time
from datetime import timedelta, timezone, datetime
import time
import uuid
from typing import List, Optional, TypeVar, Generic, cast, Any, Type, get_args
from collections.abc import Callable

from bson.objectid import ObjectId
import motor.motor_asyncio

from pymongo import MongoClient, DESCENDING, ASCENDING
from pydantic import BaseModel

from .singletons import settings, logger

T = TypeVar('T', bound=BaseModel)

from .models.driftapi import (
    PingResponse,
#    EnterData,
#    StartData,
#    TargetData,
	EndData,
	RaceEvent,
	EnterEvent,
	StartEvent,
	TargetEvent,
	EndEvent,
	target_code,
)

from .models.racedisplay import (
    ErrorResponseModel,
    ResponseModel,
	PlayerStatusSchema,
	GameSchema,
    LobbySchema,
)

# --------------------------------------------------------------------------------
# driftapi
client = motor.motor_asyncio.AsyncIOMotorClient(settings.database_url)
driftapi_database = client[settings.database_name]
driftapi_playerstatus_collection = driftapi_database.get_collection("driftapi_playerstatus_collection")
driftapi_game_collection = driftapi_database.get_collection("driftapi_game_collection")
driftapi_lobby_collection = driftapi_database.get_collection("driftapi_lobby_collection")
# currently not used:
#driftapi_raceevent_collection = driftapi_database.get_collection("driftapi_raceevent_collection")


# helpers
def lobby_helper(lobby) -> dict:
    return {
        "id": str(lobby["_id"]),
        "lobby_id": str(lobby["lobby_id"]),
        "password": str(lobby["password"]),
    }

def game_helper(game) -> dict:
    return {
		"id": str(game["_id"]),
        "lobby_id": str(game["lobby_id"]),
        "game_id": str(game["game_id"]),
        "num_stages": game["num_stages"],
        "stage_id": game["stage_id"],
        "start_time": game["start_time"],
        "track_id": game["track_id"],
        "time_limit": game["time_limit"],
        "lap_count": game["lap_count"],
        "track_condition": game["track_condition"],
        "track_bundle": game["track_bundle"],
        "wheels": game["wheels"],
        "setup_mode": game["setup_mode"],
        "game_mode": game["game_mode"],
        "bonus_target": game["bonus_target"],
        "joker_lap_code": game["joker_lap_code"],
        "joker_lap_precondition_code": game["joker_lap_precondition_code"],	
    }

def player_helper(player) -> dict:
    return {
		"id": str(player["_id"]),
        "lobby_id": str(player["lobby_id"]),
        "game_id": str(player["game_id"]),
        "user_id": str(player["user_id"]),
        "user_name": str(player["user_name"]),
        "stage_id": player["stage_id"],
        "laps_completed": player["laps_completed"],
        "target_code_counter": player["target_code_counter"],
        "total_score":player["total_score"],
        "total_time": player["total_time"],
        "best_lap": player["best_lap"],
        "last_lap": player["last_lap"],
        "last_lap_timestamp": player["last_lap_timestamp"],
        "last_target_timestamp": player["last_target_timestamp"],
        "best_speed_drift": player["best_speed_drift"],
        "best_angle_drift": player["best_angle_drift"],
        "best_360_angle": player["best_360_angle"],
        "best_180_speed": player["best_180_speed"],
        "last_recognized_target": player["last_recognized_target"],
        "second_last_recognized_target": player["second_last_recognized_target"],
        "third_last_recognized_target": player["third_last_recognized_target"],
        "forth_last_recognized_target": player["forth_last_recognized_target"],
        "fith_last_recognized_target": player["fith_last_recognized_target"],
        "joker_laps_counter": player["joker_laps_counter"],
        "enter_data": player["enter_data"],
        "start_data": player["start_data"],
        "end_data": player["end_data"],
    }

def get_time() -> int:
    """Just a helper for getting time in consistent way"""
    return int(time.time())

def _convert(obj: dict, cls: type):
    """Remove redundant _id field and convert to given type."""
    if obj is not None:
        obj["id"] = str(obj["_id"])
        del obj["_id"]
        return cls(**obj)

# Retrieve all lobbies present in the database
async def find_lobbies():
    lobbies = []
    async for lobby in driftapi_lobby_collection.find():
        lobbies.append(lobby_helper(lobby))
    return lobbies

# Add a new lobby 
async def add_lobby(lobby_data: dict) -> dict:
    lobby = await driftapi_lobby_collection.find_one({"lobby_id":lobby_data["lobby_id"]})
    if lobby:
        return lobby_helper(lobby)
    lobby = await driftapi_lobby_collection.insert_one(lobby_data)
    new_lobby = await driftapi_lobby_collection.find_one({"_id":lobby.inserted_id})
    return lobby_helper(new_lobby)

# Retrieve one specific lobby from database
async def get_lobby_data(lobby_id: str):
    lobby = await driftapi_lobby_collection.find_one({"lobby_id":lobby_id})
    return lobby_helper(lobby)

# Delete a lobby from the game_database
async def delete_lobby(lobby_id: str):
#delete all players from all games in this lobby first (this includes all stages as well)
    async for player in driftapi_playerstatus_collection.find({"lobby_id":lobby_id}):
        await driftapi_playerstatus_collection.delete_one({"lobby_id":lobby_id})
#delete all games in this lobby (this includes all stages as well)
    async for game in driftapi_game_collection.find({"lobby_id":lobby_id}):
        await driftapi_game_collection.delete_one({"lobby_id":lobby_id})
# now delete lobby
    lobby = await driftapi_lobby_collection.find_one({"lobby_id":lobby_id})
    if lobby:
        await driftapi_lobby_collection.delete_one({"lobby_id":lobby_id})
        return True

# Add a new game 
async def add_game(lobby_id: str, game_data: dict) -> dict:
    game = await driftapi_game_collection.find_one({"lobby_id":lobby_id, "game_id":game_data["game_id"], "stage_id":game_data["stage_id"]})
    if game:
        return game_helper(game)
    game = await driftapi_game_collection.insert_one(game_data)
    new_game = await driftapi_game_collection.find_one({"_id": game.inserted_id})
    return game_helper(new_game)

# Delete a game from the game_database
async def delete_game(lobby_id: str, game_id: str):
#delete all players first (also includes all stages)
    async for player in driftapi_playerstatus_collection.find({"lobby_id":lobby_id, "game_id":game_id}):
        await driftapi_playerstatus_collection.delete_one({"lobby_id":lobby_id, "game_id":game_id})
# now delete game (also includes all stages)
    async for game in driftapi_game_collection.find({"lobby_id":lobby_id, "game_id":game_id}):
        await driftapi_game_collection.delete_one({"lobby_id":lobby_id, "game_id":game_id})
    return True

# Retrieve all games present in the database (ensure that games will only be shown once if consisting of multiple stages)
async def find_games(lobby_id: str):
    games = []
    async for game in driftapi_game_collection.find({"lobby_id":lobby_id, "stage_id":1}):
        games.append(game_helper(game))
    return games

# Retrieve one specific game from database
async def get_game_data(lobby_id: str, game_id: str, stage_id: int):
    game = await driftapi_game_collection.find_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id})
    return game_helper(game)

# Retrieve all players of a specific game from database
async def get_playerstatus(lobby_id: str, game_id: str, stage_id: int):
    players = []
    async for player in driftapi_playerstatus_collection.find({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id}):
        players.append(player_helper(player))
    return players
    
# Delete a user from a specific game from the user_database (this includes all stages as well)
async def delete_player(lobby_id: str, game_id: str, user_name:str):
    async for player in driftapi_playerstatus_collection.find({"lobby_id":lobby_id, "game_id":game_id, "user_name":user_name}):
        await driftapi_playerstatus_collection.delete_one({"lobby_id":lobby_id, "game_id":game_id, "user_name":user_name})
    return True

# Delete a user from a specific game and stage from the user_database
async def delete_player_from_stage(lobby_id: str, game_id: str, stage_id: int, user_name:str):
    player = await driftapi_playerstatus_collection.find_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id, "user_name":user_name})
    if player:
        await driftapi_playerstatus_collection.delete_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id, "user_name":user_name})
    return True

# Delete all users from a specific game from the user_database (also include all stages if multiple) 
async def delete_players(lobby_id: str, game_id: str, stage_id: int):
    async for player in driftapi_playerstatus_collection.find({"lobby_id":lobby_id, "game_id":game_id}):
        await driftapi_playerstatus_collection.delete_one({"lobby_id":lobby_id, "game_id":game_id})

# Feature add: if start time was set in game, than set as current time + 2 min:
    game = await driftapi_game_collection.find_one({"lobby_id":lobby_id, "game_id":game_id})
    if game:
        game_data = GameSchema(
            lobby_id = lobby_id, #for safety
            game_id = game_id, #for safety
            #password_sh3 = None,
            num_stages = game["num_stages"],
            stage_id = stage_id, #for safety
            start_time = game["start_time"],
            track_id = game["track_id"],
            time_limit = game["time_limit"],
            lap_count = game["lap_count"],
            #future: add more conditions (race conditions)  
            track_condition = game["track_condition"],
            track_bundle = game["track_bundle"],
            wheels = game["wheels"],
            setup_mode = game["setup_mode"],
            game_mode = game["game_mode"],
            bonus_target = game["bonus_target"],
            joker_lap_code = game["joker_lap_code"],
            joker_lap_precondition_code = game["joker_lap_precondition_code"]
        )
        game_data = jsonable_encoder(game_data)

        if ( game_data["start_time"] != None):
            current_time = datetime.now()
            n = 2
            future_time = current_time + timedelta(minutes=n)
            start_time = future_time.astimezone(timezone.utc)
            
            game_data["start_time"] = str(start_time)
            updated_game = await driftapi_game_collection.update_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id},{"$set":game_data})

    return True
   
# Delete all users from a specific stage of a stage game from the user_database
async def delete_players_from_stage(lobby_id: str, game_id: str, stage_id: int):
    async for player in driftapi_playerstatus_collection.find({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id}):
        await driftapi_playerstatus_collection.delete_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id})
    return True
       
# Set the starting lights in 2 minutes (also include all stages if multiple) 
async def start_stage(lobby_id: str, game_id: str, stage_id: int):
    game = await driftapi_game_collection.find_one({"lobby_id":lobby_id, "game_id":game_id})
    if game:
        num_stages = int(game["num_stages"])
        for x in range(num_stages):
            game = await driftapi_game_collection.find_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":x+1})
            if game:
                game_data = GameSchema(
                    lobby_id = lobby_id, #for safety
                    game_id = game_id, #for safety
                    #password_sh3 = None,
                    num_stages = game["num_stages"],
                    stage_id = game["stage_id"],
                    track_id = game["track_id"],
                    time_limit = game["time_limit"],
                    lap_count = game["lap_count"],
                    #future: add more conditions (race conditions)  
                    track_condition = game["track_condition"],
                    track_bundle = game["track_bundle"],
                    wheels = game["wheels"],
                    setup_mode = game["setup_mode"],
                    game_mode = game["game_mode"],
                    bonus_target = game["bonus_target"],
                    joker_lap_code = game["joker_lap_code"],
                    joker_lap_precondition_code = game["joker_lap_precondition_code"]
                )
                game_data = jsonable_encoder(game_data)

                current_time = datetime.now()
                n = 2
                future_time = current_time + timedelta(minutes=n)
                start_time = future_time.astimezone(timezone.utc)
                    
                game_data["start_time"] = str(start_time)
                updated_game = await driftapi_game_collection.update_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":x+1},{"$set":game_data})

    return True
    
#----------------------------------------------------------------------------------------------

# Drift API Function !
async def ping_game(lobby_id: str, game_id: str, stage_id:int):
    game = await driftapi_game_collection.find_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id})
    if game:
	    return game

async def insert_or_update_playerstatus(lobby_id:str, game_id:str, stage_id:int, obj:EnterEvent) -> bool:
    targetCounter = {}
    for e in target_code:
        targetCounter[str(e.value)]=0

    user_data = PlayerStatusSchema(
        lobby_id = lobby_id,
        game_id = game_id,#obj.game_id,	#for safety
        user_id = obj.user_id,
        user_name = obj.user_name,
        stage_id = stage_id,
        laps_completed = 0,
        target_code_counter=targetCounter,
        total_score = 0,
        total_time = "",
        best_lap = None,
        last_lap = None,
        last_lap_timestamp = None,
        last_target_timestamp = None,
        best_speed_drift = None,
        best_angle_drift = None,
        best_360_angle = None,
        best_180_speed = None,
        last_recognized_target = None,
        second_last_recognized_target = None,
        third_last_recognized_target = None,
        forth_last_recognized_target = None,
        fith_last_recognized_target = None,
        joker_laps_counter = 0,
        enter_data = obj.data,
        start_data = None,
        end_data = None
    )

    user_data = jsonable_encoder(user_data)
    game_data = await driftapi_game_collection.find_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id})
    if game_data:
        player = await driftapi_playerstatus_collection.find_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id, "user_id":user_data["user_id"]})
        if player:
            updated_player = await driftapi_playerstatus_collection.update_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id, "user_id":user_data["user_id"]},{"$set": user_data})
        else:
            await driftapi_playerstatus_collection.insert_one(user_data)
    return True

async def insert_raceevent(lobby_id: str, game_id:str, stage_id:int, obj: RaceEvent, sha3_password = None) -> str:

    eventType = type(obj)
    if eventType is EnterEvent:
        await insert_or_update_playerstatus(lobby_id, game_id, stage_id, obj)

    elif eventType is TargetEvent:
        set_user_id = jsonable_encoder(obj.user_id)
        playerStatusId = await driftapi_playerstatus_collection.find_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id, "user_id":set_user_id})
        if playerStatusId:
            user_data = PlayerStatusSchema(
                lobby_id = lobby_id, #for safety
                game_id = game_id, #for safety
                user_id = obj.user_id,
                user_name = obj.user_name,
                stage_id = playerStatusId["stage_id"],
                laps_completed = playerStatusId["laps_completed"],
                target_code_counter=playerStatusId["target_code_counter"],
                total_score = playerStatusId["total_score"],
                total_time = playerStatusId["total_time"],
                best_lap = playerStatusId["best_lap"],
                last_lap = playerStatusId["last_lap"],
                last_lap_timestamp = playerStatusId["last_lap_timestamp"],
                last_target_timestamp = playerStatusId["last_target_timestamp"],
                best_speed_drift = playerStatusId["best_speed_drift"],
                best_angle_drift = playerStatusId["best_angle_drift"],
                best_360_angle = playerStatusId["best_360_angle"],
                best_180_speed = playerStatusId["best_180_speed"],
                last_recognized_target = playerStatusId["last_recognized_target"],
                second_last_recognized_target = playerStatusId["second_last_recognized_target"],
                third_last_recognized_target = playerStatusId["third_last_recognized_target"],
                forth_last_recognized_target = playerStatusId["forth_last_recognized_target"],
                fith_last_recognized_target = playerStatusId["fith_last_recognized_target"],
                joker_laps_counter = playerStatusId["joker_laps_counter"],
                enter_data = playerStatusId["enter_data"],
                start_data = playerStatusId["start_data"],
                end_data = playerStatusId["end_data"]
            )

            user_data = jsonable_encoder(user_data)

            #increase the target code counter by one (for tracking the number of targets that had been passed)
            user_data["target_code_counter"][str(obj.data.target_code.value)]+=1

            game = await driftapi_game_collection.find_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id})
            if game:
                game_data = GameSchema(
                    lobby_id = lobby_id, #for safety
                    game_id = game_id, #for safety
                    #password_sh3 = None,
                    num_stages = game["num_stages"],
                    stage_id = game["stage_id"],
                    start_time = game["start_time"],
                    track_id = game["track_id"],
                    time_limit = game["time_limit"],
                    lap_count = game["lap_count"],
                    #future: add more conditions (race conditions)  
                    track_condition = game["track_condition"],
                    track_bundle = game["track_bundle"],
                    wheels = game["wheels"],
                    setup_mode = game["setup_mode"],
                    game_mode = game["game_mode"],
                    bonus_target = game["bonus_target"],
                    joker_lap_code = game["joker_lap_code"],
                    joker_lap_precondition_code = game["joker_lap_precondition_code"], 
                )
                game_data = jsonable_encoder(game_data)

            #check if joker lap should be increased:
            if game_data["joker_lap_code"] == obj.data.target_code:
                if not game_data["joker_lap_precondition_code"]:
                    user_data["joker_laps_counter"] += 1
                elif game_data["joker_lap_precondition_code"] == user_data["last_recognized_target"]:
                    user_data["joker_laps_counter"] += 1

            if obj.data.target_code == target_code.start_finish:
                if user_data["last_lap_timestamp"]:
                    user_data["laps_completed"] += 1 #only add a lap after the start line has been crossed the second time
                    if( user_data["laps_completed"] <= 1 ):
                        new_lap_time:timedelta = obj.data.crossing_time.astimezone(timezone.utc) - (datetime.strptime(user_data["last_lap_timestamp"], '%Y-%m-%dT%H:%M:%S.%f%z'))
                    else:
                        new_lap_time:timedelta = obj.data.crossing_time.astimezone(timezone.utc) - (datetime.strptime(user_data["last_lap_timestamp"], '%Y-%m-%dT%H:%M:%S.%f')).astimezone(timezone.utc)
                    user_data["last_lap"] = str(new_lap_time.total_seconds())
                    if user_data["best_lap"]:
                        bestLap = timedelta(seconds=float(user_data["best_lap"]))
                        if bestLap > new_lap_time:
                            user_data["best_lap"] = str(new_lap_time.total_seconds())
                    else:
                        user_data["best_lap"] = str(new_lap_time.total_seconds())
                    user_data["last_lap_timestamp"] = obj.data.crossing_time
                else:
                    #this is only active when the target finished is crossed the first time, as in that case, there is no last_lap_timestamp set:
                    #for the first lap, we count the time since the signal time, not the first crossing. This is how it is done in the drift app.
                    user_data["last_lap_timestamp"] = user_data["start_data"]["signal_time"]

            if obj.data.score>0:
                user_data["total_score"] += obj.data.score
                if obj.data.target_code == target_code.speed_drift:
                    if user_data["best_speed_drift"] == None:
                        user_data["best_speed_drift"] = obj.data.score
                    else:
                        if obj.data.score > user_data["best_speed_drift"]:
                            user_data["best_speed_drift"] = obj.data.score
                if obj.data.target_code == target_code.angle_drift:
                    if user_data["best_angle_drift"] == None:
                        user_data["best_angle_drift"] = obj.data.score
                    else:
                        if obj.data.score > user_data["best_angle_drift"]:
                            user_data["best_angle_drift"] = obj.data.score
                if obj.data.target_code == target_code.threesixty:
                    if user_data["best_360_angle"] == None:
                        user_data["best_360_angle"] = obj.data.score
                    else:
                        if obj.data.score > user_data["best_360_angle"]:
                            user_data["best_360_angle"] = obj.data.score
                if obj.data.target_code == target_code.oneeighty:
                    if user_data["best_180_speed"] == None:
                        user_data["best_180_speed"] = obj.data.score
                    else:
                        if obj.data.score > user_data["best_180_speed"]:
                            user_data["best_180_speed"] = obj.data.score

            user_data["fith_last_recognized_target"] = user_data["forth_last_recognized_target"]
            user_data["forth_last_recognized_target"] = user_data["third_last_recognized_target"]
            user_data["third_last_recognized_target"] = user_data["second_last_recognized_target"]
            user_data["second_last_recognized_target"] = user_data["last_recognized_target"]
            user_data["last_recognized_target"] = obj.data.target_code
            user_data["last_target_timestamp"] = datetime.now()  

            updated_player = await driftapi_playerstatus_collection.update_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id, "user_id":playerStatusId["user_id"]},{"$set": user_data})

    elif eventType is StartEvent:
        set_user_id = jsonable_encoder(obj.user_id)
        playerStatusId = await driftapi_playerstatus_collection.find_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id, "user_id":set_user_id})
        if playerStatusId:
            user_data = PlayerStatusSchema(
                lobby_id = lobby_id,
                game_id = game_id,#obj.game_id,	#for safety
                user_id = obj.user_id,
                user_name = obj.user_name,
                stage_id = playerStatusId["stage_id"],
                laps_completed = playerStatusId["laps_completed"],
                target_code_counter=playerStatusId["target_code_counter"],
                total_score = playerStatusId["total_score"],
                total_time = playerStatusId["total_time"],
                best_lap = playerStatusId["best_lap"],
                last_lap = playerStatusId["last_lap"],
                last_lap_timestamp = playerStatusId["last_lap_timestamp"],
                last_target_timestamp = playerStatusId["last_target_timestamp"],
                best_speed_drift = playerStatusId["best_speed_drift"],
                best_angle_drift = playerStatusId["best_angle_drift"],
                best_360_angle = playerStatusId["best_360_angle"],
                best_180_speed = playerStatusId["best_180_speed"],
                last_recognized_target = playerStatusId["last_recognized_target"],
                second_last_recognized_target = playerStatusId["second_last_recognized_target"],
                third_last_recognized_target = playerStatusId["third_last_recognized_target"],
                forth_last_recognized_target = playerStatusId["forth_last_recognized_target"],
                fith_last_recognized_target = playerStatusId["fith_last_recognized_target"],
                joker_laps_counter = playerStatusId["joker_laps_counter"],
                enter_data = playerStatusId["enter_data"],
                start_data = obj.data,
                end_data = playerStatusId["end_data"]
            )
            user_data = jsonable_encoder(user_data)
            updated_player = await driftapi_playerstatus_collection.update_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id, "user_id":playerStatusId["user_id"]},{"$set": user_data})

    elif eventType is EndEvent:
        set_user_id = jsonable_encoder(obj.user_id)
        playerStatusId = await driftapi_playerstatus_collection.find_one({"lobby_id":lobby_id, "game_id":game_id, "stage_id":stage_id, "user_id":set_user_id})
        if playerStatusId:
            user_data = PlayerStatusSchema(
                lobby_id = lobby_id,
                game_id = game_id,#obj.game_id,	#for safety
                user_id = obj.user_id,
                user_name = obj.user_name,
                stage_id = playerStatusId["stage_id"],
                laps_completed = playerStatusId["laps_completed"],
                target_code_counter=playerStatusId["target_code_counter"],
                total_score = playerStatusId["total_score"],
                total_time = playerStatusId["total_time"],
                best_lap = playerStatusId["best_lap"],
                last_lap = playerStatusId["last_lap"],
                last_lap_timestamp = playerStatusId["last_lap_timestamp"],
                last_target_timestamp = playerStatusId["last_target_timestamp"],
                best_speed_drift = playerStatusId["best_speed_drift"],
                best_angle_drift = playerStatusId["best_angle_drift"],
                best_360_angle = playerStatusId["best_360_angle"],
                best_180_speed = playerStatusId["best_180_speed"],
                last_recognized_target = playerStatusId["last_recognized_target"],
                second_last_recognized_target = playerStatusId["second_last_recognized_target"],
                third_last_recognized_target = playerStatusId["third_last_recognized_target"],
                forth_last_recognized_target = playerStatusId["forth_last_recognized_target"],
                fith_last_recognized_target = playerStatusId["fith_last_recognized_target"],
                joker_laps_counter = playerStatusId["joker_laps_counter"],
                enter_data = playerStatusId["enter_data"],
                start_data = playerStatusId["start_data"],
                end_data = obj.data
            )
            user_data = jsonable_encoder(user_data)
            if user_data["start_data"] and user_data["end_data"]:
                totalRaceTime:timedelta = (datetime.strptime(user_data["end_data"]["finished_time"], '%Y-%m-%dT%H:%M:%S.%f%z')) - (datetime.strptime(user_data["start_data"]["signal_time"], '%Y-%m-%dT%H:%M:%S.%f%z'))
                user_data["total_time"] = str(totalRaceTime.total_seconds())

            user_data["total_score"] = user_data["end_data"]["total_score"]

            updated_player = await driftapi_playerstatus_collection.update_one({"lobby_id": lobby_id, "game_id": game_id, "stage_id":stage_id, "user_id": playerStatusId["user_id"]},{"$set": user_data})

    return "OK"#self.raceevent_db.insert(values)






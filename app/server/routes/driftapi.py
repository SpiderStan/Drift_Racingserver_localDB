from fastapi import APIRouter, Body, HTTPException
from fastapi.encoders import jsonable_encoder

from ..singletons import settings, logger

from ..database import (
    find_lobbies,
    get_lobby_data,
    add_lobby,
    delete_lobby,
    find_games,
    add_game,
    delete_game,
    get_game_data,
    get_playerstatus,
    delete_player,
    delete_players,
    delete_player_from_stage,
    delete_players_from_stage,
    start_stage,
    ping_game,
    insert_raceevent,
    get_targetstatus,
    get_highscorestatus,
    reset_highscorestatus,
    remove_player_highscorestatus,
)

from ..models.driftapi import (
    PingResponse,
	EndData,
	RaceEvent,
	EnterEvent,
	StartEvent,
	TargetEvent,
	EndEvent,
)

from ..models.racedisplay import (
    ErrorResponseModel,
    ResponseModel,
	PlayerStatusSchema,
	GameSchema,
    LobbySchema,
)

router = APIRouter()

# This event is triggered when a user enters a server uri in the app. The app can see if there actually is a server behind that uri and could for example show a green light, so that the user knows he entered the right server.
@router.get("/game/{lobby_id}/{stage_id}/{game_id}/ping", status_code=200, response_model = PingResponse, tags=["community_api"], description="Ping that is used from the app to determine if a race with this uri and race id exists. The response is used to synchronize the race settings in the app, see example response. All fields in the response are optional.")
async def ping(lobby_id: str, game_id:str, stage_id:int):
    game = await ping_game(lobby_id, game_id, stage_id)
    if game:
        reply = {"status": True}
        if game["start_time"]: reply["start_time"] = game["start_time"]
        if game["lap_count"]: reply["lap_count"] = game["lap_count"]
        if game["track_condition"]: reply["track_condition"] = game["track_condition"]
        if game["track_bundle"]: reply["track_bundle"] = game["track_bundle"]
        if game["wheels"]: reply["wheels"] = game["wheels"]
        if game["setup_mode"]: reply["setup_mode"] = game["setup_mode"]
        return reply
    raise HTTPException(status_code=404, detail="Item not found")

# This event is triggered when the user starts a run (free run, race, gymkhana) and after the loading is completed (the user sees the hud of the racer)
# it's purpose is for the server to control the car setup and if that matches with what is allowed for the race
@router.post("/game/{lobby_id}/{stage_id}/{game_id}/enter", status_code=201, tags=["community_api"], description="<p>This event is triggered when the user starts a run (free run, race, gymkhana) and after the loading is completed (the user sees the hud of the racer)</p><p>it's purpose is for the server to control the car setup and if that matches with what is allowed for the race</p>")
async def create_EnterEvent(lobby_id: str, game_id:str, stage_id:int, enterEvent:EnterEvent):
    res = await insert_raceevent(lobby_id, game_id, stage_id, enterEvent)
    return res

# This event is triggered when the user hits the "Start Motor" button the first time.
@router.post("/game/{lobby_id}/{stage_id}/{game_id}/start", status_code=201, tags=["community_api"], description="This event is triggered when the user hits the 'Start Motor' button the first time.")
async def create_StartEvent(lobby_id: str, game_id:str, stage_id:int, startEvent:StartEvent):
    res = await insert_raceevent(lobby_id, game_id, stage_id, startEvent)
    return res

# This event is triggered whenever a target is recognized
@router.post("/game/{lobby_id}/{stage_id}/{game_id}/target", status_code=201, tags=["community_api"], description="This event is triggered whenever a target is recognized")
async def create_TargetEvent(lobby_id: str, game_id:str, stage_id:int, targetEvent:TargetEvent):
    res = await insert_raceevent(lobby_id, game_id, stage_id, targetEvent)
    return res

# This event is triggered whenever a player shuts down the motor and finishes the run
@router.post("/game/{lobby_id}/{stage_id}/{game_id}/end", status_code=201, tags=["community_api"], description = "This event is triggered whenever a player shuts down the motor and finishes the run")
async def create_EndEvent(lobby_id: str, game_id:str, stage_id:int, endEvent:EndEvent):
    res = await insert_raceevent(lobby_id, game_id, stage_id, endEvent)
    return res

#--------------------------------------------------------------------------------------------
if settings.enable_racedisplay:
    # All of the below functions belong to the reference racing server and are not part of the actual Dr!ft Community API.

# currently not used:
#    # This is a debug function that you can use to query for the created race events.
#    @router.put("/game/{lobby_id}/{game_id}/events", status_code=200, tags=["racingserver_api"], description="This is a debug function that you can use to query for the created race events.")
#    async def get_Events(game_id:str, query:dict):
#        query["game_id"]=game_id
#        return db_client.find_raceevent(query)







    @router.post("/manage_lobby/find/", tags=["racingserver_api"])
    async def find_lobby(query:dict):
        res = await find_lobbies()
        return res

    @router.get("/manage_lobby/get/{lobby_id}/", tags=["racingserver_api"])
    async def get_lobby(lobby_id: str,):
        res = await get_lobby_data(lobby_id)
        return res

    @router.post("/manage_lobby/create", response_description="Lobby data added into the database")
    async def add_lobby_data(lobby: LobbySchema = Body(...)):
        lobby = jsonable_encoder(lobby)
        new_lobby = await add_lobby(lobby)
        return ResponseModel(new_lobby, "Lobby added successfully.")

    @router.delete("/manage_lobby/delete/{lobby_id}", response_description="Lobby data deleted from the database")
    async def delete_lobby_data(lobby_id: str):
        deleted_lobby = await delete_lobby(lobby_id)
        if deleted_lobby:
            return ResponseModel(
                "Lobby with lobby_id: {} removed".format(lobby_id), "Lobby deleted successfully"
            )
        return ErrorResponseModel(
            "An error occurred", 404, "Lobby with lobby_id {0} doesn't exist".format(lobby_id)
        )

    @router.get("/game/{lobby_id}/{game_id}/{stage_id}/playerstatus", status_code=200, tags=["racingserver_api"])
    async def get_scoreboard(lobby_id: str, game_id:str, stage_id:int):
        res = await get_playerstatus(lobby_id, game_id, stage_id)
        return res

    @router.get("/game/{lobby_id}/{game_id}/{stage_id}/{user_name}/targetstatus", status_code=200, tags=["racingserver_api"])
    async def get_targetboard(lobby_id: str, game_id:str, stage_id:int, user_name:str):
        res = await get_targetstatus(lobby_id, game_id, stage_id, user_name)
        return res

    @router.get("/game/{lobby_id}/highscores", status_code=200, tags=["racingserver_api"])
    async def get_highscoreboard(lobby_id: str):
        res = await get_highscorestatus(lobby_id)
        return res

    @router.delete("/game/{lobby_id}/reset/highscores", status_code=200, tags=["racingserver_api"])
    async def reset_highscoreboard(lobby_id: str):
        res = await reset_highscorestatus(lobby_id)
        return res

    @router.delete("/game/{lobby_id}/remove_player/{user_name}/highscores", status_code=200, tags=["racingserver_api"])
    async def remove_player_highscoreboard(lobby_id: str, user_name:str):
        res = await remove_player_highscorestatus(lobby_id, user_name)
        return

    @router.post("/manage_game/create/{lobby_id}/", response_description="Game data added into the database")
    async def add_game_data(lobby_id: str, game: GameSchema = Body(...)):
        game = jsonable_encoder(game)
        new_game = await add_game(lobby_id, game)
        return ResponseModel(new_game, "Game added successfully.")

    @router.delete("/manage_game/delete/{lobby_id}/{game_id}", response_description="Game data deleted from the database")
    async def delete_game_data(lobby_id: str, game_id: str):
        deleted_game = await delete_game(lobby_id, game_id)
        if deleted_game:
            return ResponseModel(
                "Game with game_id: {} removed".format(game_id), "Game deleted successfully"
            )
        return ErrorResponseModel(
            "An error occurred", 404, "Game with game_id {0} doesn't exist".format(game_id)
        )

    @router.get("/manage_game/reset/{lobby_id}/{game_id}/{stage_id}", status_code=200, tags=["racingserver_api"])
    async def reset_game(lobby_id: str, game_id:str, stage_id:int):
        res = await delete_players(lobby_id, game_id, stage_id)
        return res

    @router.get("/manage_game/reset_stage/{lobby_id}/{game_id}/{stage_id}", status_code=200, tags=["racingserver_api"])
    async def reset_stage(lobby_id: str, game_id:str, stage_id:int):
        res = await delete_players_from_stage(lobby_id, game_id, stage_id)
        return res

    @router.get("/manage_game/start_stage/{lobby_id}/{game_id}/{stage_id}", status_code=200, tags=["racingserver_api"])
    async def start_stage_game(lobby_id: str, game_id:str, stage_id:int):
        res = await start_stage(lobby_id, game_id, stage_id)
        return res
        
    @router.delete("/manage_game/reset_player/{lobby_id}/{game_id}/{user_name}", status_code=200, tags=["racingserver_api"])
    async def reset_player(lobby_id: str, game_id:str, user_name:str):
        res = await delete_player(lobby_id, game_id, user_name)
        return

    @router.delete("/manage_game/reset_player_from_stage/{lobby_id}/{game_id}/{stage_id}/{user_name}", status_code=200, tags=["racingserver_api"])
    async def reset_player_from_stage(lobby_id: str, game_id:str, stage_id:int, user_name:str):
        res = await delete_player_from_stage(lobby_id, game_id, stage_id, user_name)
        return

    @router.get("/manage_game/get/{lobby_id}/{game_id}/{stage_id}/", status_code=200, tags=["racingserver_api"])
    async def get_game(lobby_id: str, game_id:str, stage_id:int):
        res = await get_game_data(lobby_id, game_id, stage_id)
        return res

    @router.post("/manage_game/find/{lobby_id}/", tags=["racingserver_api"])
    async def find_game(lobby_id: str, query:dict):
        res = await find_games(lobby_id)
        return res

#--------------------------------------------------------------------------------------------
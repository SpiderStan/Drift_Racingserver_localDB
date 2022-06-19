import streamlit as st
import pandas as pd 
from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings
    
def app():

    #st.markdown("## Main Page")

# initialize emoji as a Session State variable
    if "lobby_emoji" not in st.session_state:
        st.session_state.lobby_emoji = "👪"
    if "" not in st.session_state:
        st.session_state.quit_emoji = "🚪" 
    if "emoji_ready" not in st.session_state:
        st.session_state.emoji_ready = "🚦"
    if "emoji_driving" not in st.session_state:
        st.session_state.emoji_driving = "🏎️"
    if "emoji_finish" not in st.session_state:
        st.session_state.emoji_finish = "🏁"
    if "back_emoji" not in st.session_state:
        st.session_state.back_emoji = "◀️"
    if "delete_emoji" not in st.session_state:
        st.session_state.delete_emoji = "💣"
    if "reset_emoji" not in st.session_state:
        st.session_state.reset_emoji = "🔄"
    if "download_emoji" not in st.session_state:
        st.session_state.download_emoji = "💾"
    if "show_game_emoji" not in st.session_state:
        st.session_state.show_game_emoji = "🔍"
    if "tweak_game_emoji" not in st.session_state:
        st.session_state.tweak_game_emoji = "⚙️"
    if "remove_emoji" not in st.session_state:
        st.session_state.remove_emoji = "❌"
    if "create_emoji" not in st.session_state:
        st.session_state.create_emoji = "✏️"
    if "track_dry_emoji" not in st.session_state:
        st.session_state.track_dry_emoji = "☀️"
    if "track_wet_emoji" not in st.session_state:
        st.session_state.track_wet_emoji = "🌧️"
    if "track_snow_emoji" not in st.session_state:
        st.session_state.track_snow_emoji = "❄️"
    if "track_gravel_emoji" not in st.session_state:
        st.session_state.track_gravel_emoji = "\U0001FAA8"  # rock         
    if "track_gravel_trap_emoji" not in st.session_state:
        st.session_state.track_gravel_trap_emoji = "🌫️"
    if "track_unknown_emoji" not in st.session_state:
        st.session_state.track_unknown_emoji = "🚧"
    if "false_start_emoji" not in st.session_state:
        st.session_state.false_start_emoji = "🛑" 
    if "award_1st_emoji" not in st.session_state:
        st.session_state.award_1st_emoji = "🥇" 
    if "award_2nd_emoji" not in st.session_state:
        st.session_state.award_2nd_emoji = "🥈" 
    if "award_3rd_emoji" not in st.session_state:
        st.session_state.award_3rd_emoji = "🥉" 
    if "award_bonus_emoji" not in st.session_state:
        st.session_state.award_bonus_emoji = "🏅"
    if "award_trophy_emoji" not in st.session_state:
        st.session_state.award_trophy_emoji = "🏆"
    if "statistics_emoji" not in st.session_state:
        st.session_state.statistics_emoji = "🧮"       
    if "time_emoji" not in st.session_state:
        st.session_state.time_emoji = "⏱️" 
    if "time2_emoji" not in st.session_state:
        st.session_state.time2_emoji = "⌚"
    if "distance_emoji" not in st.session_state:
        st.session_state.distance_emoji = "📏" 
    if "distance2_emoji" not in st.session_state:
        st.session_state.distance2_emoji = "📐" 
    if "average_speed_emoji" not in st.session_state:
        st.session_state.average_speed_emoji = "🏎️💨" 

    if 'lobby_id' in st.session_state:
        del st.session_state.lobby_id
        
    if st.button(f"Create New Lobby {st.session_state.create_emoji}"):
        st.session_state.nextpage = "create_lobby"
        st.experimental_rerun()

    if st.button(f"Join Lobby {st.session_state.lobby_emoji}"):
        st.session_state.nextpage = "select_lobby"
        st.experimental_rerun()

    if st.button(f"Delete Lobby {st.session_state.delete_emoji}"):
        st.session_state.nextpage = "delete_lobby"
        st.experimental_rerun()

    st.write("Available Lobbies:")
    result = fetch_post(f"{settings.driftapi_path}/driftapi/manage_lobby/find/", {})
    if result:
        result = pd.DataFrame( [{"lobby_id":r["lobby_id"]} for r in result if ("lobby_id" in r)] )
        st.write(result)

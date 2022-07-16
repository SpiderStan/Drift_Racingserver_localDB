import streamlit as st
import time

import pandas as pd 
from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings
    
def app():

    #st.markdown("## Main Page")

# initialize emoji as a Session State variable
    if "lobby_emoji" not in st.session_state:
        st.session_state.lobby_emoji = "👪"
    if "quit_emoji" not in st.session_state:
        st.session_state.quit_emoji = "🚪" 
    if "ready_emoji" not in st.session_state:
        st.session_state.ready_emoji = "🚦"
    if "driving_emoji" not in st.session_state:
        st.session_state.driving_emoji = "🏎️"
    if "finish_emoji" not in st.session_state:
        st.session_state.finish_emoji = "🏁"
    if "round_emoji" not in st.session_state:
        st.session_state.round_emoji = "🚩"           
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
    if "checkmark_emoji" not in st.session_state:
        st.session_state.checkmark_emoji = "✔️"   
    if "remove_emoji" not in st.session_state:
        st.session_state.remove_emoji = "❌"
    if "create_emoji" not in st.session_state:
        st.session_state.create_emoji = "✏️"
    if "track_emoji" not in st.session_state:
        st.session_state.track_emoji = "🛣️"
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
    if "points_emoji" not in st.session_state:
        st.session_state.points_emoji = "💯"
    if "target_emoji" not in st.session_state:
        st.session_state.target_emoji = "🎯"
    if "status_emoji" not in st.session_state:
        st.session_state.status_emoji = "🎮"           
    if "current_sector_emoji" not in st.session_state:
        st.session_state.current_sector_emoji = "🔵"         
    if "completed_sector_emoji" not in st.session_state:
        st.session_state.completed_sector_emoji = "🟢" 
    if "noncompleted_sector_emoji" not in st.session_state:
        st.session_state.noncompleted_sector_emoji = "🟡"
    if "skull_emoji" not in st.session_state:
        st.session_state.skull_emoji = "💀"
    if "training_emoji" not in st.session_state:
        st.session_state.training_emoji = "💪"

    if 'lobby_id' in st.session_state:
        del st.session_state.lobby_id

    m = st.markdown("""
    <style>
    div.stButton > button:first-child {
        color: white;
        height: 3em;
        width: 15em;
        border-radius:10px;
        border:3px solid #696969;
        font-size:20px;
        font-weight: bold;
        margin: auto;
        display: block;
    }

    div.stButton > button:active {
        position:relative;
        top:3px;
    }

    </style>""", unsafe_allow_html=True)

    placeholder1 = st.empty()
    placeholder2 = st.empty()
    placeholder3 = st.empty()
    
    with placeholder1.container():

        colM11, colM12, colM13, colM14 = st.columns(4)

        with colM11:
            if st.button(f"Create New Lobby {st.session_state.create_emoji}"):
                st.session_state.nextpage = "create_lobby"
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with colM12:
            if st.button(f"Join Lobby {st.session_state.lobby_emoji}"):
                st.session_state.nextpage = "select_lobby"
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with colM13:
            if st.button(f"Delete Lobby {st.session_state.delete_emoji}"):
                st.session_state.nextpage = "delete_lobby"
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                time.sleep(0.1)
                st.experimental_rerun()

        with colM14:
            if st.button(f"System Settings {st.session_state.tweak_game_emoji}"):
                st.session_state.nextpage = "system_settings"
                placeholder1.empty()
                placeholder2.empty()
                placeholder3.empty()
                time.sleep(0.1)
                st.experimental_rerun()

    # CSS to inject contained in a string
    hide_dataframe_row_index = """
                <style>
                .row_heading.level0 {display:none}
                .blank {display:none}
                </style>
    """
    # Inject CSS with Markdown
    st.markdown(hide_dataframe_row_index, unsafe_allow_html=True)

    with placeholder2.container():
        st.subheader("Available Lobbies:")
    
    with placeholder3.container():
        result = fetch_post(f"{settings.driftapi_path}/driftapi/manage_lobby/find/", {})
        if result:
            result = pd.DataFrame( [{"Lobby:":r["lobby_id"]} for r in result if ("lobby_id" in r)] )
            result = result.style.set_properties(**{
                'font-size': '20pt',
            })
            st.table(result)
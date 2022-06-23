import streamlit as st

from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger

def app():

    lobby_id = st.session_state.lobby_id        
    game_id = None

    st.write("Select Number of Stages for new Stage Race Game in Lobby " + str(lobby_id))

    with st.form("my_form"):        
        num_stages = st.slider("Choose Number of Stages", min_value=2, max_value=20, value=2, step=1, format=None, key=None, help="the number of stages in your event", on_change=None, disabled = False)

        if st.form_submit_button(f"Go to Stage Config (Part 1) {st.session_state.create_emoji}"):
            st.session_state.num_stages = num_stages
            st.session_state.nextpage = "create_stagerace_config"
            st.experimental_rerun()

    if st.button(f"Back {st.session_state.back_emoji}"):
        st.session_state.nextpage = "main_page"
        st.experimental_rerun()
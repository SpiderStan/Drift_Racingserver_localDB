import streamlit as st

from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger

def app():

    lobby_id = st.session_state.lobby_id        
    game_id = None

    st.write("Select Game from Lobby " + str(lobby_id))

    if 'game_id' not in st.session_state:
        with st.form("my_form"):
            result = fetch_post(f"{settings.driftapi_path}/driftapi/manage_game/find/{lobby_id}", {})
            if result:
                result = [r["game_id"] for r in result if ("game_id" in r.keys())]
                game_id = st.selectbox(label="Choose Game", options=result)
                stage_id = 1
                if st.form_submit_button(f"Show {st.session_state.show_game_emoji}"):
                    st.session_state.game_id = game_id
                    st.session_state.stage_id = 1
                    game = fetch_get(f"{settings.driftapi_path}/driftapi/manage_game/get/{lobby_id}/{game_id}/{stage_id}/")
                    if(game["num_stages"] == 1):
                        st.session_state.num_stages = 1
                        st.session_state.nextpage = "racedisplay"
                    else:
                        st.session_state.num_stages = game["num_stages"]
                        st.session_state.nextpage = "stage_racedisplay"   
                    st.experimental_rerun()
    else:
        st.session_state.nextpage = "racedisplay"
        st.experimental_rerun()

    if st.button(f"Back to Main Menu of Lobby {st.session_state.back_emoji}"):
        st.session_state.nextpage = "main_page"
        st.experimental_rerun()
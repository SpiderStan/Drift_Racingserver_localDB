import streamlit as st
import time

from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger

def app():

    st.session_state.new_stage_event = False
    st.session_state.new_game = False

    lobby_id = st.session_state.lobby_id        
    game_id = None

    st.subheader("Select Game from Lobby " + str(lobby_id))

    placeholder1 = st.empty()
    placeholder2 = st.empty()

    with placeholder1.container():
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
                        st.session_state.num_stages = game["num_stages"]
                        if(game["game_mode"] == "RACE"):
                            if(game["num_stages"] == 1):
                                st.session_state.game_track_images_set = False
                                st.session_state.game_track_images = None
                                st.session_state.show_awards = False
                                st.session_state.nextpage = "racedisplay"
                            else:
                                st.session_state.game_track_images_set = [False] * 20
                                st.session_state.game_track_images = [None] * 20
                                st.session_state.show_awards = False
                                st.session_state.nextpage = "stage_racedisplay"
                        elif(game["game_mode"] == "LAP_RACE"):
                            if(game["num_stages"] == 1):
                                st.session_state.game_track_images_set = False
                                st.session_state.game_track_images = None
                                st.session_state.show_awards = False
                                st.session_state.nextpage = "lapracedisplay"
                            else:
                                st.session_state.game_track_images_set = [False] * 20
                                st.session_state.game_track_images = [None] * 20
                                st.session_state.show_awards = False
                                st.session_state.nextpage = "stage_racedisplay"
                        elif(game["game_mode"] == "TIME_RACE"):
                            if(game["num_stages"] == 1):
                                st.session_state.game_track_images_set = False
                                st.session_state.game_track_images = None
                                st.session_state.show_awards = False
                                st.session_state.nextpage = "timeracedisplay"
                            else:
                                st.session_state.game_track_images_set = [False] * 20
                                st.session_state.game_track_images = [None] * 20
                                st.session_state.show_awards = False
                                st.session_state.nextpage = "stage_racedisplay"
                        elif(game["game_mode"] == "ELIMINATION"):
                            if(game["num_stages"] == 1):
                                st.session_state.game_track_images_set = False
                                st.session_state.game_track_images = None
                                st.session_state.show_awards = False
                                st.session_state.nextpage = "eliminationracedisplay"
                            else:
                                st.session_state.game_track_images_set = [False] * 20
                                st.session_state.game_track_images = [None] * 20
                                st.session_state.show_awards = False
                                st.session_state.nextpage = "stage_racedisplay"
                        elif(game["game_mode"] == "GYMKHANA"):
                            if(game["num_stages"] == 1):
                                st.session_state.game_track_images_set = False
                                st.session_state.game_track_images = None
                                st.session_state.show_awards = False
                                st.session_state.nextpage = "racedisplay"
                            else:
                                st.session_state.game_track_images_set = [False] * 20
                                st.session_state.game_track_images = [None] * 20
                                st.session_state.show_awards = False
                                st.session_state.nextpage = "stage_racedisplay"
                        elif(game["game_mode"] == "GYMKHANA_TRAINING"):
                            if(game["num_stages"] == 1):
                                st.session_state.game_track_images_set = False
                                st.session_state.game_track_images = None
                                st.session_state.show_awards = False
                                st.session_state.nextpage = "gymkhana_training_racedisplay"
                            else:
                                st.session_state.game_track_images_set = [False] * 20
                                st.session_state.game_track_images = [None] * 20
                                st.session_state.show_awards = False
                                st.session_state.nextpage = "stage_racedisplay"
                        placeholder1.empty()
                        placeholder2.empty()
                        time.sleep(0.1)
                        st.experimental_rerun()
        else:
            st.session_state.nextpage = "racedisplay"
            placeholder1.empty()
            placeholder2.empty()
            time.sleep(0.1)
            st.experimental_rerun()

    with placeholder2.container():
        if st.button(f"Back {st.session_state.back_emoji}"):
            st.session_state.nextpage = "main_page"
            placeholder1.empty()
            placeholder2.empty()
            time.sleep(0.1)
            st.experimental_rerun()
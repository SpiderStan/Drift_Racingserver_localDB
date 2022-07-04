import streamlit as st
import time
import hashlib

from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def app():

    lobby_id = None

    placeholder1 = st.empty()
    placeholder2 = st.empty()

    with placeholder1.container():        
        if 'lobby_id' not in st.session_state:
            with st.form("my_form"):
                result = fetch_post(f"{settings.driftapi_path}/driftapi/manage_lobby/find/", {})
                if result:
                    result = [r["lobby_id"] for r in result if ("lobby_id" in r.keys())]
                    lobby_id = st.selectbox(label="Choose Lobby to join:", options=result)
                    password = st.text_input("Enter Lobby Password (leave empty if no password set):", value="", max_chars=None, key=None, type="password", help=None, autocomplete=None, on_change=None, disabled=False)
                    if st.form_submit_button(f"Join {st.session_state.lobby_emoji}"):
                        result = fetch_get(f"{settings.driftapi_path}/driftapi/manage_lobby/get/{lobby_id}/")
                        pw_hash = make_hashes(password)
                        if (result["password"] == pw_hash):
                            st.session_state.lobby_id = lobby_id
                            st.session_state.nextpage = "main_page"
                        else:
                            st.session_state.nextpage = "pre_mainpage"
                            st.error("Sorry wrong password, going back to main menu...")
                            time.sleep(1)
                        placeholder1.empty()
                        placeholder2.empty()
                        time.sleep(0.1)
                        st.experimental_rerun()
        else:
            st.session_state.nextpage = "main_page"
            placeholder1.empty()
            placeholder2.empty()
            time.sleep(0.1)
            st.experimental_rerun()

    with placeholder2.container():        
        if st.button(f"Back {st.session_state.back_emoji}"):
            st.session_state.nextpage = "pre_mainpage"
            placeholder1.empty()
            placeholder2.empty()
            time.sleep(0.1)
            st.experimental_rerun()
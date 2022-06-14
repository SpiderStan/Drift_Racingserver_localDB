import streamlit as st
import time
import hashlib

from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def app():

    lobby_id = None

    with st.form("my_form"):
        result = fetch_post(f"{settings.driftapi_path}/driftapi/manage_lobby/find/", {})
        if result:
            result = [r["lobby_id"] for r in result if ("lobby_id" in r.keys())]
            lobby_id = st.selectbox(label="Choose Lobby for deletion:", options=result)
            password = st.text_input("Enter Lobby Password (leave empty if no password set):", value="", max_chars=None, key=None, type="password", help=None, autocomplete=None, on_change=None, disabled=False)
            if st.form_submit_button(f"Delete {st.session_state.delete_emoji}"):
                result = fetch_get(f"{settings.driftapi_path}/driftapi/manage_lobby/get/{lobby_id}/")
                pw_hash = make_hashes(password)
                if (result["password"] == pw_hash):
                    result = fetch_delete(f"{settings.driftapi_path}/driftapi/manage_lobby/delete/{lobby_id}")
                else:
                    st.error("Sorry wrong password, going back to main menu...")
                time.sleep(1)
                st.session_state.lobby_id = None
                st.session_state.game_id = None
                st.session_state.stage_id = 1
                st.session_state.num_stages = 1
                st.session_state.nextpage = "pre_mainpage"
                st.experimental_rerun()

    if st.button(f"Back {st.session_state.back_emoji}"):
        st.session_state.nextpage = "pre_mainpage"
        st.experimental_rerun()

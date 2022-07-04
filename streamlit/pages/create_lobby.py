import streamlit as st
import time

import hashlib

from zoneinfo import ZoneInfo #to set the timezone to german time
from enum import Enum
from datetime import datetime, timezone, timedelta
from  .session import fetch_post, fetch_put, fetch_get, fetch_delete
from .singletons import settings, logger
from .model import track_condition, track_bundle, wheels, setup_mode, target_code

#  not used at the moment
def createLobbyOptionContainer(label:str, options:Enum):
    with st.container():
        columnLeft, columnRight = st.columns(2)
        with columnLeft:
            enabled = st.checkbox("Sync. "+label, value=False, key=None, help=None, on_change=None)
#            enabled = st.checkbox("Enable "+label, value=False, key=None, help=None, on_change=None)
        with columnRight:
            selected = st.selectbox(label=label, options=[e.value for e in options])
        if enabled:
            return {label:selected}
        else:
            return {}
        
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def app():

    placeholder1 = st.empty()
    placeholder2 = st.empty()

    with placeholder1.container():        
        with st.form("my_form", clear_on_submit=True):
            lobbyOptions = {}
            lobby_id = st.text_input("Create new Lobby ID:", value="Lobby1", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, disabled=False)
            password = st.text_input("Set Password for Lobby (or leave empty for empty password):", value="", max_chars=None, key=None, type="password", help=None, autocomplete=None, on_change=None, disabled=False)            

            submitted = st.form_submit_button(f"Create {st.session_state.create_emoji}")

            if submitted:
            
                    pw_hash = make_hashes(password)
            
                    body = {
                        "lobby_id" : lobby_id,
                        "password" : pw_hash,
                    }

                    result = fetch_post(f"{settings.driftapi_path}/driftapi/manage_lobby/create", body)

                    st.session_state.nextpage = "main_page"
                    st.session_state.lobby_id = lobby_id
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
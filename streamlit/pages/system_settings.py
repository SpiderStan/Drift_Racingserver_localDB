import streamlit as st
import pandas as pd 
from .singletons import settings
    
def app():

    with st.form("App Title Form", clear_on_submit=True):
        app_title = st.text_input("App Title: Current App Title is " + str(st.session_state.app_title), value=f"🏎️ DR!FT Racingserver ⛽", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, disabled=False)

        submitted = st.form_submit_button(f"Change {st.session_state.create_emoji}")

        if submitted:
            st.session_state.app_title = app_title
            st.experimental_rerun()

    with st.form("IP Address Form", clear_on_submit=True):
        ip_address = st.text_input("IP Address: Current IP Address is " + str(st.session_state.ip_address), value="127.0.0.1", max_chars=None, key=None, type="default", help=None, autocomplete=None, on_change=None, disabled=False)

        submitted = st.form_submit_button(f"Change {st.session_state.create_emoji}")

        if submitted:
            st.session_state.ip_address = ip_address
            st.experimental_rerun()

    if st.button(f"Back {st.session_state.back_emoji}"):
        st.session_state.nextpage = "pre_mainpage"
        st.experimental_rerun()

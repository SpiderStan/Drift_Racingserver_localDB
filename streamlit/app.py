import streamlit as st
import os
import base64
from PIL import Image
import configparser

# Custom imports 
from multipage import MultiPage
from pages import pre_mainpage, mainpage, create_lobby, select_lobby, delete_lobby, create_race_game, create_lap_race_game, create_time_race_game, create_gymkhana_game, create_gymkhana_training, create_stagerace_config, create_pre_stagerace_game, create_stagerace_game, select_race, delete_race, racedisplay, lapracedisplay, timeracedisplay, sectordisplay, stage_racedisplay, gymkhana_training_racedisplay, download_race, download_laprace, download_timerace, download_stagerace, remove_player_from_race, remove_player_from_stage_part1, remove_player_from_stage_part2, reset_stage, statistics, statistics_stage, download_statistics, highscore_list, remove_player_from_highscore_list, system_settings # import your pages here

def _max_width_(prcnt_width:int = 75):
    max_width_str = f"max-width: {prcnt_width}%;"
    st.markdown(f""" 
                <style> 
                .reportview-container .main .block-container{{{max_width_str}}}
                </style>    
                """, 
                unsafe_allow_html=True,
    )

# added app_meta for icon and tooltip
def app_meta(icon):

    # Set website details
    st.set_page_config(page_title ="DR!FT Racingserver", 
                       page_icon=icon, 
                       layout='wide')
    
    # set sidebar width
    st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 300px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 300px;
        margin-left: -300px;
    }
    </style>
    """,
    unsafe_allow_html=True,
    )

# different black backgrounds from pixabay:
# https://cdn.pixabay.com/photo/2014/02/04/20/22/abstract-258338_960_720.png (from: https://pixabay.com/de/illustrations/abstrakt-linien-regenbogen-bunt-258338/)
# https://cdn.pixabay.com/photo/2014/06/16/23/39/black-370118_960_720.png (from https://pixabay.com/de/illustrations/schwarz-hintergrund-textur-370118/ )
# https://cdn.pixabay.com/photo/2016/04/04/12/43/texture-1306790_960_720.jpg
# https://cdn.pixabay.com/photo/2016/10/22/01/54/wood-1759566_960_720.jpg
# https://cdn.pixabay.com/photo/2015/08/04/09/00/backdrop-874452_960_720.jpg
# https://cdn.pixabay.com/photo/2016/09/07/21/51/black-skin-1652717_960_720.jpg
# https://cdn.pixabay.com/photo/2013/02/21/19/12/charcoal-84670_960_720.jpg
# https://cdn.pixabay.com/photo/2016/09/08/17/38/texture-1654986_960_720.jpg
# https://cdn.pixabay.com/photo/2015/09/09/17/12/interior-931947_960_720.jpg
# https://cdn.pixabay.com/photo/2016/11/19/15/04/black-1839731_960_720.jpg

# added background hack for URL images
def set_bg_hack_url():
    '''
    A function to unpack an image from url and set as bg.
    Returns
    -------
    The background.
    '''
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url("https://cdn.pixabay.com/photo/2014/02/04/20/22/abstract-258338_960_720.png");
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

def set_bg_hack():
    '''
    A function to unpack an image from root folder and set as bg.
    The bg will be static and won't take resolution of device into account.
    Returns
    -------
    The background.
    '''
    # set bg name
    main_bg = "background/background.png"
    main_bg_ext = "png"
        
    st.markdown(
         f"""
         <style>
         .stApp {{
             background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()});
             background-size: cover
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

if __name__ == '__main__':
    # Create an instance of the app 

# apply app meta and background image
    app_meta('🏎')
    set_bg_hack()
#    set_bg_hack_url()

    config = configparser.ConfigParser()
    config.read('config/config.ini')
    rserver = config['racingserver']
    
    st.session_state.app_title = rserver.get('serverName', f"🏎️ DR!FT Racingserver Test ⛽")
    st.session_state.ip_address = rserver.get('serverIPaddress', '127.0.0.1')
 
    app = MultiPage()

    if "app_title" not in st.session_state:
        st.session_state.app_title = f"🏎️ DR!FT Racingserver ⛽"

    if "ip_address" not in st.session_state:
        st.session_state.ip_address = "127.0.0.1"
    
# Title of the main page
    st.title(st.session_state.app_title)
    
# Add all your applications (pages) here
    app.add_page("pre_mainpage", pre_mainpage.app)
    app.add_page("create_lobby", create_lobby.app)
    app.add_page("select_lobby", select_lobby.app)
    app.add_page("delete_lobby", delete_lobby.app)
    app.add_page("system_settings", system_settings.app)
    app.add_page("main_page", mainpage.app)
    app.add_page("create_race_game", create_race_game.app)
    app.add_page("create_gymkhana_game", create_gymkhana_game.app)
    app.add_page("create_gymkhana_training", create_gymkhana_training.app)
    app.add_page("create_lap_race_game", create_lap_race_game.app)
    app.add_page("create_time_race_game", create_time_race_game.app)
    app.add_page("create_pre_stagerace_game", create_pre_stagerace_game.app)
    app.add_page("create_stagerace_config", create_stagerace_config.app)
    app.add_page("create_stagerace_game", create_stagerace_game.app)
    app.add_page("stage_racedisplay", stage_racedisplay.app)
    app.add_page("gymkhana_training_racedisplay", gymkhana_training_racedisplay.app)
    app.add_page("select_race", select_race.app)
    app.add_page("delete_race", delete_race.app)
    app.add_page("statistics", statistics.app)
    app.add_page("racedisplay", racedisplay.app)
    app.add_page("lapracedisplay", lapracedisplay.app)
    app.add_page("timeracedisplay", timeracedisplay.app)
    app.add_page("sectordisplay", sectordisplay.app)
    app.add_page("download_race", download_race.app)
    app.add_page("download_laprace", download_laprace.app)
    app.add_page("download_timerace", download_timerace.app)
    app.add_page("download_stagerace", download_stagerace.app)
    app.add_page("remove_player_from_race", remove_player_from_race.app)
    app.add_page("remove_player_from_stage_part1", remove_player_from_stage_part1.app)
    app.add_page("remove_player_from_stage_part2", remove_player_from_stage_part2.app)
    app.add_page("reset_stage", reset_stage.app)
    app.add_page("statistics_stage", statistics_stage.app)
    app.add_page("download_statistics", download_statistics.app)
    app.add_page("highscore_list", highscore_list.app)
    app.add_page("remove_player_from_highscore_list", remove_player_from_highscore_list.app)

    print(app.pages)

    # The main app
    app.run()
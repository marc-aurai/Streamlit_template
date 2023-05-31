import streamlit as st
from PIL import Image

import pages.utils_streamlit.AWS_login as AWS_login
from pages.tabs.voetbal import TAB_voetbal
from pages.tabs.voetbal_stats import TAB_voetbal_stats
from pages.utils_streamlit.AWS_login import check_password as check_password_AWS
from pages.utils_streamlit.login import check_password
from pages.utils_streamlit.video import ST_readVideo, videoMetaData

if "message_history" not in st.session_state:
    st.session_state.message_history = []


@st.cache_data(show_spinner="Een momentje...")
def load_metadataVideosFrom_S3Bucket():
    df = videoMetaData()
    return df


@st.cache_data(show_spinner="Een momentje...")
def load_images():
    return Image.open("assets/image/southfields_logo.png")


def streamlit_page_config():
    st.set_page_config(
        page_title="Southfields AI",
        page_icon=Image.open("assets/image/SF_icon.png"),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                button[title="View fullscreen"]{visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    multi_css = f"""
            <style>
            .stMultiSelect div div div div div:nth-of-type(2) {{visibility: hidden;}}
            .stMultiSelect div div div div div:nth-of-type(2)::before {{visibility: visible; content:"Maak eventueel een keuze"}}
            </style>
            """
    st.markdown(multi_css, unsafe_allow_html=True)


streamlit_page_config()
SF_logo = load_images()

try:
    df_videoMetadata = load_metadataVideosFrom_S3Bucket()
except:
    print("Access AWS Probably denied.")

login_field, opt = st.columns(2)
with login_field:
    if AWS_login.AWS:
        AWS_check = check_password_AWS()
        streamlit_check = False
    else:
        streamlit_check = check_password()
        AWS_check = False


if AWS_check or streamlit_check:
    tab_voetbal, tab_voetbalStats, tab_voetbalVideos, tab_handbal, tab_rugby = st.tabs(
        ["Voetbal", "Voetbal Stats", "Voetbal Videos", "Handbal", "Rugby League"]
    )
    with tab_voetbal:
        (
            df_match_selected,
            df_playerStats_selected,
            df_player_stats,
            df_formationHome,
            df_formationAway,
            logo_folder,
            home_team,
            away_team,
        ) = TAB_voetbal()

        with tab_voetbalStats:
            TAB_voetbal_stats(
                df_match_selected,
                df_playerStats_selected,
                df_player_stats,
                df_formationHome,
                df_formationAway,
                logo_folder,
                home_team,
                away_team,
            )

        with tab_voetbalVideos:
            try:
                ST_readVideo(df_videoMetadata, df_match_selected.date.values[0])
            except:
                print("AWS Access was denied.")

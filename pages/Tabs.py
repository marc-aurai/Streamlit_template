import streamlit as st
from PIL import Image

from pages.utils_streamlit.login import check_password
from pages.tabs.voetbal_tab import voetbal_tab

if "message_history" not in st.session_state:
    st.session_state.message_history = []


@st.cache_data(show_spinner="Een momentje...")
def _loadImages():
    return Image.open("assets/image/aurai_logo.png")


def _streamlitPageConfig():
    st.set_page_config(
        page_title="Southfields AI",
        page_icon=Image.open("assets/image/aurai_logo.png"),
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


_streamlitPageConfig()
SF_logo = _loadImages()


login_field, opt = st.columns(2)
with login_field:
    streamlit_check = check_password()

if streamlit_check:
    tab_voetbal, tab_handbal, tab_rugby = st.tabs(
        ["Voetbal", "Handbal", "Rugby League"]
    )
    with tab_voetbal:
        voetbal_tab("Welcome", "To tab Voetbal")
    with tab_handbal:
        voetbal_tab("Hi", "To tab Handbal")
    with tab_rugby:
        voetbal_tab("Hallo", "To tab Rugby")
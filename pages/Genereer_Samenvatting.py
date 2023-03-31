import calendar
import datetime
import uuid

import pytz
import streamlit as st
from PIL import Image
from streamlit_chat import message as st_message

from pages.utils_streamlit.st_login import check_password

if "message_history" not in st.session_state:
    st.session_state.message_history = []


@st.cache_data(show_spinner="Een momentje...")
def load_images():
    return Image.open("assets/image/southfields_logo.png")


def streamlit_page_config():
    st.set_page_config(
        page_title="Genereer Samenvatting",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def get_datetime() -> str:
    created_at = datetime.datetime.now(pytz.timezone("Europe/Amsterdam"))
    created_at_formatted = (
        str(calendar.month_name[created_at.month])
        + " "
        + str(created_at.day)
        + ": "
        + str(created_at.strftime("%H:%M:%S"))
    )
    return created_at_formatted

if check_password():
    streamlit_page_config()
    st.sidebar.success("Genereer een samenvatting op deze demo pagina.")
    image = load_images()
    st.image(image)

    st.write(""" # South-Fields Demo """)

    temperature_GPT = st.sidebar.number_input(
        label="Model Temperature", min_value=0.0, max_value=1.0, value=0.5
    )

    input_data = st.text_area(
        label="Wedstrijd Data", value="..", height=200, max_chars=None
    )
    submit = st.button("Genereer")

    if submit:
        with st.spinner("Even een samenvatting aan het schrijven, momentje..."):
            if input_data != "..":
                generated_output = "\nGPT not implemented yet." #streamlit_prompt_curie(input_data, TEMP=temperature_GPT)
                _datetime = get_datetime()
                st.session_state.message_history.append(_datetime + generated_output)
                for message_ in reversed(st.session_state.message_history):
                    st_message(
                        message_, avatar_style="bottts-neutral", seed="Aneka", is_user=False
                    )

    st.info(
        """Model temperature:\n - Hogere waarden zoals 0.8 zal de output meer random 
            maken\n - Lagere waarden zoals 0.2 zal de output meer gericht en deterministisch maken""",
        icon="ℹ️",
    )

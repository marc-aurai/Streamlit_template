import calendar
import datetime
import ast

import pandas as pd
import pytz
import streamlit as st
from PIL import Image
from streamlit_chat import message as st_message

from pages.utils_streamlit.chat import (
    GPT_3,
    GPT_chat_completion,
    GPT_chat_completion_streaming,
)
from pages.utils_streamlit.login import check_password
from pages.utils_streamlit.plot_winstreak import plot_winstreak
from pages.utils_streamlit.selections import (
    ST_select_match_date,
    ST_select_match,
    ST_get_data_match,
    ST_select_injury_home,
    ST_select_injury_away,
    ST_select_trainers,
)

if "message_history" not in st.session_state:
    st.session_state.message_history = []


@st.cache_data(show_spinner="Een momentje...")
def load_images():
    return Image.open("assets/image/southfields_logo.png")


@st.cache_data(show_spinner="Een momentje...")
def load_dataset() -> pd.DataFrame:  # Elke dag bijvoorbeeld als job schedulen
    df = pd.read_csv("./pages/data/eredivisie.csv", sep=",")
    df = df.sort_values(by="date", ascending=False)
    return df


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
    df = load_dataset()
    st.image(image)
    st.write(""" # Southfields AI Tool """)

    # SIDEBAR
    TOKENS = st.sidebar.number_input(
        label="Maximum length (Tokens)", min_value=50, max_value=500, value=350
    )
    temperature_GPT = st.sidebar.number_input(
        label="Model Temperature", min_value=0.0, max_value=1.0, value=0.4
    )
    openai_model = st.sidebar.selectbox(
        "Selecteer een model",
        (
            "gpt-3.5-turbo",
            "curie:ft-southfields-2023-04-05-11-53-31",
            "davinci:ft-southfields-2023-04-07-18-26-14",
        ),
    )
    st.sidebar.success("Geselecteerd: " + str(openai_model))

    # Main page
    select_date, select_match = st.columns(2)
    matches_on_date = ST_select_match_date(df, select_date)
    selected_match = ST_select_match(select_match, matches_on_date)
    match_prompt, match_streak_home, match_streak_away, home_team, away_team, select_match_injuries = ST_get_data_match(df, selected_match)
    select_injury_home, select_injury_away = st.columns(2)
    match_prompt = ST_select_injury_home(match_prompt, select_injury_home, select_match_injuries)
    match_prompt = ST_select_injury_away(match_prompt, select_injury_away, select_match_injuries)
    select_trainers, select_optioneel = st.columns(2)
    match_prompt = ST_select_trainers(match_prompt, select_trainers, select_match_injuries)
    

    input_data = st.text_area(
        label="Wedstrijd Data", value=match_prompt, height=400, max_chars=None
    )
    submit = st.button("Genereer")

    if submit:
        with st.spinner("Even een samenvatting aan het schrijven, momentje..."):
            if input_data != "..":
                if str(openai_model) in ("gpt-3.5-turbo", "gpt-4"):
                    generated_output = GPT_chat_completion_streaming(
                        prompt=input_data,
                        model_engine=openai_model,
                        MAX_TOKENS=TOKENS,
                        TEMP=temperature_GPT,
                    )

                    plot_col1, plot_col2, plot_col3 = st.columns(3)
                    try:
                        with plot_col1:
                            st.pyplot(
                                plot_winstreak(
                                    match_streak_home, title_plt=str(home_team) + "\n"
                                )
                            )
                    except:
                        with plot_col1:
                            st.warning("Winstreak Home team not available.")
                    try:
                        with plot_col3:
                            st.pyplot(
                                plot_winstreak(
                                    match_streak_away, title_plt=str(away_team) + "\n"
                                )
                            )
                    except:
                        with plot_col3:
                            st.warning("Winstreak Away team not available.")

                    chats = st.empty()
                    completion_chunks = []
                    _datetime = get_datetime()
                    completion_chunks.append(str(_datetime) + "\n\n")
                    for chunk in generated_output:
                        try:
                            completion_chunks.append(chunk.choices[0].delta.content)
                        except:
                            completion_chunks.append("")
                        with chats.container():
                            st.write("".join(completion_chunks).strip())

                if str(openai_model) in (
                    "curie:ft-southfields-2023-04-05-11-53-31",
                    "davinci:ft-southfields-2023-04-07-18-26-14",
                ):
                    generated_output = GPT_3(
                        prompt=input_data,
                        model_engine=openai_model,
                        MAX_TOKENS=TOKENS,
                        TEMP=temperature_GPT,
                    )

                st.session_state.message_history.append(
                    "".join(completion_chunks).strip()
                )
                for message_ in reversed(st.session_state.message_history):
                    st_message(
                        message_,
                        avatar_style="bottts-neutral",
                        seed="Aneka",
                        is_user=False,
                    )

    st.info(
        """Model temperature:\n - Hogere waarden zoals 0.8 zal de output meer random 
            maken\n - Lagere waarden zoals 0.2 zal de output meer gericht en deterministisch maken""",
        icon="ℹ️",
    )

import pandas as pd
import streamlit as st
from PIL import Image

from pages.utils_streamlit.login_aws import check_password as check_password_AWS
from pages.utils_streamlit.login import check_password
from pages.utils_streamlit.selections import (
    ST_select_match_date,
    ST_select_match,
    ST_get_data_match,
    ST_select_injury_home,
    ST_select_injury_away,
    ST_select_trainers,
    ST_select_rank,
    ST_select_formation,
    ST_select_goals,
)
from pages.utils_streamlit.generate import generate_completion, generate_winstreak_plots

if "message_history" not in st.session_state:
    st.session_state.message_history = []


@st.cache_data(show_spinner="Een momentje...")
def load_images():
    return Image.open("assets/image/southfields_logo.png")


@st.cache_data(show_spinner="Een momentje...")
def load_dataset() -> pd.DataFrame:  # Elke dag bijvoorbeeld als job schedulen
    df = pd.read_csv("./pages/data/eredivisie.csv", sep=",")
    df = df.sort_values(by="date", ascending=False)
    df['date'] = df['date'].str.replace('Z', '')
    return df

@st.cache_data(show_spinner="Een momentje...")
def load_dataset_player_stats() -> pd.DataFrame:  # Elke dag bijvoorbeeld als job schedulen
    df = pd.read_csv("./pages/data/eredivisie_playerstats.csv", sep=",")
    df = df.sort_values(by="date", ascending=False)
    df['date'] = df['date'].str.replace('Z', '')
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


if check_password_AWS():
    streamlit_page_config()
    st.sidebar.success("Genereer een samenvatting op deze demo pagina.")
    image = load_images()
    df = load_dataset()
    df_player_stats = load_dataset_player_stats()
    st.image(image)
    st.write(""" # Southfields AI Tool """)

    # SIDEBAR
    TOKENS = st.sidebar.number_input(
        label="Maximum length (Tokens)", min_value=20, max_value=800, value=400
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

    # MAIN PAGE
    select_date, select_match = st.columns(2)
    matches_on_date = ST_select_match_date(df, select_date)
    selected_match = ST_select_match(select_match, matches_on_date)
    (
        match_prompt,
        match_streak_home,
        match_streak_away,
        home_team,
        away_team,
        select_match_injuries,
    ) = ST_get_data_match(df, selected_match)

    # select_cards_home, select_cards_away = st.columns(2)

    select_injury_home, select_injury_away = st.columns(2)
    match_prompt = ST_select_injury_home(
        match_prompt, select_injury_home, select_match_injuries
    )
    match_prompt = ST_select_injury_away(
        match_prompt, select_injury_away, select_match_injuries
    )

    select_goals, select_trainers = st.columns(2)
    match_prompt = ST_select_goals(
        match_prompt, select_goals, select_match_injuries
    )
    match_prompt = ST_select_trainers(
        match_prompt, select_trainers, select_match_injuries
    )

    select_rank_home, select_optioneel = st.columns(2)
    match_prompt = ST_select_rank(
        match_prompt, select_rank_home, select_match_injuries, team="home"
    )

    select_rank_away, select_optioneel = st.columns(2)
    match_prompt = ST_select_rank(
        match_prompt, select_rank_away, select_match_injuries, team="away"
    )

    select_formations_home, select_formations_away = st.columns(2)
    match_prompt = ST_select_formation(
        match_prompt, select_formations_home, select_match_injuries, df_player_stats, team="home"
    )
    match_prompt = ST_select_formation(
        match_prompt, select_formations_away, select_match_injuries, df_player_stats, team="away"
    )

    input_data = st.text_area(
        label="Wedstrijd Data", value=match_prompt, height=400, max_chars=None
    )
    submit = st.button("Genereer")

    generate_winstreak_plots(
            match_streak_home, home_team, match_streak_away, away_team
        )

    if submit:
        with st.spinner("Even een samenvatting aan het schrijven, momentje..."):
            if input_data != "..":
                generate_completion(
                    openai_model,
                    input_data,
                    TOKENS,
                    temperature_GPT,
                    match_streak_home,
                    home_team,
                    match_streak_away,
                    away_team,
                )

    st.info(
        """Model temperature:\n - Hogere waarden zoals 0.8 zal de output meer random 
            maken\n - Lagere waarden zoals 0.2 zal de output meer gericht en deterministisch maken""",
        icon="ℹ️",
    )

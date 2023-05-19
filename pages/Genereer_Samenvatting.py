import pandas as pd
import streamlit as st
from PIL import Image

from pages.utils_streamlit.AWS import read_S3_file
import pages.utils_streamlit.AWS_login as AWS_login
from pages.utils_streamlit.AWS_login import check_password as check_password_AWS
from pages.utils_streamlit.login import check_password
from pages.utils_streamlit.selections import (
    ST_select_date_match_venue,
    ST_select_dataset,
    ST_select_match_date,
    ST_select_match,
    ST_get_data_match,
    ST_select_injury_home,
    ST_select_injury_away,
    ST_select_trainers,
    ST_select_rank,
    ST_select_formation,
    ST_select_goals,
    ST_select_possession,
    ST_select_keepers,
    ST_club_logos,
    ST_cardEvents,
    ST_uniqueEvents,
)
from pages.utils_streamlit.stats import (
    ST_show_formation, 
    ST_SchotenOpDoel, 
    ST_SchotenOpDoelTeam,
    ST_AssistMakers,
    ST_GoalMakers,
)
from pages.utils_streamlit.generate import generate_completion, generate_winstreak_plots
from streamlit_chat import message as st_message


if "message_history" not in st.session_state:
    st.session_state.message_history = []


@st.cache_data(show_spinner="Een momentje...")
def load_images():
    return Image.open("assets/image/southfields_logo.png")


@st.cache_data(show_spinner="Een momentje...")
def load_dataset(selected_dataset: str) -> pd.DataFrame:  # Elke dag bijvoorbeeld als job schedulen
    try:
        df = read_S3_file(bucketName="gpt-ai-tool-wsc", fileName="prompt_OPTA_data/All/{}.csv".format(selected_dataset))
    except:
        df = pd.read_csv("./pages/data/eredivisie.csv", sep=",")
    df = df.sort_values(by="date", ascending=False)
    df['date'] = df['date'].str.replace('Z', '')
    return df

@st.cache_data(show_spinner="Een momentje...")
def load_dataset_player_stats(selected_dataset: str) -> pd.DataFrame:  # Elke dag bijvoorbeeld als job schedulen
    try:
        df = read_S3_file(bucketName="gpt-ai-tool-wsc", fileName="prompt_OPTA_data/All/{}_playerstats.csv".format(selected_dataset))
    except:
        df = pd.read_csv("./pages/data/eredivisie_playerstats.csv", sep=",")
    df = df.sort_values(by="date", ascending=False)
    df['date'] = df['date'].str.replace('Z', '')
    return df

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

    multi_css=f'''
            <style>
            .stMultiSelect div div div div div:nth-of-type(2) {{visibility: hidden;}}
            .stMultiSelect div div div div div:nth-of-type(2)::before {{visibility: visible; content:"Maak eventueel een keuze"}}
            </style>
            '''
    st.markdown(multi_css, unsafe_allow_html=True)

streamlit_page_config()
if AWS_login.AWS:
    AWS_check = check_password_AWS()
    streamlit_check = False
else:
    streamlit_check = check_password()
    AWS_check = False

if AWS_check or streamlit_check:
    tab1, tab2, tab3, tab4 = st.tabs(["Voetbal", "Voetbal Stats", "Handbal", "Rugby League"])
    with tab1:
        SF_logo = load_images()
        st.sidebar.success("Genereer een samenvatting op deze demo pagina.")
        st.image(SF_logo)

        # SIDEBAR
        TOKENS = st.sidebar.number_input(
            label="Maximum length (Tokens)", min_value=20, max_value=800, value=700
        )
        temperature_GPT = st.sidebar.number_input(
            label="Model Temperature", min_value=0.0, max_value=1.0, value=0.4
        )
        openai_model = st.sidebar.selectbox(
            "Selecteer een model",
            (
                "gpt-3.5-turbo",
                # "curie:ft-southfields-2023-04-05-11-53-31",
                # "davinci:ft-southfields-2023-04-07-18-26-14",
            ),
        )
        st.sidebar.success("Geselecteerd: " + str(openai_model))

        # MAIN PAGE
        select_dataset, empty_field,club_logo_home, uitslag, club_logo_away = st.columns((9, 2.25, 2.25, 2.25, 2.25))
        selected_dataset, logo_folder = ST_select_dataset(select_dataset)

        df = load_dataset(selected_dataset)
        df_player_stats = load_dataset_player_stats(selected_dataset)
        select_date, select_match = st.columns(2)
        matches_on_date, selected_match_date = ST_select_match_date(df, select_date)
        selected_match = ST_select_match(select_match, matches_on_date)
        (
            match_prompt,
            match_streak_home,
            match_streak_away,
            home_team,
            away_team,
            df_match_selected,
            df_playerStats_selected,
        ) = ST_get_data_match(df, selected_match, df_player_stats)
            
        ST_club_logos(club_logo_home, df_match_selected, team="home", logo_fold=logo_folder)
        with uitslag: 
            st.write("<span style='font-size:40px'>{}</span>".format(str(df_match_selected.score_home.values[0])
                                                                     +" - "+str(df_match_selected.score_away.values[0])), 
                     unsafe_allow_html=True)
        ST_club_logos(club_logo_away, df_match_selected, team="away", logo_fold=logo_folder)

        select_injury_home, select_injury_away = st.columns(2)
        match_prompt = ST_select_injury_home(
            match_prompt, select_injury_home, df_match_selected
        )
        match_prompt = ST_select_injury_away(
            match_prompt, select_injury_away, df_match_selected
        )

        selectCards, select_optioneel4 = st.columns(2)

        select_intro, select_optioneel = st.columns(2)
        match_prompt = ST_select_date_match_venue(
        match_prompt, select_intro, df_match_selected
        )

        select_goals, select_trainers = st.columns(2)
        match_prompt = ST_select_goals(
            match_prompt, select_goals, df_match_selected
        )
        match_prompt = ST_select_trainers(
            match_prompt, select_trainers, df_match_selected
        )

        select_keepers, select_optioneel3 = st.columns(2)
        match_prompt = ST_select_keepers(
            match_prompt, select_keepers, df_match_selected
        )

        select_rank_home, select_possession = st.columns(2)
        match_prompt = ST_select_rank(
            match_prompt, select_rank_home, df_match_selected, team="home"

        )
        match_prompt = ST_select_possession(
            match_prompt, select_possession, df_match_selected
        )

        select_rank_away, select_optioneel2 = st.columns(2)
        match_prompt = ST_select_rank(
            match_prompt, select_rank_away, df_match_selected, team="away"
        )

        select_formations_home, select_formations_away = st.columns(2)
        match_prompt = ST_select_formation(
            match_prompt, select_formations_home, df_match_selected, df_player_stats, team="home"
        )
        match_prompt = ST_select_formation(
            match_prompt, select_formations_away, df_match_selected, df_player_stats, team="away"
        )

        match_prompt = ST_cardEvents(match_prompt, selectCards, df_match_selected)
        match_prompt = ST_uniqueEvents(match_prompt, df_match_selected)

        input_data = st.text_area(
            label="Wedstrijd Data (Prompt)", value=match_prompt, height=400, max_chars=None
        )
        submit = st.button("Genereer")


        generate_winstreak_plots(
                match_streak_home, home_team, match_streak_away, away_team
            )

        if submit:
            with st.spinner("Even een samenvatting aan het schrijven, momentje..."):
                if input_data != "..":
                    completion = generate_completion(
                        openai_model,
                        input_data,
                        TOKENS,
                        temperature_GPT,
                        match_streak_home,
                        home_team,
                        match_streak_away,
                        away_team,
                        selected_match_date,
                    )
        for message_ in reversed(st.session_state.message_history):
            st_message(
                message_,
                avatar_style="bottts-neutral",
                seed="Aneka",
                is_user=False,
            )
        st.sidebar.info(
            """Model temperature:\n - Hogere waarden zoals 0.8 zal de output meer random 
                maken\n - Lagere waarden zoals 0.2 zal de output meer gericht en deterministisch maken""",
            icon="ℹ️",
        )

    with tab2:
        opt1, club_logo_home, opt2, club_logo_away, opt3 = st.columns((1.5,1,3,1,1.5))
        ST_club_logos(club_logo_home, df_match_selected, team="home", logo_fold=logo_folder)
        ST_club_logos(club_logo_away, df_match_selected, team="away", logo_fold=logo_folder)

        st.markdown("<h2 style='text-align: center; color: white;'>Speler Statistieken</h2>", unsafe_allow_html=True)
        select_schoten_home, select_schoten_away = st.columns(2)
        ST_SchotenOpDoel(select_schoten_home, df_playerStats_selected, team="Home")
        ST_SchotenOpDoel(select_schoten_away, df_playerStats_selected, team="Away")

        goals_Home, goals_away = st.columns(2)
        ST_GoalMakers(goals_Home, df_playerStats_selected, team_name=home_team)
        ST_GoalMakers(goals_away, df_playerStats_selected, team_name=away_team)

        assists_Home, assists_away = st.columns(2)
        ST_AssistMakers(assists_Home, df_playerStats_selected, team_name=home_team)
        ST_AssistMakers(assists_away, df_playerStats_selected, team_name=away_team)

        st.markdown("<h2 style='text-align: center; color: white;'>Team Statistieken</h2>", unsafe_allow_html=True)

        select_schoten_homeTeam, select_schoten_awayTeam = st.columns(2)
        ST_SchotenOpDoelTeam(select_schoten_homeTeam, df_playerStats_selected, team="Home", team_name = home_team)
        ST_SchotenOpDoelTeam(select_schoten_awayTeam, df_playerStats_selected, team="Away", team_name = away_team)

        st.markdown("<h2 style='text-align: center; color: white;'>Opstelling</h2>", unsafe_allow_html=True)
        select_formations_home, select_formations_away = st.columns(2)
        match_prompt = ST_show_formation(
            match_prompt, select_formations_home, df_match_selected, df_player_stats, team="home"
        )
        match_prompt = ST_show_formation(
            match_prompt, select_formations_away, df_match_selected, df_player_stats, team="away"
        )

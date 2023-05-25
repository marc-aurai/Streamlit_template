import ast

import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_chat import message as st_message

import pages.utils_streamlit.AWS_login as AWS_login
from pages.utils_streamlit.AWS import read_S3_file
from pages.utils_streamlit.AWS_login import \
    check_password as check_password_AWS
from pages.utils_streamlit.generate import (generate_completion,
                                            generate_winstreak_plots)
from pages.utils_streamlit.login import check_password
from pages.utils_streamlit.selections import (ST_cardEvents, ST_clubLogos,
                                              ST_getDataFromMatch,
                                              ST_goalEvents_MD,
                                              ST_selectDataset, ST_selectGoals,
                                              ST_selectInjuries,
                                              ST_selectIntro, ST_selectKeepers,
                                              ST_selectMatch,
                                              ST_selectMatchDate,
                                              ST_selectPossession,
                                              ST_selectRank, ST_selectTrainers,
                                              ST_uniqueEvents)
from pages.utils_streamlit.stats import (ST_AssistMakers, ST_GoalMakers,
                                         ST_goalRankingList, ST_minsPlayed,
                                         ST_ongeslagenStreak, ST_penaltyKiller,
                                         ST_penaltyRankingList,
                                         ST_SchotenOpDoel,
                                         ST_SchotenOpDoelTeam,
                                         ST_showFormation)
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
    tab_voetbal, tab_voetbalStats, tab_voetbalVideos, tab_handbal, tab_rugby = st.tabs(["Voetbal", "Voetbal Stats", "Voetbal Videos", "Handbal", "Rugby League"])
    with tab_voetbal:
        with st.spinner("Momentje Alstublieft.."):
            SF_logo = load_images()
            st.sidebar.success("Genereer een samenvatting op deze demo pagina.")
            #st.image(SF_logo)

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
            opt, club_logo_home, uitslag, club_logo_away, opt = st.columns((1.5,1,3,1,1.5))
            opt, goalsHomeField, opt, goalsAwayField = st.columns((1,4,2,4))
            st.markdown("""---""")

            select_dataset, opt = st.columns(2)
            selected_dataset, logo_folder = ST_selectDataset(select_dataset)

            df = load_dataset(selected_dataset)
            df_player_stats = load_dataset_player_stats(selected_dataset)
            select_date, select_match = st.columns(2)
            matches_on_date, selected_match_date = ST_selectMatchDate(df, select_date)
            selected_match = ST_selectMatch(select_match, matches_on_date)
            (
                match_prompt,
                match_streak_home,
                match_streak_away,
                home_team,
                away_team,
                df_match_selected,
                df_playerStats_selected,
            ) = ST_getDataFromMatch(df, selected_match, df_player_stats)
                
            ST_clubLogos(club_logo_home, df_match_selected, team="home", logo_fold=logo_folder)
            with uitslag: 
                st.markdown("<p style='text-align: center; color: white; font-size: 45px;'>{}</p>".format(str(df_match_selected.score_home.values[0])
                                                                        + " - "+str(df_match_selected.score_away.values[0])),
                                                                        unsafe_allow_html=True)
            for goal in ast.literal_eval(df_match_selected._goalEventsOrginal.values[0]):
                if goal["contestantId"] == df_match_selected.homeContestantId.values[0]:   
                    ST_goalEvents_MD(goalsField=goalsHomeField, goalEvent=goal)
                if goal["contestantId"] == df_match_selected.awayContestantId.values[0]:   
                    ST_goalEvents_MD(goalsField=goalsAwayField, goalEvent=goal)

            ST_clubLogos(club_logo_away, df_match_selected, team="away", logo_fold=logo_folder)

            select_injury_home, select_injury_away = st.columns(2)
            match_prompt = ST_selectInjuries(
                match_prompt, select_injury_home, df_match_selected, team="home",
            )
            match_prompt = ST_selectInjuries(
                match_prompt, select_injury_away, df_match_selected, team="away",
            )

            selectCards, opt = st.columns(2)

            select_intro, select_trainers = st.columns(2)
            match_prompt = ST_selectIntro(
            match_prompt, select_intro, df_match_selected
            )
            match_prompt = ST_selectTrainers(
                match_prompt, select_trainers, df_match_selected
            )

            select_goals, select_possession = st.columns(2)
            match_prompt = ST_selectGoals(
                match_prompt, select_goals, df_match_selected
            )
            match_prompt = ST_selectPossession(
                match_prompt, select_possession, df_match_selected
            )
            
            select_keepers, opt = st.columns(2)
            match_prompt = ST_selectKeepers(
                match_prompt, select_keepers, df_match_selected
            )

            select_rank_home, select_rank_away = st.columns(2)
            match_prompt = ST_selectRank(
                match_prompt, select_rank_home, df_match_selected, team="home"

            )
            match_prompt = ST_selectRank(
                match_prompt, select_rank_away, df_match_selected, team="away"
            )

            # select_formations_home, select_formations_away = st.columns(2)
            # match_prompt = ST_selectFormation(
            #     match_prompt, select_formations_home, df_match_selected, df_player_stats, team="home"
            # )
            # match_prompt = ST_selectFormation(
            #     match_prompt, select_formations_away, df_match_selected, df_player_stats, team="away"
            # )
            formation_home = ast.literal_eval(
                df_match_selected["formation_home"].values[0]
            )
            df_formationHome = pd.DataFrame(formation_home)
            formation_away = ast.literal_eval(
                df_match_selected["formation_away"].values[0]
            )
            df_formationAway = pd.DataFrame(formation_away)

            match_prompt = ST_cardEvents(match_prompt, selectCards, df_match_selected)
            match_prompt = ST_uniqueEvents(match_prompt, df_match_selected)

            input_data = st.text_area(
                label="Wedstrijd Data (Prompt)", value=match_prompt, height=400, max_chars=None
            )
            submit = st.button("Genereer")


            generate_winstreak_plots(
                    match_streak_home, home_team, match_streak_away, away_team
                )
            st.markdown("""---""")

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

        with tab_voetbalStats:
            opt1, club_logo_home, opt2, club_logo_away, opt3 = st.columns((1.5,1,3,1,1.5))
            ST_clubLogos(club_logo_home, df_match_selected, team="home", logo_fold=logo_folder)
            ST_clubLogos(club_logo_away, df_match_selected, team="away", logo_fold=logo_folder)

            streak_home, streak_away = st.columns((2))
            ST_ongeslagenStreak(streak_home, df_match_selected, team="home")
            ST_ongeslagenStreak(streak_away, df_match_selected, team="away")


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

            gespeeldeMinuten_home, gespeeldeMinuten_away = st.columns(2)
            ST_minsPlayed(gespeeldeMinuten_home, df_playerStats_selected, team="home")
            ST_minsPlayed(gespeeldeMinuten_away, df_playerStats_selected, team="away")

            select_penaltyHome, select_penaltyAway = st.columns(2)
            ST_penaltyKiller(select_penaltyHome, df_playerStats_selected, team="Home")
            ST_penaltyKiller(select_penaltyAway, df_playerStats_selected, team="Away")

            st.markdown("<h2 style='text-align: center; color: white;'>Team Statistieken</h2>", unsafe_allow_html=True)
            select_schoten_homeTeam, select_schoten_awayTeam = st.columns(2)
            ST_SchotenOpDoelTeam(select_schoten_homeTeam, df_playerStats_selected, team="Home", team_name = home_team)
            ST_SchotenOpDoelTeam(select_schoten_awayTeam, df_playerStats_selected, team="Away", team_name = away_team)

            st.markdown("<h2 style='text-align: center; color: white;'>Competitie Statistieken</h2>", unsafe_allow_html=True)
            select_penaltyRanking, select_goalRanking = st.columns((1.5,2))
            ST_penaltyRankingList(df_player_stats, select_penaltyRanking)
            ST_goalRankingList(df_player_stats, select_goalRanking)

            st.markdown("<h2 style='text-align: center; color: white;'>Opstelling</h2>", unsafe_allow_html=True)
            select_formations_home, select_formations_away = st.columns(2)
            ST_showFormation(
                select_formations_home, df_match_selected, df_player_stats, team="home", df=df_formationHome
            )
            ST_showFormation(
                select_formations_away, df_match_selected, df_player_stats, team="away", df=df_formationAway
            )

        with tab_voetbalVideos:
            try:
                ST_readVideo(df_videoMetadata, df_match_selected.date.values[0])
            except:
                print("AWS Access was denied.")
            
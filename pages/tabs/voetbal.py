import ast

import pandas as pd
import streamlit as st
from streamlit_chat import message as st_message

from pages.utils_streamlit.AWS import read_S3_file
from pages.utils_streamlit.generate import (generate_completion,
                                            generate_winstreak_plots)
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


@st.cache_data(show_spinner="Een momentje...")
def load_dataset(
    selected_dataset: str,
) -> pd.DataFrame:  # Elke dag bijvoorbeeld als job schedulen
    try:
        df = read_S3_file(
            bucketName="gpt-ai-tool-wsc",
            fileName="prompt_OPTA_data/All/{}.csv".format(selected_dataset),
        )
    except:
        df = pd.read_csv("./pages/data/eredivisie.csv", sep=",")
    df = df.sort_values(by="date", ascending=False)
    df["date"] = df["date"].str.replace("Z", "")
    return df


@st.cache_data(show_spinner="Een momentje...")
def load_dataset_player_stats(
    selected_dataset: str,
) -> pd.DataFrame:  # Elke dag bijvoorbeeld als job schedulen
    try:
        df = read_S3_file(
            bucketName="gpt-ai-tool-wsc",
            fileName="prompt_OPTA_data/All/{}_playerstats.csv".format(selected_dataset),
        )
    except:
        df = pd.read_csv("./pages/data/eredivisie_playerstats.csv", sep=",")
    df = df.sort_values(by="date", ascending=False)
    df["date"] = df["date"].str.replace("Z", "")
    return df


def TAB_voetbal():
    with st.spinner("Momentje Alstublieft.."):
        # SIDEBAR
        st.sidebar.success("Genereer een samenvatting op deze demo pagina.")
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
        opt, club_logo_home, uitslag, club_logo_away, opt = st.columns(
            (1.5, 1, 3, 1, 1.5)
        )
        opt, goalsHomeField, opt, goalsAwayField = st.columns((1, 4, 2, 4))
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

        ST_clubLogos(
            club_logo_home, df_match_selected, team="home", logo_fold=logo_folder
        )
        with uitslag:
            st.markdown(
                "<p style='text-align: center; color: white; font-size: 45px;'>{}</p>".format(
                    str(df_match_selected.score_home.values[0])
                    + " - "
                    + str(df_match_selected.score_away.values[0])
                ),
                unsafe_allow_html=True,
            )
        for goal in ast.literal_eval(df_match_selected._goalEventsOrginal.values[0]):
            if goal["contestantId"] == df_match_selected.homeContestantId.values[0]:
                ST_goalEvents_MD(goalsField=goalsHomeField, goalEvent=goal)
            if goal["contestantId"] == df_match_selected.awayContestantId.values[0]:
                ST_goalEvents_MD(goalsField=goalsAwayField, goalEvent=goal)

        ST_clubLogos(
            club_logo_away, df_match_selected, team="away", logo_fold=logo_folder
        )

        select_injury_home, select_injury_away = st.columns(2)
        match_prompt = ST_selectInjuries(
            match_prompt,
            select_injury_home,
            df_match_selected,
            team="home",
        )
        match_prompt = ST_selectInjuries(
            match_prompt,
            select_injury_away,
            df_match_selected,
            team="away",
        )

        selectCards, opt = st.columns(2)

        select_intro, select_trainers = st.columns(2)
        match_prompt = ST_selectIntro(match_prompt, select_intro, df_match_selected)
        match_prompt = ST_selectTrainers(
            match_prompt, select_trainers, df_match_selected
        )

        select_goals, select_possession = st.columns(2)
        match_prompt = ST_selectGoals(match_prompt, select_goals, df_match_selected)
        match_prompt = ST_selectPossession(
            match_prompt, select_possession, df_match_selected
        )

        select_keepers, opt = st.columns(2)
        match_prompt = ST_selectKeepers(match_prompt, select_keepers, df_match_selected)

        select_rank_home, select_rank_away = st.columns(2)
        match_prompt = ST_selectRank(
            match_prompt, select_rank_home, df_match_selected, team="home"
        )
        match_prompt = ST_selectRank(
            match_prompt, select_rank_away, df_match_selected, team="away"
        )

        formation_home = ast.literal_eval(df_match_selected["formation_home"].values[0])
        df_formationHome = pd.DataFrame(formation_home)
        formation_away = ast.literal_eval(df_match_selected["formation_away"].values[0])
        df_formationAway = pd.DataFrame(formation_away)

        match_prompt = ST_cardEvents(match_prompt, selectCards, df_match_selected)
        match_prompt = ST_uniqueEvents(match_prompt, df_match_selected)

        input_data = st.text_area(
            label="Wedstrijd Data (Prompt)",
            value=match_prompt,
            height=400,
            max_chars=None,
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
    return (
        df_match_selected,
        df_playerStats_selected,
        df_player_stats,
        df_formationHome,
        df_formationAway,
        logo_folder,
        home_team,
        away_team,
    )

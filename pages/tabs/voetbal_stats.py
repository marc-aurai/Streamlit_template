import pandas as pd
import streamlit as st

from pages.utils_streamlit.selections import ST_clubLogos
from pages.utils_streamlit.stats import (ST_AssistMakers, ST_GoalMakers,
                                         ST_goalRankingList, ST_minsPlayed,
                                         ST_ongeslagenStreak, ST_penaltyKiller,
                                         ST_penaltyRankingList,
                                         ST_SchotenOpDoel,
                                         ST_SchotenOpDoelTeam,
                                         ST_showFormation)


def TAB_voetbal_stats(
    df_match_selected: pd.DataFrame,
    df_playerStats_selected: pd.DataFrame,
    df_player_stats: pd.DataFrame,
    df_formationHome: pd.DataFrame,
    df_formationAway: pd.DataFrame,
    logo_folder,
    home_team: str,
    away_team: str,
):
    opt1, club_logo_home, opt2, club_logo_away, opt3 = st.columns((1.5, 1, 3, 1, 1.5))
    ST_clubLogos(club_logo_home, df_match_selected, team="home", logo_fold=logo_folder)
    ST_clubLogos(club_logo_away, df_match_selected, team="away", logo_fold=logo_folder)

    streak_home, streak_away = st.columns((2))
    ST_ongeslagenStreak(streak_home, df_match_selected, team="home")
    ST_ongeslagenStreak(streak_away, df_match_selected, team="away")

    st.markdown(
        "<h2 style='text-align: center; color: white;'>Speler Statistieken</h2>",
        unsafe_allow_html=True,
    )
    select_penaltyHome, select_penaltyAway = st.columns(2)
    ST_penaltyKiller(select_penaltyHome, df_playerStats_selected, team="Home")
    ST_penaltyKiller(select_penaltyAway, df_playerStats_selected, team="Away")

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

    st.markdown(
        "<h2 style='text-align: center; color: white;'>Team Statistieken</h2>",
        unsafe_allow_html=True,
    )
    select_schoten_homeTeam, select_schoten_awayTeam = st.columns(2)
    ST_SchotenOpDoelTeam(
        select_schoten_homeTeam,
        df_playerStats_selected,
        team="Home",
        team_name=home_team,
    )
    ST_SchotenOpDoelTeam(
        select_schoten_awayTeam,
        df_playerStats_selected,
        team="Away",
        team_name=away_team,
    )

    st.markdown(
        "<h2 style='text-align: center; color: white;'>Competitie Statistieken</h2>",
        unsafe_allow_html=True,
    )
    select_penaltyRanking, select_goalRanking = st.columns((1.6, 2))
    ST_penaltyRankingList(df_player_stats, select_penaltyRanking)
    ST_goalRankingList(df_player_stats, select_goalRanking)
    # Assist ranking list competitie

    st.markdown(
        "<h2 style='text-align: center; color: white;'>Opstelling</h2>",
        unsafe_allow_html=True,
    )
    select_formations_home, select_formations_away = st.columns(2)
    ST_showFormation(
        select_formations_home,
        df_match_selected,
        df_player_stats,
        team="home",
        df=df_formationHome,
    )
    ST_showFormation(
        select_formations_away,
        df_match_selected,
        df_player_stats,
        team="away",
        df=df_formationAway,
    )

import streamlit as st
import pandas as pd
import ast


def ST_select_match_date(df: pd.DataFrame, select_date):
    with select_date:
        selected_match_date = st.selectbox(
            "Selecteer wedstrijd datum: ", df.date.unique().tolist()
        )
    matches_on_date = df.loc[df["date"] == selected_match_date]
    return matches_on_date


def ST_select_match(select_match, matches_on_date):
    with select_match:
        selected_match = st.selectbox(
            "Selecteer wedstrijd: ", matches_on_date.match.values.tolist()
        )
    return selected_match


def ST_get_data_match(df: pd.DataFrame, selected_match):
    match_prompt = str(df["prompt"].loc[df["match"] == selected_match].to_list()[0])
    match_streak_home = (
        df["last_six_home"].loc[df["match"] == selected_match].to_list()[0]
    )
    match_streak_away = (
        df["last_six_away"].loc[df["match"] == selected_match].to_list()[0]
    )
    home_team = df["home_team"].loc[df["match"] == selected_match].to_list()[0]
    away_team = df["away_team"].loc[df["match"] == selected_match].to_list()[0]
    select_match_injuries = df.loc[df["match"] == selected_match]
    return (
        match_prompt,
        match_streak_home,
        match_streak_away,
        home_team,
        away_team,
        select_match_injuries,
    )


def ST_select_injury_home(match_prompt, select_injury_home, select_match_injuries):
    with select_injury_home:
        injuries_home = ast.literal_eval(select_match_injuries.home_injuries.values[0])
        injuries_home = [injury for injury in injuries_home if injury != "None"]
        selected_home_injuries = st.multiselect(
            "Selecteer {} blessures: ".format(select_match_injuries["home_team"].values[0]),
            options=injuries_home,
        )
        if selected_home_injuries:
            match_prompt = match_prompt.replace(
                "competitie.", "competitie.\n" + str("\n".join(selected_home_injuries))
            )
    return match_prompt


def ST_select_injury_away(match_prompt, select_injury_away, select_match_injuries):
    with select_injury_away:
        injuries_away = ast.literal_eval(select_match_injuries.away_injuries.values[0])
        injuries_away = [injury for injury in injuries_away if injury != "None"]

        selected_away_injuries = st.multiselect(
            "Selecteer {} blessures: ".format(
                select_match_injuries["away_team"].values[0]
            ),
            options=injuries_away,
        )
        if selected_away_injuries:
            match_prompt = match_prompt.replace(
                "competitie.", "competitie.\n" + str("\n".join(selected_away_injuries))
            )
    return match_prompt


def ST_select_trainers(match_prompt, select_trainers, select_match_injuries):
    with select_trainers:
        selected_trainers = st.checkbox(value=False, 
                                        label="Selecteer trainers van:\n{} & {} ".format(
                                            select_match_injuries["home_team"].values[0],
                                            select_match_injuries["away_team"].values[0]
                                        )
        )
        if selected_trainers:
            options=select_match_injuries.trainers.values,
            match_prompt = match_prompt.replace(
                ".\n\n###\n\n", "\n" + str(" ".join(options)) + ".\n\n###\n\n"
            )
        else: 
            pass
    return match_prompt
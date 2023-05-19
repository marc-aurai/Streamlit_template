import ast
import datetime as dt
import locale

import pandas as pd
import streamlit as st
from PIL import Image
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from pages.utils_streamlit.AWS import read_S3_club_logos

locale.setlocale(category=locale.LC_ALL, locale="nl_NL")

def ST_selectDataset(select_dateset) -> pd.DataFrame:
    """Access a group of matches (or single match) on a particular match date.

    Args:
        df (pd.DataFrame): eredivisie.csv, which originate from (soccer_pipeline.py).
        Includes all the necessary data from all played matches in Eredvisie 22/23.
        select_date (st.column): A Streamlit container in the Streamlit UI.

    Returns:
        matches_on_date (pd.DataFrame): Returns a smaller dataframe,
        which only returns the rows that occured on the date the user selected.
    """
    with select_dateset:
        selected_dataset = st.selectbox(
            "Voetbal competitie: ",
            ["Eredivisie 22-23", "Eredivisie 21-22", "KKD 22-23"],
        )
    if selected_dataset == "KKD 22-23":
        logo_folder = "KKD_logos"
    else:
        logo_folder = "eredivisie_logos"
    return selected_dataset, logo_folder


def ST_selectMatchDate(df: pd.DataFrame, select_date) -> pd.DataFrame:
    """Access a group of matches (or single match) on a particular match date.

    Args:
        df (pd.DataFrame): eredivisie.csv, which originate from (soccer_pipeline.py).
        Includes all the necessary data from all played matches in Eredvisie 22/23.
        select_date (st.column): A Streamlit container in the Streamlit UI.

    Returns:
        matches_on_date (pd.DataFrame): Returns a smaller dataframe,
        which only returns the rows that occured on the date the user selected.
    """
    sorted_dates = sorted(df.date.unique().tolist(), key=lambda x: dt.datetime.strptime(x, '%a %d %b %Y'), reverse=True)
    with select_date:
        selected_match_date = st.selectbox(
            "Wedstrijd datum: ", sorted_dates
        )
    matches_on_date = df.loc[df["date"] == selected_match_date]
    return matches_on_date, selected_match_date


def ST_selectMatch(select_match, matches_on_date: pd.DataFrame) -> str:
    """Access a specific match after you selected a specific match date.

    Args:
        select_match (st.column): A Streamlit container in the Streamlit UI.
        matches_on_date (pd.DataFrame): A small dataframe which resulted from the function (ST_select_match_date).
        It contains only the rows that occured on the date the user selected.

    Returns:
        selected_match (str): Returns a single match as a string,
        which only returns the selected match by the user that occured on the date the user selected.
    """
    with select_match:
        selected_match = st.selectbox(
            "Wedstrijd: ", matches_on_date.match.values.tolist()
        )
    return selected_match


def ST_getDataFromMatch(
    df: pd.DataFrame, selected_match: str, df_playerStats: pd.DataFrame
) -> tuple[str, str, str, str, str, pd.DataFrame]:
    """Get all the available data from a specific date and matchthat originates from OPTA and
    processed by the soccer_pipeline.py script.

    Args:
        df (pd.DataFrame): A small dataframe which resulted from the function (ST_select_match).
        It contains only one row that occured on the date the user selected and the specific match the user selected.
        selected_match (st.column): A Streamlit container in the Streamlit UI.

    Returns:
        tuple[str, str, str, str, str, pd.DataFrame]: 1.Prompt 2.The winstreak of the home team
        3.The winstreak of the away team 4.The name of the home team 5.The name of the away team
        6.Returns a dataframe with a single row; which only returns the selected match by the user that occured on the date the user selected.
    """
    match_prompt = str(df["prompt"].loc[df["match"] == selected_match].to_list()[0])
    match_streak_home = (
        df["last_six_home"].loc[df["match"] == selected_match].to_list()[0]
    )
    match_streak_away = (
        df["last_six_away"].loc[df["match"] == selected_match].to_list()[0]
    )
    home_team = df["home_team"].loc[df["match"] == selected_match].to_list()[0]
    away_team = df["away_team"].loc[df["match"] == selected_match].to_list()[0]
    df_match_selected = df.loc[df["match"] == selected_match]
    df_playerStats_selected = df_playerStats.loc[df_playerStats["match"] == selected_match]
    return (
        match_prompt,
        match_streak_home,
        match_streak_away,
        home_team,
        away_team,
        df_match_selected,
        df_playerStats_selected
    )


def ST_selectInjuries(
    match_prompt: str, select_field, df_match_selected: pd.DataFrame, team: str
) -> str:
    """This function adds players from the home team, that currently have injuries, to the prompt in the Streamlit Application.
    It can be the case that the team has no injuries.

    Args:
        match_prompt (str): The prompt that originates from the pipeline (soccer_pipeline.py).
        select_injury_home (st.column): A Streamlit container in the Streamlit UI.
        df_match_selected (pd.DataFrame): A dataframe with a single row;
        which only returns the selected match by the user that occured on the date the user selected.

    Returns:
        str: The prompt that originates from the pipeline (soccer_pipeline.py) + potential
        injuries that have been added by the user input (multiselect component in Streamlit).
    """
    with select_field:
        injuries = ast.literal_eval(df_match_selected["{}_injuries".format(team)].values[0])
        injuries = [injury for injury in injuries if injury != "None"]
        selected_injuries = st.multiselect(
            "{} blessures: ".format(df_match_selected["{}_team".format(team)].values[0]),
            options=injuries,
        )
        if selected_injuries:
            match_prompt = (
                match_prompt + str(".\n".join(selected_injuries)) + ".\n"
            )
    return match_prompt


def ST_selectTrainers(
    match_prompt: str, select_trainers, df_match_selected: pd.DataFrame
) -> str:
    """This function adds both the trainers from the home- and away team, to the prompt in the Streamlit Application.
    Args:
        match_prompt (str): The prompt that originates from the pipeline (soccer_pipeline.py).
        select_trainers (st.column): A Streamlit container in the Streamlit UI.
        df_match_selected (pd.DataFrame): A dataframe with a single row;
        which only returns the selected match by the user that occured on the date the user selected.
    Returns:
        str: The prompt that originates from the pipeline (soccer_pipeline.py) + potential
        injuries, trainers or other datapoints that have been added by the user input (multiselect component in Streamlit).
    """
    with select_trainers:
        selected_trainers = st.checkbox(
            value=False,
            label="Trainers van:\n{} & {} ".format(
                df_match_selected["home_team"].values[0],
                df_match_selected["away_team"].values[0],
            ),
        )
        if selected_trainers:
            options = list(df_match_selected.trainers.values[0])
            match_prompt = match_prompt + str("".join(options)) + ".\n"
        else:
            pass
    return match_prompt


def ST_selectPossession(
    match_prompt: str, select_possession, df_match_selected: pd.DataFrame
) -> str:
    with select_possession:
        selected_possession = st.checkbox(
            value=True,
            label="Balbezit",
        )
        if selected_possession:
            options = list(df_match_selected._possession.values[0])
            match_prompt = match_prompt + str("".join(options)) + ".\n"
        else:
            pass
    return match_prompt


def ST_selectRank(
    match_prompt: str, select_rank, df_match_selected: pd.DataFrame, team: str
) -> str:
    with select_rank:
        selected_rank = st.checkbox(
            value=True,
            label="Rank van:\n{}".format(
                df_match_selected[str(team) + "_team"].values[0],
            ),
        )
        if selected_rank:
            lastRank = str(df_match_selected["lastRank_" + str(team)].values[0])
            newRank = str(df_match_selected["rank_" + str(team)].values[0])
            if lastRank != newRank:
                match_prompt = (
                    match_prompt
                    + str(df_match_selected[str(team) + "_team"].values[0])
                    + " stond op plek {} en staat nu op de {}".format(lastRank, newRank)
                    + "e plaats.\n"
                )
            else:
                match_prompt = (
                    match_prompt
                    + str(df_match_selected[str(team) + "_team"].values[0])
                    + " staat na deze wedstrijd nog steeds op de {}".format(newRank)
                    + "e plaats.\n"
                )
        else:
            pass
    return match_prompt


def ST_selectFormation(
    match_prompt: str,
    select_field,
    df_match_selected: pd.DataFrame,
    player_stats: pd.DataFrame,
    team: str,
) -> str:
    with select_field:
        selected_formations = st.checkbox(
            value=False,
            label="Opstelling van:\n{}".format(
                df_match_selected[str(team) + "_team"].values[0],
            ),
        )
        if selected_formations:
            formation_away = ast.literal_eval(
                df_match_selected["formation_" + str(team)].values[0]
            )
            df = pd.DataFrame(formation_away)
            df.rename(
                columns={"playerName": "Naam",
                        "position": "Positie",
                        "positionSide": "Positie kant"},
                inplace=True,
            )
            gd = GridOptionsBuilder.from_dataframe(
                df[["Naam", "Positie", "Positie kant"]]
            )
            gd.configure_pagination(enabled=False)
            gd.configure_selection(selection_mode="single", use_checkbox=True)
            gridOptions = gd.build()

            custom_css = {
                ".ag-column-hover": {"background-color": "#Cbcbcb", "color": "#FFFFFF"},
                ".ag-row-hover": {"background-color": "#Cbcbcb", "color": "#FFFFFF"},
                ".ag-header-hover": {"background-color": "#Cbcbcb", "color": "#FFFFFF"},
                ".ag-header-cell": {"background-color": "#100c44", "color": "#FFFFFF"},
                ".ag-row-odd": {"background-color": "#100c44", "color": "#FFFFFF"},
                ".ag-row-even": {"background-color": "#100c44", "color": "#FFFFFF"},
                ".ag-subheader": {"border-color": "#100c44"},
            }

            grid_table = AgGrid(
                df[["Naam", "Positie", "Positie kant"]],
                gridOptions=gridOptions,
                enable_enterprise_modules=False,
                fit_columns_on_grid_load=True,
                custom_css=custom_css,
                update_mode=GridUpdateMode.MODEL_CHANGED,
                allow_unsafe_jscode=True,
            )
            # Show substitutions
            substitutions = df_match_selected["substitutions_" + str(team)].values[0]
            nameOff, symbol, nameOn, timeMin = st.columns((4, 1, 4, 1))
            for substitution in ast.literal_eval(substitutions):
                with nameOff:
                    st.write(
                        "<span style='font-size:12px'>{}</span>".format(
                            substitution["playerOffName"]
                        )
                        + "<span style='color:red;font-size:12px'>{}</span>".format(
                            "⬇"
                        ),
                        unsafe_allow_html=True,
                    )
                with symbol:
                    st.write(
                        "<span style='color:white;font-size:12px'>{}</span>".format(
                            "⇆"
                        ),
                        unsafe_allow_html=True,
                    )
                with nameOn:
                    st.write(
                        "<span style='font-size:12px'>{}</span>".format(
                            substitution["playerOnName"]
                        )
                        + "<span style='color:green;font-size:12px'>{}</span>".format(
                            "⬆"
                        ),
                        unsafe_allow_html=True,
                    )
                with timeMin:
                    st.write(
                        "<span style='color:white;font-size:12px'>{}{}</span>".format(
                            str(substitution["timeMin"]), "'"
                        ),
                        unsafe_allow_html=True,
                    )

            player_stats = player_stats.loc[
                player_stats["date"] == df_match_selected.date.values[0]
            ]
            player_stats = [
                ast.literal_eval(
                    player_stats["player_stats_" + str(team)].values[match]
                )
                for match in range(
                    len(player_stats["player_stats_" + str(team)].values)
                )
            ]  # Get all player stats from all matches on the selected date
            player_stats = [
                item for sublist in player_stats for item in sublist
            ]  # flatten player stats list

            try:
                df_selected = pd.DataFrame(grid_table["selected_rows"])
                selected_player = (
                    df["playerId"]
                    .loc[df["Naam"] == str(df_selected["Naam"].values[0])]
                    .values[0]
                )
                player_stat = next(
                    player
                    for player in player_stats
                    if player["playerId"] == selected_player
                )
                player_stat = pd.DataFrame(
                    player_stat, index=[1]
                )  # .sort_index(axis=1)
                player_stat.rename(
                columns={"playerName": "Naam",
                        "saves":"Reddingen",
                        "goalAssist": "Assists",
                        "accuratePass": "Passes Aangekomen",
                        "totalPass": "Totaal Passes",
                        "score_pogingen": "Score Pogingen",
                        "minsPlayed": "Minuten Gespeeld",
                        "Pass_accuracy": "Pass Accuraatheid"},
                inplace=True,
                )
                player_stat = player_stat.set_index("Naam")
            except:
                pass
        else:
            pass
    try:
        st.write(player_stat.loc[:, player_stat.columns != "playerId"])
    except:
        pass
    return match_prompt


def ST_selectGoals(
    match_prompt: str, select_goals, df_match_selected: pd.DataFrame
) -> str:
    with select_goals:
        selected_goals = st.checkbox(
            value=True,
            label="Goals",
        )
        if selected_goals:
            options = list(df_match_selected._goalEvents.values[0])
            match_prompt = match_prompt + str("".join(options)) + ".\n"
        else:
            pass
    return match_prompt


def ST_selectIntro(
    match_prompt: str, select_intro, df_match_selected: pd.DataFrame
) -> str:
    # Intro = date + match + venue
    with select_intro:
        selected_intro = st.checkbox(
            value=True,
            label="Intro",
        )
        if selected_intro:
            options = list(df_match_selected._date_match_venue.values[0])
            match_prompt = match_prompt + str("".join(options)) + ".\n"
        else:
            pass
    return match_prompt


def ST_selectKeepers(
    match_prompt: str, select_keepers, df_match_selected: pd.DataFrame
) -> str:
    with select_keepers:
        selected_keepers = st.checkbox(
            value=True,
            label="Keepers",
        )
        if selected_keepers:
            options = list(df_match_selected.keepers.values[0])
            match_prompt = match_prompt + str("".join(options)) + ".\n"
        else:
            pass
    return match_prompt


def ST_clubLogos(select_container, df_match_selected: pd.DataFrame, team: str, logo_fold: str = "eredivisie_logos"):
    """ Show a team logo inside a streamlit container 

    Args:
        select_container (_type_): _description_
        df_match_selected (pd.DataFrame): _description_
        team (str): _description_
    """
    with select_container:
        try:
            st.image(
                read_S3_club_logos(
                    bucketName="gpt-ai-tool-wsc",
                    fileName="logos/{}/{}.png".format(
                        logo_fold,
                        df_match_selected[str(team) + "_team"].values[0]
                    ),
                )
            )
        except:
            try:
                st.image(
                    Image.open(
                        "assets/logos/{}/{}.png".format(
                            logo_fold,
                            df_match_selected[str(team) + "_team"].values[0]
                        )
                    )
                )
            except:
                pass


def ST_cardEvents(match_prompt: str, select_container, df_match_selected: pd.DataFrame):
    with select_container:
        overtredingen = str(df_match_selected._cardEvents.values[0]).split(", ")
        selectedCards = st.multiselect(
            "Overtredingen:",
            options=overtredingen,
        )
        if selectedCards:
            match_prompt = match_prompt + str(".\n".join(selectedCards)) + ".\n"
    return match_prompt


def ST_uniqueEvents(
    match_prompt: str,
    df_match_selected: pd.DataFrame,
):
    """ Show cumulatief aantal kaarten per speler, indien het intressant is. 
    Zoals schorsingen bijvoorbeeld.
    Args:
        match_prompt (str): 
        df_match_selected (pd.DataFrame): De geselecteerde match (dataframe row), 
        na het selecteren van: competitite -> datum -> wedstrijd

    Returns:
        _type_: _description_
    """
    for key, value in ast.literal_eval(
        df_match_selected.cardsHistoryYellow.values[0]
    ).items():
        if value in [5, 10]:
            st.write(
                "<span style='font-size:14px'>{}. </span>".format(str(key))
                + "<span style='color:yellow;font-size:16px'>Cumulatief: {}</span>".format(
                    str(value)
                ),
                unsafe_allow_html=True,
            )
        elif value > 10:
            st.write(
                "<span style='font-size:14px'>{}. </span>".format(str(key))
                + "<span style='color:yellow;font-size:16px'>Cumulatief: {}</span>".format(
                    str(value)
                ),
                unsafe_allow_html=True,
            )

    for key, value in ast.literal_eval(
        df_match_selected.cardsHistoryRed.values[0]
    ).items():
        checkBox_schorsing = st.checkbox(label="Schorsingen", value=False)
        st.write(
            "<span style='font-size:14px'>{}. </span>".format(str(key))
            + "<span style='color:red;font-size:16px'>Cumulatief: {}</span>".format(
                str(value)
            ),
            unsafe_allow_html=True,
        )
        if checkBox_schorsing:
            match_prompt = (
                match_prompt
                + str(key).replace("🟥 ", "")
                + " is geschorst voor de volgende wedstrijd vanwege een rode kaart."
            )
    try:
        if checkBox_schorsing:
            match_prompt = match_prompt + "\n"
    except:  # Then no checkBox was available: No red cards.
        pass
    return match_prompt

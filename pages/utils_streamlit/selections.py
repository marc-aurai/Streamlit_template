import streamlit as st
import pandas as pd
import ast
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from PIL import Image
from pages.utils_streamlit.AWS import read_S3_club_logos
from io import BytesIO


def ST_select_dataset(select_dateset) -> pd.DataFrame:
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
    return selected_dataset


def ST_select_match_date(df: pd.DataFrame, select_date) -> pd.DataFrame:
    """Access a group of matches (or single match) on a particular match date.

    Args:
        df (pd.DataFrame): eredivisie.csv, which originate from (soccer_pipeline.py).
        Includes all the necessary data from all played matches in Eredvisie 22/23.
        select_date (st.column): A Streamlit container in the Streamlit UI.

    Returns:
        matches_on_date (pd.DataFrame): Returns a smaller dataframe,
        which only returns the rows that occured on the date the user selected.
    """
    with select_date:
        selected_match_date = st.selectbox(
            "Wedstrijd datum: ", df.date.unique().tolist()
        )
    matches_on_date = df.loc[df["date"] == selected_match_date]
    return matches_on_date, selected_match_date


def ST_select_match(select_match, matches_on_date: pd.DataFrame) -> str:
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


def ST_get_data_match(
    df: pd.DataFrame, selected_match: str
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
    return (
        match_prompt,
        match_streak_home,
        match_streak_away,
        home_team,
        away_team,
        df_match_selected,
    )


def ST_select_injury_home(
    match_prompt: str, select_injury_home, df_match_selected: pd.DataFrame
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
    with select_injury_home:
        injuries_home = ast.literal_eval(df_match_selected.home_injuries.values[0])
        injuries_home = [injury for injury in injuries_home if injury != "None"]
        selected_home_injuries = st.multiselect(
            "{} blessures: ".format(df_match_selected["home_team"].values[0]),
            options=injuries_home,
        )
        if selected_home_injuries:
            match_prompt = (
                match_prompt + str(".\n".join(selected_home_injuries)) + ".\n"
            )
    return match_prompt


def ST_select_injury_away(
    match_prompt: str, select_injury_away, df_match_selected: pd.DataFrame
) -> str:
    """This function adds players from the away team, that currently have injuries, to the prompt in the Streamlit Application.
    It can be the case that the team has no injuries.

    Args:
        match_prompt (str): The prompt that originates from the pipeline (soccer_pipeline.py).
        select_injury_away (st.column): A Streamlit container in the Streamlit UI.
        df_match_selected (pd.DataFrame): A dataframe with a single row;
        which only returns the selected match by the user that occured on the date the user selected.

    Returns:
        str: The prompt that originates from the pipeline (soccer_pipeline.py) + potential
        injuries that have been added by the user input (multiselect component in Streamlit).
    """
    with select_injury_away:
        injuries_away = ast.literal_eval(df_match_selected.away_injuries.values[0])
        injuries_away = [injury for injury in injuries_away if injury != "None"]

        selected_away_injuries = st.multiselect(
            "{} blessures: ".format(df_match_selected["away_team"].values[0]),
            options=injuries_away,
        )
        if selected_away_injuries:
            match_prompt = (
                match_prompt + str(".\n".join(selected_away_injuries)) + ".\n"
            )
    return match_prompt



def ST_select_trainers(
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


def ST_select_possession(
    match_prompt: str, select_possession, df_match_selected: pd.DataFrame
) -> str:
    with select_possession:
        selected_possession = st.checkbox(
            value=True,
            label="Balbezit",
        )
        if selected_possession:
            options = list(df_match_selected._possession.values[0])
            match_prompt = (
                match_prompt
                + str("".join(options)) + ".\n"
            )
        else:
            pass
    return match_prompt


def ST_select_rank(
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


def ST_select_formation(
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
            gd = GridOptionsBuilder.from_dataframe(
                df[["playerName", "position", "positionSide"]]
            )
            gd.configure_pagination(enabled=False)
            gd.configure_selection(selection_mode="single", use_checkbox=True)
            gridOptions = gd.build()

            custom_css = {
                ".ag-column-hover": {"background-color":"#Cbcbcb","color":"#FFFFFF"},
                ".ag-row-hover": {"background-color":"#Cbcbcb","color":"#FFFFFF"},
                ".ag-header-hover": {"background-color":"#Cbcbcb","color":"#FFFFFF"},
                ".ag-header-cell": {"background-color":"#100c44", "color":"#FFFFFF"},
                ".ag-row-odd": {"background-color":"#100c44", "color":"#FFFFFF"},
                ".ag-row-even": {"background-color":"#100c44", "color":"#FFFFFF"},
                ".ag-subheader": {"border-color":"#100c44"},
                }
            
            grid_table = AgGrid(
                df[["playerName", "position", "positionSide"]],
                gridOptions=gridOptions,
                enable_enterprise_modules=False,
                fit_columns_on_grid_load=True,
                custom_css=custom_css,
                update_mode=GridUpdateMode.MODEL_CHANGED,
                allow_unsafe_jscode=True,
            )
            # Show substitutions
            substitutions = df_match_selected["substitutions_"+str(team)].values[0]
            nameOff, symbol, nameOn, timeMin = st.columns((4,1,4,1))
            for substitution in ast.literal_eval(substitutions):
                with nameOff:
                    st.write("<span style='font-size:10px'>{}</span>".format(substitution["playerOffName"])
                             +"<span style='color:red;font-size:10px'>{}</span>".format("⬇"),
                             unsafe_allow_html=True)
                with symbol:
                    st.write("<span style='color:white;font-size:10px'>{}</span>".format("⇆"), unsafe_allow_html=True)
                with nameOn:
                    st.write("<span style='font-size:10px'>{}</span>".format(substitution["playerOnName"])
                             +"<span style='color:green;font-size:10px'>{}</span>".format("⬆"), 
                             unsafe_allow_html=True)
                with timeMin:
                    st.write("<span style='color:white;font-size:10px'>{}{}</span>".format(str(substitution["timeMin"]),"'"), unsafe_allow_html=True)
            
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
                    .loc[df["playerName"] == str(df_selected["playerName"].values[0])]
                    .values[0]
                )
                player_stat = next(
                    player
                    for player in player_stats
                    if player["playerId"] == selected_player
                )
                player_stat = pd.DataFrame(
                    player_stat, index=[0]
                )  # .sort_index(axis=1)
            except:
                pass
        else:
            pass
    try:
        st.write(player_stat.loc[:, player_stat.columns != "playerId"])
    except:
        pass
    return match_prompt


def ST_select_goals(
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


def ST_select_date_match_venue(
    match_prompt: str, select_intro, df_match_selected: pd.DataFrame
) -> str:
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


def ST_select_keepers(
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


def ST_club_logos(
    select_container, df_match_selected: pd.DataFrame, team: str
):
    with select_container:
        try:
            st.image(
                read_S3_club_logos(
                    bucketName="gpt-ai-tool-wsc",
                    fileName="eredivisie_logos/{}.png".format(df_match_selected[str(team)+"_team"].values[0]),
                    )
            )
        except:
            try:
                st.image(Image.open("assets/eredivisie_logos/{}.png".format(df_match_selected[str(team)+"_team"].values[0])))
            except:
                pass
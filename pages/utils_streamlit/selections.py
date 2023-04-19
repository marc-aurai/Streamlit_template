import streamlit as st
import pandas as pd
import ast
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder


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
    return matches_on_date


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
    select_match_injuries = df.loc[df["match"] == selected_match]
    return (
        match_prompt,
        match_streak_home,
        match_streak_away,
        home_team,
        away_team,
        select_match_injuries,
    )


def ST_select_injury_home(
    match_prompt: str, select_injury_home, select_match_injuries: pd.DataFrame
) -> str:
    """This function adds players from the home team, that currently have injuries, to the prompt in the Streamlit Application.
    It can be the case that the team has no injuries.

    Args:
        match_prompt (str): The prompt that originates from the pipeline (soccer_pipeline.py).
        select_injury_home (st.column): A Streamlit container in the Streamlit UI.
        select_match_injuries (pd.DataFrame): A dataframe with a single row;
        which only returns the selected match by the user that occured on the date the user selected.

    Returns:
        str: The prompt that originates from the pipeline (soccer_pipeline.py) + potential
        injuries that have been added by the user input (multiselect component in Streamlit).
    """
    with select_injury_home:
        injuries_home = ast.literal_eval(select_match_injuries.home_injuries.values[0])
        injuries_home = [injury for injury in injuries_home if injury != "None"]
        selected_home_injuries = st.multiselect(
            "{} blessures: ".format(
                select_match_injuries["home_team"].values[0]
            ),
            options=injuries_home,
        )
        if selected_home_injuries:
            match_prompt = match_prompt.replace(
                "competitie.", "competitie.\n" + str("\n".join(selected_home_injuries))
            )
    return match_prompt


def ST_select_injury_away(
    match_prompt: str, select_injury_away, select_match_injuries: pd.DataFrame
) -> str:
    """This function adds players from the away team, that currently have injuries, to the prompt in the Streamlit Application.
    It can be the case that the team has no injuries.

    Args:
        match_prompt (str): The prompt that originates from the pipeline (soccer_pipeline.py).
        select_injury_away (st.column): A Streamlit container in the Streamlit UI.
        select_match_injuries (pd.DataFrame): A dataframe with a single row;
        which only returns the selected match by the user that occured on the date the user selected.

    Returns:
        str: The prompt that originates from the pipeline (soccer_pipeline.py) + potential
        injuries that have been added by the user input (multiselect component in Streamlit).
    """
    with select_injury_away:
        injuries_away = ast.literal_eval(select_match_injuries.away_injuries.values[0])
        injuries_away = [injury for injury in injuries_away if injury != "None"]

        selected_away_injuries = st.multiselect(
            "{} blessures: ".format(
                select_match_injuries["away_team"].values[0]
            ),
            options=injuries_away,
        )
        if selected_away_injuries:
            match_prompt = match_prompt.replace(
                "competitie.", "competitie.\n" + str("\n".join(selected_away_injuries))
            )
    return match_prompt


def ST_select_trainers(
    match_prompt: str, select_trainers, select_match_injuries: pd.DataFrame
) -> str:
    """This function adds both the trainers from the home- and away team, to the prompt in the Streamlit Application.

    Args:
        match_prompt (str): The prompt that originates from the pipeline (soccer_pipeline.py).
        select_trainers (st.column): A Streamlit container in the Streamlit UI.
        select_match_injuries (pd.DataFrame): A dataframe with a single row;
        which only returns the selected match by the user that occured on the date the user selected.


    Returns:
        str: The prompt that originates from the pipeline (soccer_pipeline.py) + potential
        injuries, trainers or other datapoints that have been added by the user input (multiselect component in Streamlit).
    """
    with select_trainers:
        selected_trainers = st.checkbox(
            value=False,
            label="Trainers van:\n{} & {} ".format(
                select_match_injuries["home_team"].values[0],
                select_match_injuries["away_team"].values[0],
            ),
        )
        if selected_trainers:
            options = list(select_match_injuries.trainers.values[0])
            match_prompt = match_prompt.replace(
                "\n\n###\n\n", "\n" + str("".join(options)) + ".\n\n###\n\n"
            )
        else:
            pass
    return match_prompt


def ST_select_rank_home(
    match_prompt: str, select_rank_home, select_match_injuries: pd.DataFrame
) -> str:
    """This function adds both the trainers from the home- and away team, to the prompt in the Streamlit Application.

    Args:
        match_prompt (str): The prompt that originates from the pipeline (soccer_pipeline.py).
        select_trainers (st.column): A Streamlit container in the Streamlit UI.
        select_match_injuries (pd.DataFrame): A dataframe with a single row;
        which only returns the selected match by the user that occured on the date the user selected.


    Returns:
        str: The prompt that originates from the pipeline (soccer_pipeline.py) + potential
        injuries, trainers or other datapoints that have been added by the user input (multiselect component in Streamlit).
    """
    with select_rank_home:
        selected_trainers = st.checkbox(
            value=False,
            label="Rank van:\n{}".format(
                select_match_injuries["home_team"].values[0],
            ),
        )
        if selected_trainers:
            options = str(select_match_injuries.rank_home.values[0])
            match_prompt = match_prompt.replace(
                "\n\n###\n\n", "\n"+ str(select_match_injuries["home_team"].values[0]) + " staat nu op de " + str("".join(options)) + "e plaats.\n\n###\n\n"
            )
        else:
            pass
    return match_prompt


def ST_select_rank_away(
    match_prompt: str, select_rank_away, select_match_injuries: pd.DataFrame
) -> str:
    """This function adds both the trainers from the home- and away team, to the prompt in the Streamlit Application.

    Args:
        match_prompt (str): The prompt that originates from the pipeline (soccer_pipeline.py).
        select_trainers (st.column): A Streamlit container in the Streamlit UI.
        select_match_injuries (pd.DataFrame): A dataframe with a single row;
        which only returns the selected match by the user that occured on the date the user selected.


    Returns:
        str: The prompt that originates from the pipeline (soccer_pipeline.py) + potential
        injuries, trainers or other datapoints that have been added by the user input (multiselect component in Streamlit).
    """
    with select_rank_away:
        selected_trainers = st.checkbox(
            value=False,
            label="Rank van:\n{}".format(
                select_match_injuries["away_team"].values[0],
            ),
        )
        if selected_trainers:
            options = str(select_match_injuries.rank_away.values[0])
            match_prompt = match_prompt.replace(
                "\n\n###\n\n", "\n"+ str(select_match_injuries["away_team"].values[0]) + " staat nu op de " + str("".join(options)) + "e plaats.\n\n###\n\n"
            )
        else:
            pass
    return match_prompt


def ST_select_formation_home(
    match_prompt: str, select_formations_home, select_match_injuries: pd.DataFrame
) -> str:
    with select_formations_home:
        selected_formations = st.checkbox(
            value=False,
            label="Opstelling van:\n{}".format(
                select_match_injuries["home_team"].values[0],
            ),
        )
        if selected_formations:
            formation_home = ast.literal_eval(select_match_injuries.formation_home.values[0])
            df = pd.DataFrame(formation_home)
            gd = GridOptionsBuilder.from_dataframe(df[["playerName", "position"]])
            gd.configure_pagination(enabled=True)
            gd.configure_selection(selection_mode='single', use_checkbox=True)
            gridOptions = gd.build()

            grid_table = AgGrid(df[["playerName", "position"]],
                   gridOptions=gridOptions,
                   enable_enterprise_modules=True,
                   fit_columns_on_grid_load=True,
                   theme="balham",
                   update_mode=GridUpdateMode.MODEL_CHANGED,
                   allow_unsafe_jscode=True,
            )
            try:
                #dict_keys(['data', 'selected_rows', 'column_state', 'excel_blob'])
                df_selected = pd.DataFrame(grid_table["selected_rows"])
                selected_player = df.loc[df["playerName"] == str(df_selected["playerName"].values[0])]
            except:
                pass
        else:
            pass
    try:
        st.write(selected_player[["playerName","position","accuratePass","totalPass"]])
    except:pass
    return match_prompt


def ST_select_formation_away(
    match_prompt: str, select_formations_away, select_match_injuries: pd.DataFrame
) -> str:
    with select_formations_away:
        selected_formations = st.checkbox(
            value=False,
            label="Opstelling van:\n{}".format(
                select_match_injuries["away_team"].values[0],
            ),
        )
        if selected_formations:
            formation_away = ast.literal_eval(select_match_injuries.formation_away.values[0])
            df = pd.DataFrame(formation_away)
            gd = GridOptionsBuilder.from_dataframe(df[["playerName", "position"]])
            gd.configure_pagination(enabled=True)
            gd.configure_selection(selection_mode='single', use_checkbox=True)
            gridOptions = gd.build()

            grid_table = AgGrid(df[["playerName", "position"]],
                   gridOptions=gridOptions,
                   enable_enterprise_modules=True,
                   fit_columns_on_grid_load=True,
                   theme="balham",
                   update_mode=GridUpdateMode.MODEL_CHANGED,
                   allow_unsafe_jscode=True,
            )
            #dict_keys(['data', 'selected_rows', 'column_state', 'excel_blob'])
            try:
                df_selected = pd.DataFrame(grid_table["selected_rows"])
                selected_player = df.loc[df["playerName"] == str(df_selected["playerName"].values[0])]
            except:
                pass
        else:
            pass
    try:
        st.write(selected_player[["playerName","position","accuratePass","totalPass"]])
    except:
        pass
    return match_prompt

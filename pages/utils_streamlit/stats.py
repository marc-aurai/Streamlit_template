import pandas as pd
import streamlit as st
import ast
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder

def ST_show_formation(
    match_prompt: str,
    select_field,
    df_match_selected: pd.DataFrame,
    player_stats: pd.DataFrame,
    team: str,
) -> str:
    with select_field:
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
    try:
        st.write(player_stat.loc[:, player_stat.columns != "playerId"])
    except:
        pass
    return match_prompt


def ST_SchotenOpDoelTeam(
    select_field,
    df: pd.DataFrame,
    team: str,
    team_name: str,
):
    with select_field:
        try:
            df = pd.DataFrame({"Team": team_name,"Schoten op doel Totaal": df["SchotenOpDoel_" + str(team)]})
            df = df.set_index("Schoten op doel Totaal")
            st.dataframe(df, use_container_width=True)
        except:
            pass
        
        
def ST_SchotenOpDoel(
    select_field,
    df: pd.DataFrame,
    team: str
):
    with select_field:
        try:
            df = pd.DataFrame(ast.literal_eval(df["MatchStats" + str(team)].values[0]))
            df = df[["SchotenOpDoel", "playerName"]]
            df['SchotenOpDoel'] = df['SchotenOpDoel'].astype('int')
            df.rename(
                columns={"SchotenOpDoel": "Schoten op doel",
                        "playerName":"Spelernaam",
                        },
                inplace=True,
                )
            df['Spelernaam'].where(df['Schoten op doel'] <4, df['Spelernaam'].astype(str) + "🔥", inplace=True)
            df = df.set_index("Schoten op doel")
            st.dataframe(df, use_container_width=True)
        except:
            pass


def ST_AssistMakers(
    field,
    df: pd.DataFrame,
    team_name: str,
):
    with field:
        try:
            df = pd.DataFrame({
                "Assists dit Seizoen": ast.literal_eval(df["AssistCounter"].values[0]).values(),   
                "Spelernaam": ast.literal_eval(df["AssistCounter"].values[0]).keys(),
            })
            df = df.loc[df['Spelernaam'].str.contains(team_name, case=False)]  
            df['Spelernaam'] = df['Spelernaam'].str.replace(team_name, '', regex=True)
            df['Spelernaam'] = df['Spelernaam'].str.replace("|", '', regex=True)       
            df = df.set_index("Assists dit Seizoen")
            st.dataframe(df.sort_values(by="Assists dit Seizoen", ascending=False), use_container_width=True)
        except:
            pass


def ST_GoalMakers(
    field,
    df: pd.DataFrame,
    team_name: str,
):
    with field:
        try:
            df = pd.DataFrame({
                "Goals dit Seizoen": ast.literal_eval(df["GoalCounter"].values[0]).values(),
                "Spelernaam": ast.literal_eval(df["GoalCounter"].values[0]).keys(),
                })
            df = df.loc[df['Spelernaam'].str.contains(team_name, case=False)]
            df['Spelernaam'] = df['Spelernaam'].str.replace(team_name, '', regex=True)
            df['Spelernaam'] = df['Spelernaam'].str.replace("|", '', regex=True)
            df.sort_values(by="Goals dit Seizoen", ascending=False)
            df['Spelernaam'].where(df['Goals dit Seizoen'] <10, df['Spelernaam'].astype(str) + "🔥", inplace=True)
            df = df.set_index("Goals dit Seizoen")
            st.dataframe(df, use_container_width=True)
        except:
            pass
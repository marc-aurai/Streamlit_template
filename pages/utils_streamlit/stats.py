import ast
from collections import Counter

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder


def ST_showFormation(
    select_field,
    df_match_selected: pd.DataFrame,
    player_stats: pd.DataFrame,
    team: str,
    df: pd.DataFrame,
) -> str:
    with select_field:
        selected_formations = st.checkbox(
            value=False,
            label="Opstelling van:\n{}".format(
                df_match_selected[str(team) + "_team"].values[0],
            ),
        )
        if selected_formations:
            
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
                reload_data=True,
            )
            # Show substitutions
            substitutions = df_match_selected["substitutions_" + str(team)].values[0]
            nameOff, symbol, nameOn, timeMin = st.columns((4, 1, 4, 1))
            if substitutions:
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

            df_selected = pd.DataFrame(grid_table["selected_rows"])
            if not df_selected.empty:
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
                
    try:
        st.write(player_stat.loc[:, player_stat.columns != "playerId"])
    except:
        pass


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

            df = df.iloc[-1:]
            st.dataframe(df.style.set_properties(**{'color': 'rgb(255, 255, 255)'}), use_container_width=True)
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
            #df = df.set_index("Spelernaam")
            df.index = df.index + 1
            st.dataframe(df.style.set_properties(**{'color': 'rgb(255, 255, 255)'}), use_container_width=True)
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
            #df = df.set_index("Spelernaam")
            df = df.sort_values(by="Assists dit Seizoen", ascending=False).reset_index(inplace=True, drop=True)
            df.index = df.index + 1
            st.dataframe(df.style.set_properties(**{'color': 'rgb(255, 255, 255)'}), use_container_width=True)
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
            df = df.reset_index(drop=True)
            df.index = df.index + 1
            st.dataframe(df.style.set_properties(**{'color': 'rgb(255, 255, 255)'}), use_container_width=True)
        except:
            pass


def ST_ongeslagenStreak(    
    field,
    df: pd.DataFrame,
    team: str,
):
    with field:
        streak = ""
        last_six = str(df["last_six_{}".format(team)].values[0])
        last_six = [
            match_status
        for match_status in list(last_six)
        ]
        for i in range(3, 6):
            if all(element == last_six[0] for element in last_six[:i]):
                if last_six[0] == "W":
                    streak = "Laatste {} gewonnen 🔥".format(i)
                if last_six[0] == "L":
                    streak = "Laatste {} verloren 👎".format(i)
        if streak != "":
            st.markdown("<h2 style='text-align: center; color: white; font-size: 18px;'>{}</h2>".format(streak), unsafe_allow_html=True)


def ST_minsPlayed(
    field,
    df: pd.DataFrame,
    team: str,
):
    with field:
        minsPlayed = ast.literal_eval(df["minsPlayedCounter"].values[0])
        formation_names = [player_stat["playerName"] for player_stat in ast.literal_eval(df["player_stats_{}".format(team)].values[0])] + [player_stat["playerOnName"] for player_stat in ast.literal_eval(df["substitutions_{}".format(team)].values[0])]
        speelminutenTeam = df["sum_matchLength_{}".format(team)].values[0]
        df = pd.DataFrame({
                "Speelminuten": minsPlayed.values(),
                "Spelernaam": minsPlayed.keys(),
                }).sort_values(by="Speelminuten", ascending=False)
        df = df[df['Spelernaam'].isin(formation_names)]
        speelMinutenPercentage = [str(round(((speelMinuten*100) / speelminutenTeam), 2))+"%" for speelMinuten in df["Speelminuten"].values]
        df["Speelminuten Seizoen"] = speelMinutenPercentage
        # df = df.set_index("Speelminuten")
        df.reset_index(drop=True, inplace=True)
        df.index = df.index + 1
        st.dataframe(df.style.set_properties(**{'color': 'rgb(255, 255, 255)'}), use_container_width=True)

    
def ST_penaltyKiller(
    field,
    df: pd.DataFrame,
    team: str,
):
    try:
        penaltyEventsKeeper = ast.literal_eval(df["penalty{}".format(team)].values[0])
        if penaltyEventsKeeper:
            with field:
                for penalty in penaltyEventsKeeper:
                    if "penaltySave" in penalty:
                        st.info(
                        "{} (Keeper) kreeg een penalty tegen deze wedstrijd en hield hem tegen.🔥".format(
                            penalty["playerName"]
                        ),
                        # unsafe_allow_html=True,
                        )
                    else:
                        st.info(
                        "{} (Keeper) kreeg een penalty tegen deze wedstrijd en hield hem niet tegen.".format(
                            penalty["playerName"]
                        ),
                        # unsafe_allow_html=True,
                    )
                    
    except:
        pass


def ST_penaltyRankingList(
        df: pd.DataFrame,
        penaltyField,
):
    try:
        penaltyEvents = df.penaltyHome.values.tolist() + df.penaltyAway.values.tolist()
        penaltyEvents = [i for i in penaltyEvents if i != "[]"]
        penaltyEventsRefactored = []
        for penaltyEvent in penaltyEvents:
            penaltyEventsRefactored.append(ast.literal_eval(penaltyEvent)[0])

        penaltyRankingList = []
        for penaltyEvent in penaltyEventsRefactored:
            if "penaltySave" in penaltyEvent:
                penaltyRankingList.append(penaltyEvent)

        penaltyRanking = dict(Counter(x['playerName'] for x in penaltyRankingList))
        df_penaltyRanking = pd.DataFrame(penaltyRanking.items(), columns=["Naam", "Penalty's gestopt"])# .set_index("Naam")
        with penaltyField:
            st.write(
                        "<h5 style='text-align: center; color:white;font-size:15px'>Top Penalty Killers</h5>",
                        unsafe_allow_html=True,
                    )
            df_penaltyRanking = df_penaltyRanking.sort_values(by="Penalty's gestopt", ascending=False)
            df_penaltyRanking = df_penaltyRanking.reset_index(drop=True)
            df_penaltyRanking.index = df_penaltyRanking.index + 1
            st.dataframe(df_penaltyRanking.style.set_properties(**{'color': 'rgb(255, 255, 255)'}), use_container_width=True)
    except:
        pass

def remove_duplicate_top_scorers(lst):
    unique_first_elements = set()
    result = []

    for tuple_item in lst:
        first_element = tuple_item[0]
        if first_element not in unique_first_elements:
            unique_first_elements.add(first_element)
            result.append(tuple_item)

    return result


def ST_goalRankingList(
        df: pd.DataFrame,
        goalCounterField,
):
    try:
        goalEvents = df.GoalCounter.values.tolist()
        goalEventsRanking = []
        for goalEvent in goalEvents:
            goalEventsRanking.append(ast.literal_eval(goalEvent))
        goalEventsRanking = [i for i in goalEventsRanking if i != {}]

        goalCounter = []
        for goal in goalEventsRanking:
            for playerName, goalAmount in goal.items():
                goalCounter.append((playerName, goalAmount))

        top10_Scorers = sorted(goalCounter, key = lambda x: x[1], reverse = True)[:50]
        top10_Scorers = remove_duplicate_top_scorers(top10_Scorers)
        with goalCounterField:
            st.write(
                        "<h5 style='text-align: center;color:white;font-size:15px'>Top Scorers</h5>",
                        unsafe_allow_html=True,
                    )
            df_top10 = pd.DataFrame(top10_Scorers, columns=["Naam", "Doelpunten"])
            df_top10[['Club', 'Naam']] = df_top10['Naam'].str.split('|', expand=True)
            df_top10 = df_top10[["Naam", "Club", "Doelpunten"]]
            df_top10.index = df_top10.index + 1
            st.dataframe(df_top10.style.set_properties(**{'color': 'rgb(255, 255, 255)'}))
    except:
        pass

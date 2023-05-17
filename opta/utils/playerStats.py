import pandas as pd
import requests
from collections import Counter
from tqdm import tqdm


def convertCardId(outletAuthKey, competition, cardsHistoryYellow, cardsHistoryRed):
    try:
        matchstats = requests.get(
                    f"http://api.performfeeds.com/soccerdata/squads/{{}}/?_rt=b&_fmt=json&tmcl={{}}".format(
                        outletAuthKey, competition
                    )
                ).json()["squad"]
        
        cardsHistoryYellow_Names= []
        for cardsHistoryMatch in cardsHistoryYellow:
            yellowCardsCounter = {}
            for key, value in cardsHistoryMatch.items():
                for team in matchstats:
                    for person in team["person"]:
                        if key == person["id"]:
                            yellowCardsCounter["🟨 " + str(person["matchName"])] = value
            cardsHistoryYellow_Names.append(yellowCardsCounter)

        cardsHistoryRed_Names= []
        for cardsHistoryMatch in cardsHistoryRed:
            redCardsCounter = {}
            for key, value in cardsHistoryMatch.items():
                for team in matchstats:
                    for person in team["person"]:
                        if key == person["id"]:
                            redCardsCounter["🟥 " + str(person["matchName"])] = value
            cardsHistoryRed_Names.append(redCardsCounter)
    except:
        pass
    return cardsHistoryYellow_Names, cardsHistoryRed_Names


def get_totalCardsPlayer(
    df: pd.DataFrame,
    outletAuthKey: str,
    competition: str,
) -> pd.DataFrame:
    playerCardsYellow = []
    cardsHistoryYellow = []
    playerCardsRed = []
    cardsHistoryRed = []
    for home, subHome, away, subAway in zip(df.formation_home.values, df.substitutions_home.values, df.formation_away.values, df.substitutions_away.values):
        cardsMatchYellow = []
        cardsMatchRed = []
        try:
            for playerHome in home:
                if any([card in playerHome["playerName"] for card in ["🟨"]]):
                    playerCardsYellow.append(playerHome["playerId"])
                    cardsMatchYellow.append(playerHome["playerId"])
                # Rood of twee keer geel in wedstrijd
                if any([card in playerHome["playerName"] for card in ["🟨|🟨", "🟥"]]):
                    playerCardsRed.append(playerHome["playerId"])
                    cardsMatchRed.append(playerHome["playerId"])
            for playerAway in away:    
                if any([card in playerAway["playerName"] for card in ["🟨"]]):
                    playerCardsYellow.append(playerAway["playerId"])
                    cardsMatchYellow.append(playerAway["playerId"])
                if any([card in playerAway["playerName"] for card in ["🟨|🟨", "🟥"]]):
                    playerCardsRed.append(playerAway["playerId"])
                    cardsMatchRed.append(playerAway["playerId"])

            for playerSubHome in subHome:
                if any([card in playerSubHome["playerOnName"] for card in ["🟨"]]):
                    playerCardsYellow.append(playerSubHome["playerOnId"])
                    cardsMatchYellow.append(playerSubHome["playerOnId"])
                if any([card in playerSubHome["playerOnName"] for card in ["🟨|🟨", "🟥"]]):
                    playerCardsRed.append(playerSubHome["playerOnId"])
                    cardsMatchRed.append(playerSubHome["playerOnId"])

            for playerSubAway in subAway:
                if any([card in playerSubAway["playerOnName"] for card in ["🟨"]]):
                    playerCardsYellow.append(playerSubAway["playerOnId"])
                    cardsMatchYellow.append(playerSubAway["playerOnId"])
                if any([card in playerSubAway["playerOnName"] for card in ["🟨|🟨", "🟥"]]):
                    playerCardsRed.append(playerSubAway["playerOnId"])
                    cardsMatchRed.append(playerSubAway["playerOnId"])

            countRed = [x for x in playerCardsRed if x in cardsMatchRed]
            countYellow = [x for x in playerCardsYellow if x in cardsMatchYellow]
            cardsHistoryRed.append(dict(Counter(countRed)))
            cardsHistoryYellow.append(dict(Counter(countYellow)))
        except:
            cardsHistoryRed.append({})
            cardsHistoryYellow.append({})
    cardsHistoryYellow, cardsHistoryRed = convertCardId(outletAuthKey, competition, cardsHistoryYellow, cardsHistoryRed)
    
    df["cardsHistoryRed"] = cardsHistoryRed
    df["cardsHistoryYellow"] = cardsHistoryYellow
    return df



def get_matchStats(
    df: pd.DataFrame = None,
    outletAuthKey: str = None,
) -> pd.DataFrame:
    # Create container for new column
    player_stats_home = []
    player_stats_away = []
    print("\nGet match statistics..")
    SchotenOpDoelTotaal_Home = []
    SchotenOpDoelTotaal_Away = []
    # Loop through df to get match id's
    for match in tqdm(df.index):
        try:
            matchstats_formations = requests.get(
                f"http://api.performfeeds.com/soccerdata/matchstats/{{}}/?_rt=b&_fmt=json&fx={{}}".format(
                    outletAuthKey, df["id"][match]
                )
            ).json()["liveData"]["lineUp"]

            player_stat_home = []
            player_stat_away = []
            for team in range(2):
                for player_formation in matchstats_formations[team]["player"]:
                        stat_player = {}
                        for stat in player_formation["stat"]:
                                if stat["type"] == "totalScoringAtt":
                                    stat_player["SchotenOpDoel"] = stat["value"]
                                    stat_player["playerName"] = player_formation["firstName"] + " " + player_formation["lastName"]
                                    stat_player["playerId"] = player_formation["playerId"]

                        if team == 0 and stat_player:
                            player_stat_home.append(stat_player)
                        if team == 1 and stat_player:
                            player_stat_away.append(stat_player)
        except:
            player_stat_home = []
            player_stat_away = []
        player_stat_home = sorted(player_stat_home, key=lambda d: d['SchotenOpDoel'], reverse=True) 
        player_stat_away = sorted(player_stat_away, key=lambda d: d['SchotenOpDoel'], reverse=True) 
        
        TotaalSchotenOpDoel_Home = 0
        TotaalSchotenOpDoel_Away = 0
        for SchotenOpDoel in player_stat_home:
            TotaalSchotenOpDoel_Home += int(SchotenOpDoel["SchotenOpDoel"])
        for SchotenOpDoel in player_stat_away:
            TotaalSchotenOpDoel_Away += int(SchotenOpDoel["SchotenOpDoel"])
        
        player_stats_home.append(player_stat_home)
        player_stats_away.append(player_stat_away)
    
        SchotenOpDoelTotaal_Home.append(TotaalSchotenOpDoel_Home)
        SchotenOpDoelTotaal_Away.append(TotaalSchotenOpDoel_Away) 
    # Add list to dataframe
    df["SchotenOpDoel_Home"] = SchotenOpDoelTotaal_Home
    df["SchotenOpDoel_Away"] = SchotenOpDoelTotaal_Away
    df["MatchStatsHome"] = player_stats_home
    df["MatchStatsAway"] = player_stats_away
    return df


def get_countPlayerGoals(
    df: pd.DataFrame = None,
    outletAuthKey: str = None,
) -> pd.DataFrame:
    
    goalCounter = []
    assistCounter = []
    allGoalmakers = []
    AllAssistMakers = []
    for goals in df.goal_events.values:
        countMatchGoals = []
        countMatchAssists = []
        for goal in goals:
            try:
                if goal["assistName"] != "":
                    AllAssistMakers.append(str(goal["contestantName"]+ " | " + goal["assistName"]))
                    countMatchAssists.append(str(goal["contestantName"]+ " | " + goal["assistName"]))
                if goal["scorerName"] != "":
                    allGoalmakers.append(str(goal["contestantName"]+ " | " + goal["scorerName"]))
                    countMatchGoals.append(str(goal["contestantName"]+ " | " + goal["scorerName"]))
            except:
                pass
        MatchGoals = [x for x in allGoalmakers if x in countMatchGoals]
        MatchAssists = [x for x in AllAssistMakers if x in countMatchAssists]
        goalCounter.append(dict(Counter(MatchGoals)))
        assistCounter.append(dict(Counter(MatchAssists)))
    df["GoalCounter"] = goalCounter
    df["AssistCounter"] = assistCounter
    return df
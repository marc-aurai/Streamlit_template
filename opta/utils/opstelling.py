import pandas as pd
import requests
from tqdm import tqdm


def get_formations(
    df: pd.DataFrame = None,
    outletAuthKey: str = None,
) -> pd.DataFrame:
    """Vergaar de opstelling van een team en bepaalde speler statistieken, met een API call naar OPTA toe.

    Args:
        df (pd.DataFrame, optional): De dataset als pandas dataframe die moet worden uitgebreid met de kolommen: 
        formation_home, formation_away, player_stats_home, player_stats_away. Defaults to None.
        outletAuthKey (str, optional): De authorisatie key die hoort bij het een bepaalde: sport/competitie/seizoen. Defaults to None.

    Returns:
        pd.DataFrame: Een geupdate pandas dataframe met 4 extra kolommen: formation_home, formation_away, player_stats_home, player_stats_away.
    """
    
    formations_home = []
    player_stats_home = []
    formations_away = []
    player_stats_away = []
    print("\nGet formations..")

    # Loop through df to get match id's
    for match in tqdm(df.index):
        try:
            matchstats_formations = requests.get(
                f"http://api.performfeeds.com/soccerdata/matchstats/{{}}/?_rt=b&_fmt=json&fx={{}}".format(
                    outletAuthKey, df["id"][match]
                )
            ).json()["liveData"]["lineUp"]
            try:
                cards = requests.get(
                    f"http://api.performfeeds.com/soccerdata/matchstats/{{}}/?_rt=b&_fmt=json&fx={{}}".format(
                        outletAuthKey, df["id"][match]
                    )
                ).json()["liveData"]["card"]
            except:
                cards = {}
            formation_home = []
            player_stat_home = []
            formation_away = []
            player_stat_away = []
            for team in range(2):
                for player_formation in matchstats_formations[team]["player"]:
                    if player_formation["position"] != "Substitute":
                        formation_player = {}
                        stat_player = {}
                        if player_formation["playerId"] in [
                            sub["playerId"] for sub in cards
                        ]:
                            card = next(
                                item
                                for item in cards
                                if item["playerId"] == player_formation["playerId"]
                            )  # Select the right card if the player exist
                            if card["type"] == "YC":
                                formation_player["playerName"] = (
                                    "🟨 " + player_formation["lastName"]
                                )
                            if card["type"] == "Y2C":
                                formation_player["playerName"] = (
                                    "🟨|🟨 " + player_formation["lastName"]
                                )
                            if card["type"] == "RC":
                                formation_player["playerName"] = (
                                    "🟥 " + player_formation["lastName"]
                                )
                        else:
                            formation_player["playerName"] = player_formation[
                                "lastName"
                            ]
                        formation_player["position"] = player_formation["position"]
                        formation_player["positionSide"] = player_formation[
                            "positionSide"
                        ]
                        formation_player["playerId"] = player_formation["playerId"]
                        stat_player["playerName"] = formation_player[
                            "playerName"
                        ]  # Copy from formation_player, which includes cards
                        stat_player["playerId"] = player_formation["playerId"]
                        for stat in player_formation["stat"]:
                            if stat["type"] in [
                                "minsPlayed",
                                "totalPass",
                                "accuratePass",
                                "goalAssist",
                                "totalScoringAtt",
                                "saves",
                            ]:                                
                                if stat["type"] == "totalScoringAtt":
                                    stat_player["score_pogingen"] = stat["value"]
                                else:
                                    stat_player[stat["type"]] = stat["value"]
       
                        try:
                            stat_player["Pass_accuracy"] = round(
                                (int(stat_player["accuratePass"]) * 100)
                                / int(stat_player["totalPass"]),
                                2,
                            )
                            if stat_player["minsPlayed"] == "90":
                                stat_player["minsPlayed"] = df["matchLength"][match]
                        except:
                            pass
                        if team == 0:
                            formation_home.append(formation_player)
                            player_stat_home.append(stat_player)
                        if team == 1:
                            formation_away.append(formation_player)
                            player_stat_away.append(stat_player)
        except:
            formation_home = []
            formation_away = []
            player_stat_home = []
            player_stat_away = []
        formations_home.append(formation_home)
        formations_away.append(formation_away)
        player_stats_home.append(player_stat_home)
        player_stats_away.append(player_stat_away)

    # Add list to dataframe
    df["formation_home"] = formations_home
    df["formation_away"] = formations_away
    df["player_stats_home"] = player_stats_home
    df["player_stats_away"] = player_stats_away
    return df


def get_substitute(
    df: pd.DataFrame = None,
    outletAuthKey: str = None,
) -> pd.DataFrame:
    """Vergaar de wissels tijdens een wedstrijd van een team, met een API call naar OPTA toe.

    Args:
        df (pd.DataFrame, optional): De dataset als pandas dataframe die moet worden uitgebreid met de kolommen: 
        substitutions_home, substitutions_away. Defaults to None.
        outletAuthKey (str, optional): De authorisatie key die hoort bij het een bepaalde: sport/competitie/seizoen. Defaults to None.

    Returns:
        pd.DataFrame: Een geupdate pandas dataframe met 2 extra kolommen: substitutions_home, substitutions_away.
    """
    
    substitutions_home = []
    substitutions_away = []
    print("\nGet substitute..")

    # Loop through df to get match id's
    for match in tqdm(df.index):
        try:
            matchstats = requests.get(
                f"http://api.performfeeds.com/soccerdata/matchstats/{{}}/?_rt=b&_fmt=json&fx={{}}".format(
                    outletAuthKey, df["id"][match]
                )
            ).json()
            cards = requests.get(
                f"http://api.performfeeds.com/soccerdata/matchstats/{{}}/?_rt=b&_fmt=json&fx={{}}".format(
                    outletAuthKey, df["id"][match]
                )
            ).json()["liveData"]["card"]
            substitute_home = []
            substitute_away = []
            for substitute in matchstats["liveData"]["substitute"]:
                substitute_player = {}

                # Speler uit, voeg kaart toe tot naam
                for substituteType in ["On", "Off"]:
                    if substitute["player{}Id".format(substituteType)] in [
                        sub["playerId"] for sub in cards
                    ]:
                        card = next(
                            item
                            for item in cards
                            if item["playerId"]
                            == substitute["player{}Id".format(substituteType)]
                        )  # Select the right card if the player exist
                        if card["type"] == "YC":
                            substitute_player["player{}Name".format(substituteType)] = (
                                "🟨 " + substitute["player{}Name".format(substituteType)]
                            )
                        if card["type"] == "Y2C":
                            substitute_player["player{}Name".format(substituteType)] = (
                                "🟨|🟨 "
                                + substitute["player{}Name".format(substituteType)]
                            )
                        if card["type"] == "RC":
                            substitute_player["player{}Name".format(substituteType)] = (
                                "🟥 " + substitute["player{}Name".format(substituteType)]
                            )
                    else:
                        substitute_player[
                            "player{}Name".format(substituteType)
                        ] = substitute["player{}Name".format(substituteType)]
                
                substitute_player["playerId"] = substitute["playerOnId"]
                substitute_player["playerOffId"] = substitute["playerOffId"]
                substitute_player["timeMin"] = substitute["timeMin"]
                substitute_player["minsPlayed"] = df["matchLength"][match] - int(substitute["timeMin"])
                substitute_player["subReason"] = substitute["subReason"]
                if (
                    substitute["contestantId"]
                    == matchstats["matchInfo"]["contestant"][0]["id"]
                ):
                    substitute_home.append(substitute_player)
                if (
                    substitute["contestantId"]
                    == matchstats["matchInfo"]["contestant"][1]["id"]
                ):
                    substitute_away.append(substitute_player)
        except:
            substitute_home = []
            substitute_away = []
        substitutions_home.append(substitute_home)
        substitutions_away.append(substitute_away)

    # Add list to dataframe
    df["substitutions_home"] = substitutions_home
    df["substitutions_away"] = substitutions_away
    return df


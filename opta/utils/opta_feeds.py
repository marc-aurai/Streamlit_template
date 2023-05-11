import pandas as pd
import requests
from tqdm import tqdm
import numpy as np
from googletrans import Translator
from collections import Counter
import ast


# ID's van Eredivisie seizoenen volgorde 23/22/21
def get_tournamentschedule(
    outletAuthKey: str,
    table_kind="tournamentschedule",
    competitions=[
        "d1k1pqdg2yvw8e8my74yvrdw4",
        "dp0vwa5cfgx2e733gg98gfhg4",
        "bp1sjjiswd4t3nw86vf6yq7hm",
    ],
) -> pd.DataFrame:
    """All scraped ESPN Articles correspondent to a particular competition.
    With the competition ID's from OPTA it is possible to get all matches from that competition, and thus all extra information from a match
    In order to merge the data from ESPN with OPTA the following data is needed;
    date, homeContestantCode and awayContestantCode. Since ESPN also includes date, home_abbrev (contestantcode) and away_abbrev (contestantcode).

    Args:
        outletAuthKey (str): Statsperform Authorization Key e.g. (Eredivsie, Keuken Kampioen Divisie/KKD)
        table_kind (str, optional): Table from Statsperform to select. Defaults to "tournamentschedule".
        competitions (list, optional): All competition ID's needed to concatenate the ESPN data with OPTA. Defaults to [ "d1k1pqdg2yvw8e8my74yvrdw4", "dp0vwa5cfgx2e733gg98gfhg4", "bp1sjjiswd4t3nw86vf6yq7hm", ]. \n
        ID's that originates from Eredivisie seasons:
        1: 23/22
        2: 22/21
        3: 21/20
    Returns:
        pd.DataFrame: Returns a dataframe with OPTA data, that originates from the Table tournamentschedule with the corresponding competitions.
        The Dataframe that is returned from this function includes the following columns from OPTA (tournamentschedule):
        ['id'] ,['date'] ,['homeContestantId'] ,['awayContestantId'],
        ['homeContestantOfficialName'], ['awayContestantOfficialName'],
        ['homeContestantCode'], ['awayContestantCode']
    """
    df_all_matches = pd.DataFrame()

    # Loop through different divisions
    for competition in competitions:
        url = f"http://api.performfeeds.com/soccerdata/{{}}/{{}}/{{}}?_rt=b&_fmt=json".format(
            table_kind, outletAuthKey, competition
        )
        response = requests.get(url).json()

        # Create dataframe for every competition
        df_matches = pd.DataFrame()
        df_matches = pd.concat(
            [
                # Concat all matches in competition in dataframe
                pd.concat(
                    [df_matches, pd.DataFrame(response["matchDate"][matches]["match"])]
                )
                # Range are all matches within the season
                for matches in range(len(response["matchDate"]))
            ],
            ignore_index=True,
        )

        # Concat all competitions together (seasons 23/22/21)
        df_all_matches = pd.concat([df_all_matches, df_matches], ignore_index=True)

    return df_all_matches[
        [
            "id",
            "date",
            "homeContestantId",
            "awayContestantId",
            "homeContestantName",
            "awayContestantName",
            "homeContestantCode",
            "awayContestantCode",
        ]
    ]
    # Return only selected columns from dataframe


def get_name(df, type: str = None, outletAuthKey: str = None, competition: str = None):
    """
    Helper function for get_matchstats_goals to get the 'correct' name for the scorer or player
    takes in the goal event from match_stats goals and the same outletAuthKey
    If no name is available, the scorername from the goal event is returned
    """
    data = requests.get(
        f"http://api.performfeeds.com/soccerdata/squads/{{}}/?_rt=b&_fmt=json&tmcl={{}}&ctst={{}}".format(
            outletAuthKey, competition, df["contestantId"]
        )
    ).json()

    try:
        name = next(
            person["firstName"] + " " + person["lastName"]
            for squad in data["squad"]
            for person in squad["person"]
            if person["id"] == df[str(type) + "Id"]
        )
        return str(name)
    except:
        return str(df["scorerName"]).split(". ", 1)[1]


def get_matchstats_cards(
    df: pd.DataFrame = None,
    outletAuthKey: str = None,
    competition: str = None,
) -> pd.DataFrame:
    """This function returns the input dataframe with one extra collumn named ['card_events'].
    The column contains a list of dictionaries that represents all the cards with their corresponding information:
    [contestantName, contestantId, periodId, timeMin, playerId, playerName, cardType].

    Args:
        df (pd.DataFrame): Minimum requirement: This function needs a dataframe as input that includes the ESPN data,
        concatenated with get_tournamentschedule().
        outletAuthKey (str): Statsperform Authorization Key e.g. (Eredivsie, Keuken Kampioen Divisie/KKD)

    Returns:
        pd.DataFrame: Returns the original input dataframe with one extra collumn included, named ['card_events'].
    """

    # Create container for new column
    all_team_cards = []
    print("\nGet Card Events..")

    # Loop through df to get match id's
    for match in tqdm(df.index):
        try:
            matchstats = (
                requests.get(
                    f"http://api.performfeeds.com/soccerdata/matchstats/{{}}/?_rt=b&_fmt=json&fx={{}}".format(
                        outletAuthKey, df["id"][match]
                    )
                )
                # Access card information from live data
                .json()["liveData"]["card"]
            )

            # For every card event, create dict with info and add to list
            team_cards = [
                {
                    "contestantName": requests.get(
                        f"http://api.performfeeds.com/soccerdata/team/{{}}/?_rt=b&_fmt=json&ctst={{}}".format(
                            outletAuthKey, card["contestantId"]
                        )
                    ).json()["contestant"][0]["name"],
                    "contestantId": card["contestantId"],
                    "periodId": card["periodId"],
                    "timeMin": card["timeMin"],
                    "playerId": card["playerId"],
                    # "playerName" : str(card["playerName"]).split(". ", 1)[1],
                    "playerName": get_name(
                        card,
                        type="player",
                        outletAuthKey=outletAuthKey,
                        competition=competition,
                    ),
                    "cardType": card["type"],
                    "cardReason": card["cardReason"],
                }
                for card in matchstats
            ]
        except:
            team_cards = []  # If there are no cards available
        all_team_cards.append(team_cards)

    # Add list to dataframe
    df["card_events"] = all_team_cards
    return df


def get_matchstats_goals(
    df: pd.DataFrame = None,
    outletAuthKey: str = None,
    competition: str = None,
) -> pd.DataFrame:
    """This function returns the input dataframe with one extra collumn named ['goal_events'].
    The column contains a list of dictionaries that represents all the goals with their corresponding information:
    [contestantName, contestantId, periodId, timeMin, scorerId, scorerName].

    Args:
        df (pd.DataFrame): Minimum requirement: This function needs a dataframe as input that includes the ESPN data,
        concatenated with get_tournamentschedule().
        outletAuthKey (str): Statsperform Authorization Key e.g. (Eredivsie, Keuken Kampioen Divisie/KKD)

    Returns:
        pd.DataFrame: Returns the original input dataframe with one extra collumn included, named ['goal_events'].
    """

    # Container for new column
    all_team_goals = []
    all_goalMakers = []
    print("\nGet Goal Events..")

    # Loop through df to get all match id's
    for match in tqdm(df.index):
        try:
            matchstats = (
                requests.get(
                    f"http://api.performfeeds.com/soccerdata/matchstats/{{}}/?_rt=b&_fmt=json&fx={{}}".format(
                        outletAuthKey, df["id"][match]
                    )
                )
                # Access goal information from live data
                .json()["liveData"]["goal"]
            )

            # For every event, create dict with info and add to list
            team_goals = [
                {
                    "contestantName": requests.get(
                        f"http://api.performfeeds.com/soccerdata/team/{{}}/?_rt=b&_fmt=json&ctst={{}}".format(
                            outletAuthKey, goal["contestantId"]
                        )
                    ).json()["contestant"][0]["name"],
                    "contestantId": goal["contestantId"],
                    "periodId": goal["periodId"],
                    "timeMin": goal["timeMin"],
                    "scorerId": goal["scorerId"],
                    # "scorerName" : str(goal["scorerName"]).split(". ", 1)[1],
                    "scorerName": get_name(
                        goal,
                        type="scorer",
                        outletAuthKey=outletAuthKey,
                        competition=competition,
                    ),
                    "goalType": goal["type"],
                }
                for goal in matchstats
            ]
            goalMakers = [
                get_name(
                    goal,
                    type="scorer",
                    outletAuthKey=outletAuthKey,
                    competition=competition,
                )
                for goal in matchstats
            ]
        except:
            team_goals = []  # If there are no goals available
            goalMakers = []
        all_team_goals.append(team_goals)
        all_goalMakers.append(goalMakers)

    # Add list to dataframe
    df["goal_events"] = all_team_goals
    df["goalMakers"] = all_goalMakers
    return df


def get_matchstats_possession(
    df: pd.DataFrame = None, outletAuthKey: str = None
) -> pd.DataFrame:
    """This function returns the input dataframe with two extra collumns named ['possession_home'] and ['possession_away'].
    The column contains a string that represents the team's possession percentage.

    Args:
        df (pd.DataFrame): Minimum requirement: This function needs a dataframe as input that includes the ESPN data, concatenated with get_tournamentschedule().
        outletAuthKey (str): Statsperform Authorization Key e.g. (Eredivsie, Keuken Kampioen Divisie/KKD)
    Returns:
        pd.DataFrame: Returns the original input dataframe with two extra collumns included, named ['possession_home'] and ['possession_away'].
    """
    all_possessions_home = []
    all_possessions_away = []
    print("\nGet Possession Percentage..")
    for match in tqdm(df.index):
        try:
            matchstats = requests.get(
                f"http://api.performfeeds.com/soccerdata/matchstats/{{}}/?_rt=b&_fmt=json&fx={{}}".format(
                    outletAuthKey, df["id"][match]
                )
            ).json()["liveData"]["lineUp"]
            possession_home = str(
                next(
                    item["value"]
                    for item in matchstats[0]["stat"]
                    if item["type"] == "possessionPercentage"
                )
                + "%"
            )
            possession_away = str(
                next(
                    item["value"]
                    for item in matchstats[1]["stat"]
                    if item["type"] == "possessionPercentage"
                )
                + "%"
            )
        except:
            possession_home = np.nan
            possession_away = np.nan
        all_possessions_home.append(possession_home)
        all_possessions_away.append(possession_away)

    df["possession_home"] = all_possessions_home
    df["possession_away"] = all_possessions_away
    return df


def get_venue(df: pd.DataFrame = None, outletAuthKey: str = None) -> pd.DataFrame:
    """This function returns the input dataframe with one extra collumn named ['venue'].
    The match's venue is listed in the column as a string.

    Args:
        df (pd.DataFrame): Minimum requirement: This function needs a dataframe as input that includes the ESPN data, concatenated with get_tournamentschedule().
        outletAuthKey (str): Statsperform Authorization Key e.g. (Eredivsie, Keuken Kampioen Divisie/KKD)
    Returns:
        pd.DataFrame: Returns the original input dataframe with one extra collumn included, named ['venue'].
    """

    # Container for new venues column
    all_venues = []
    print("\nGet venues..")

    # Loop through match id's
    for match in tqdm(df.index):
        try:
            # Enter match id in API call
            response = requests.get(
                f"http://api.performfeeds.com/soccerdata/matchstats/{{}}/?_rt=b&_fmt=json&fx={{}}".format(
                    outletAuthKey, df["id"][match]
                )
            ).json()

            # Access venue information in json if available
            venue = response["matchInfo"]["venue"]["longName"]
        except:
            venue = ""
        all_venues.append(venue)

    # Add list to dataframe
    df["venue"] = all_venues
    return df


def get_trainer(df: pd.DataFrame = None, outletAuthKey: str = None) -> pd.DataFrame:
    """This function returns the input dataframe with two extra collumns named ['trainer_home'] and ['trainer_away'].
    The match's trainers are listed in the column as a string.

    Args:
        df (pd.DataFrame): Minimum requirement: This function needs a dataframe as input that includes the ESPN data, concatenated with get_tournamentschedule().
        outletAuthKey (str): Statsperform Authorization Key e.g. (Eredivsie, Keuken Kampioen Divisie/KKD)

    Returns:
        pd.DataFrame: Returns the original input dataframe with two extra collumns included, named ['trainer_home'] and ['trainer_away'].
    """
    trainers_home = []
    trainers_away = []
    print("\nGet Trainers..")

    # Loop through match id's
    for match in tqdm(df.index):
        try:
            # Enter match id in API call
            response = requests.get(
                f"http://api.performfeeds.com/soccerdata/matchstats/{{}}/?_rt=b&_fmt=json&fx={{}}".format(
                    outletAuthKey, df["id"][match]
                )
            ).json()

            # Access venue information in json if available
            trainer_name_home = (
                response["liveData"]["lineUp"][0]["teamOfficial"]["firstName"]
                + " "
                + response["liveData"]["lineUp"][0]["teamOfficial"]["lastName"]
            )
            trainer_name_away = (
                response["liveData"]["lineUp"][1]["teamOfficial"]["firstName"]
                + " "
                + response["liveData"]["lineUp"][1]["teamOfficial"]["lastName"]
            )
        except:
            trainer_name_home = ""
            trainer_name_away = ""
        trainers_home.append(trainer_name_home)
        trainers_away.append(trainer_name_away)

    # Add list to dataframe
    df["trainer_home"] = trainers_home
    df["trainer_away"] = trainers_away
    return df


def get_keepers(df: pd.DataFrame = None, outletAuthKey: str = None) -> pd.DataFrame:
    """This function returns the input dataframe with two extra collumns named ['keeper_home'] and ['keeper_away'].
    The match's keepers are listed in the column as a string.

    Args:
        df (pd.DataFrame): Minimum requirement: This function needs a dataframe as input that includes the ESPN data, concatenated with get_tournamentschedule().
        outletAuthKey (str): Statsperform Authorization Key e.g. (Eredivsie, Keuken Kampioen Divisie/KKD)

    Returns:
        pd.DataFrame: Returns the original input dataframe with two extra collumns included, named ['keeper_home'] and ['keeper_away'].
    """
    keepers_home = []
    keepers_away = []
    print("\nGet Keepers..")

    # Loop through match id's
    for match in tqdm(df.index):
        try:
            # Enter match id in API call
            response = requests.get(
                f"http://api.performfeeds.com/soccerdata/matchstats/{{}}/?_rt=b&_fmt=json&fx={{}}".format(
                    outletAuthKey, df["id"][match]
                )
            ).json()

            # Access keeper information in json if available, next is used since it became a generator object.
            keeper_name_home = next(
                player["firstName"] + " " + player["lastName"]
                for player in response["liveData"]["lineUp"][0]["player"]
                if player["position"] == "Goalkeeper"
            )
            keeper_name_away = next(
                player["firstName"] + " " + player["lastName"]
                for player in response["liveData"]["lineUp"][1]["player"]
                if player["position"] == "Goalkeeper"
            )

        except:
            keeper_name_home = ""
            keeper_name_away = ""
        keepers_home.append(keeper_name_home)
        keepers_away.append(keeper_name_away)

    # Add list to dataframe
    df["keeper_home"] = keepers_home
    df["keeper_away"] = keepers_away
    return df


def get_score(df: pd.DataFrame = None, outletAuthKey: str = None) -> pd.DataFrame:
    """This function returns the input dataframe with two extra collumns named ['score_home'] and ['score_away'].

    Args:
        df (pd.DataFrame): Minimum requirement: This function needs a dataframe as input that includes the ESPN data,
        concatenated with get_tournamentschedule().
        outletAuthKey (str): Statsperform Authorization Key e.g. (Eredivsie, Keuken Kampioen Divisie/KKD)

    Returns:
        pd.DataFrame: Returns the original input dataframe with two extra collumns included, named ['score_home'] and ['score_away'].
    """

    # Create container for new column
    print("\nGet score..")
    scores_home = []
    scores_away = []
    # Loop through df to get match id's
    for match in tqdm(df.index):
        try:
            matchstats = requests.get(
                f"http://api.performfeeds.com/soccerdata/matchstats/{{}}/?_rt=b&_fmt=json&fx={{}}".format(
                    outletAuthKey, df["id"][match]
                )
            ).json()["liveData"]["matchDetails"]["scores"]["total"]
            score_home = matchstats["home"]
            score_away = matchstats["away"]
        except:
            score_home = ""  # If there is no score available
            score_away = ""
        scores_home.append(score_home)
        scores_away.append(score_away)

    # Add list to dataframe
    df["score_home"] = scores_home
    df["score_away"] = scores_away
    return df


def get_cup(
    df: pd.DataFrame = None,
    outletAuthKey: str = None,
    competition: str = None,
) -> pd.DataFrame:
    print("\nGet competitions..")
    cups = []
    for match in tqdm(df.index):
        try:
            response = requests.get(
                f"http://api.performfeeds.com/soccerdata/tournamentschedule/{{}}/{{}}?_rt=b&_fmt=json".format(
                    outletAuthKey, competition
                )
            ).json()["competition"]
            cup = response["name"]
        except:
            cup = ""
        cups.append(cup)
    df["cup"] = cups
    return df


def get_rankStatus(
    df: pd.DataFrame = None,
    outletAuthKey: str = None,
    competition: str = None,
) -> pd.DataFrame:
    (
        ranks_home,
        ranks_away,
        last_six_home,
        last_six_away,
        rank_statussen_home,
        rank_statussen_away,
        lastRanks_home,
        lastRanks_away,
    ) = ([] for i in range(8))

    print("\nGet rankstatus..")
    for match in tqdm(df.index):
        try:
            response = requests.get(
                f"http://api.performfeeds.com/soccerdata/standings/{{}}/?_rt=b&_fmt=json&tmcl={{}}".format(
                    outletAuthKey, competition
                )
            ).json()["stage"][0]["division"][0]["ranking"]
            for team_rank in response:
                if team_rank["contestantId"] == df["homeContestantId"][match]:
                    try:
                        rank_status_home = str(team_rank["rankStatus"])
                    except:
                        rank_status_home = ""
                    rank_home = str(team_rank["rank"])
                    lastRank_home = str(team_rank["lastRank"])
                    six_home = str(team_rank["lastSix"])
                if team_rank["contestantId"] == df["awayContestantId"][match]:
                    try:
                        rank_status_away = str(team_rank["rankStatus"])
                    except:
                        rank_status_away = ""
                    rank_away = str(team_rank["rank"])
                    lastRank_away = str(team_rank["lastRank"])
                    six_away = str(team_rank["lastSix"])
        except:
            (
                rank_home,
                rank_away,
                six_home,
                six_away,
                lastRank_home,
                lastRank_away,
            ) = (
                "",
                "",
                "",
                "",
                "",
                "",
            )
        ranks_home.append(rank_home)
        ranks_away.append(rank_away)
        last_six_home.append(six_home)
        last_six_away.append(six_away)
        rank_statussen_home.append(rank_status_home)
        rank_statussen_away.append(rank_status_away)
        lastRanks_home.append(lastRank_home)
        lastRanks_away.append(lastRank_away)
    (
        df["rank_home"],
        df["rank_away"],
        df["last_six_home"],
        df["last_six_away"],
        df["rank_status_home"],
        df["rank_status_away"],
        df["lastRank_home"],
        df["lastRank_away"],
    ) = (
        ranks_home,
        ranks_away,
        last_six_home,
        last_six_away,
        rank_statussen_home,
        rank_statussen_away,
        lastRanks_home,
        lastRanks_away,
    )
    return df


def translate_injury(injury):
    """
    Function that translates an injury from English to Dutch
    From dictionary with injuries that often occur; else translation by google translate
    :param injury: string with injury in English
    :return: string with injury in Dutch
    """

    translator = Translator()

    injuries = {
        "achilles tendon rupture": "gescheurde achillespees",
        "ankle/foot injury": "enkelblessure",
        "foot injury": "voetblessure",
        "hamstring": "hamstringblessure",
        "illness": "ziek",
        "knee injury": "knieblessure",
        "knock": "blessure",
        "thigh muscle strain": "verrekte dijspier",
        "calf/shin injury": "scheen- of kuitblessure",
        "groin strain": "verrekte lies",
        "groin/pelvis injury": "liesblessure",
        "neck injury": "nekblessure",
        "mcl knee ligament injury": "knieligamentblessure",
        "ankle ligaments": "enkelligamentblessure",
        "arm injury": "armblessure",
        "shoulder injury": "schouderblessure",
        "concussion": "hersenschudding",
    }

    try:
        translation = injuries[injury.lower()]
        return translation

    except KeyError:
        result = translator.translate(injury, src="en", dest="nl")
        return result.text


def get_injuries(
    df: pd.DataFrame = None,
    outletAuthKey: str = None,
    competition: str = None,
) -> pd.DataFrame:
    print("\nGet injuries..")
    home_injuries = []
    away_injuries = []
    for match in tqdm(df.index):
        try:
            home_response = requests.get(
                f"http://api.performfeeds.com/soccerdata/injuries/{{}}/?_rt=b&_fmt=json&tmcl={{}}&ctst={{}}".format(
                    outletAuthKey, competition, df["homeContestantId"][match]
                )
            ).json()["person"]
            away_response = requests.get(
                f"http://api.performfeeds.com/soccerdata/injuries/{{}}/?_rt=b&_fmt=json&tmcl={{}}&ctst={{}}".format(
                    outletAuthKey, competition, df["awayContestantId"][match]
                )
            ).json()["person"]
            home_injury = [
                str(home_injury["firstName"])
                + " "
                + str(home_injury["lastName"])
                + " van {} voetbalt niet mee vanwege een ".format(
                    df["homeContestantName"][match]
                )
                + translate_injury(str(home_injury["injury"][0]["type"]))
                # + " blessure."
                for home_injury in home_response
                for injury_details in home_injury["injury"]
                if "endDate" not in injury_details
            ]
            away_injury = [
                str(away_injury["firstName"])
                + " "
                + str(away_injury["lastName"])
                + " van {} voetbalt niet mee vanwege een ".format(
                    df["awayContestantName"][match]
                )
                + translate_injury(str(away_injury["injury"][0]["type"]))
                # + " blessure."
                for away_injury in away_response
                for injury_details in away_injury["injury"]
                if "endDate" not in injury_details
            ]
        except:
            home_injury = "None"
            away_injury = "None"
        home_injuries.append(list(set(home_injury)))
        away_injuries.append(list(set(away_injury)))
    (
        df["home_injuries"],
        df["away_injuries"],
    ) = (
        home_injuries,
        away_injuries,
    )
    return df


def get_formations(
    df: pd.DataFrame = None,
    outletAuthKey: str = None,
) -> pd.DataFrame:
    # Create container for new column
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
            cards = requests.get(
                f"http://api.performfeeds.com/soccerdata/matchstats/{{}}/?_rt=b&_fmt=json&fx={{}}".format(
                    outletAuthKey, df["id"][match]
                )
            ).json()["liveData"]["card"]
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

                substitute_player["timeMin"] = substitute["timeMin"]
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


def total_cards_player(
    df: pd.DataFrame = None,
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
                    playerCardsYellow.append(playerHome["playerName"])
                    cardsMatchYellow.append(playerHome["playerName"])
                # Rood of twee keer geel in wedstrijd
                if any([card in playerHome["playerName"] for card in ["🟨|🟨", "🟥"]]):
                    playerCardsRed.append(playerHome["playerName"])
                    cardsMatchRed.append(playerHome["playerName"])
            for playerAway in away:    
                if any([card in playerAway["playerName"] for card in ["🟨"]]):
                    playerCardsYellow.append(playerAway["playerName"])
                    cardsMatchYellow.append(playerAway["playerName"])
                if any([card in playerAway["playerName"] for card in ["🟨|🟨", "🟥"]]):
                    playerCardsRed.append(playerAway["playerName"])
                    cardsMatchRed.append(playerAway["playerName"])

            for playerSubHome in subHome:
                if any([card in playerSubHome["playerOnName"] for card in ["🟨"]]):
                    playerCardsYellow.append(playerSubHome["playerOnName"])
                    cardsMatchYellow.append(playerSubHome["playerOnName"])
                if any([card in playerSubHome["playerOnName"] for card in ["🟨|🟨", "🟥"]]):
                    playerCardsRed.append(playerSubHome["playerOnName"])
                    cardsMatchRed.append(playerSubHome["playerOnName"])

            for playerSubAway in subAway:
                if any([card in playerSubAway["playerOnName"] for card in ["🟨"]]):
                    playerCardsYellow.append(playerSubAway["playerOnName"])
                    cardsMatchYellow.append(playerSubAway["playerOnName"])
                if any([card in playerSubAway["playerOnName"] for card in ["🟨|🟨", "🟥"]]):
                    playerCardsRed.append(playerSubAway["playerOnName"])
                    cardsMatchRed.append(playerSubAway["playerOnName"])

            countRed = [x for x in playerCardsRed if x in cardsMatchRed]
            countYellow = [x for x in playerCardsYellow if x in cardsMatchYellow]
            cardsHistoryRed.append(dict(Counter(countRed)))
            cardsHistoryYellow.append(dict(Counter(countYellow)))
        except:
            cardsHistoryRed.append({})
            cardsHistoryYellow.append({})
    df["cardsHistoryRed"] = cardsHistoryRed
    df["cardsHistoryYellow"] = cardsHistoryYellow
    return df

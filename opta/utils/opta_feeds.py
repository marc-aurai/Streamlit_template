import pandas as pd
import requests
from tqdm import tqdm


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
            "homeContestantOfficialName",
            "awayContestantOfficialName",
            "homeContestantCode",
            "awayContestantCode",
        ]
    ]
    # Return only selected columns from dataframe


def get_matchstats_cards(df: pd.DataFrame, outletAuthKey: str) -> pd.DataFrame:
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
    print("Get Card Events..\n")

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
                    "playerName": card["playerName"],
                    "cardType": card["type"],
                }
                for card in matchstats
            ]
        except:
            team_cards = []  # If there are no cards available
        all_team_cards.append(team_cards)

    # Add list to dataframe
    df["card_events"] = all_team_cards
    return df


def get_matchstats_goals(df: pd.DataFrame, outletAuthKey: str) -> pd.DataFrame:
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
    print("Get Goal Events..\n")

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
                    "scorerName": goal["scorerName"],
                }
                for goal in matchstats
            ]
        except:
            team_goals = []  # If there are no goals available
        all_team_goals.append(team_goals)

    # Add list to dataframe
    df["goal_events"] = all_team_goals
    return df


def get_matchstats_possession(df: pd.DataFrame, outletAuthKey: str) -> pd.DataFrame:
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
    print("Get Possession Percentage..\n")
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
            possession_home = ""
            possession_away = ""
        all_possessions_home.append(possession_home)
        all_possessions_away.append(possession_away)

    df["possession_home"] = all_possessions_home
    df["possession_away"] = all_possessions_away
    return df


def get_venue(df: pd.DataFrame, outletAuthKey: str) -> pd.DataFrame:
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
    print("Get venues..\n")

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

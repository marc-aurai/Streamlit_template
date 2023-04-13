import pandas as pd
import requests


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
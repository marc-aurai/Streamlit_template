import pandas as pd
import requests
from tqdm import tqdm


def get_tournamentschedule(
    table_kind="tournamentschedule", competitions=["d1k1pqdg2yvw8e8my74yvrdw4", "dp0vwa5cfgx2e733gg98gfhg4", "bp1sjjiswd4t3nw86vf6yq7hm"] #ID's van Eredivisie seizoenen volgorde 23/22/21
) -> tuple[str, str, pd.DataFrame]:
    df_all_matches = pd.DataFrame() # From different competitions as well

    # Loop through different divisions 
    for competition in competitions:
        url = f"http://api.performfeeds.com/soccerdata/{{}}/6bxvue6su4ev1690mzy62a41t/{{}}?_rt=b&_fmt=json".format(
            table_kind, competition
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

    return (
        response["competition"]["name"],
        table_kind,

        # Return only selected columns from dataframe 
        df_all_matches[
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
        ],
    )


def get_matchstats_cards(df: pd.DataFrame) -> pd.DataFrame:
    """
    Function to get the stats on cards during a match 
    Loops through df containing match id's and performs API call to statsperform 
    """

    # Create container for new column
    all_team_cards = []
    print("Get Card Events..\n")

    # Loop through df to get match id's 
    for match in tqdm(df.index):
        try:
            matchstats = (
                requests.get(
                    f"http://api.performfeeds.com/soccerdata/matchstats/6bxvue6su4ev1690mzy62a41t/?_rt=b&_fmt=json&fx={{}}".format(df['id'][match])
                )

                # Access card information from live data 
                .json()["liveData"]["card"]
            )

            # For every card event, create dict with info and add to list 
            team_cards = [{'contestantName': requests.get(f"http://api.performfeeds.com/soccerdata/team/6bxvue6su4ev1690mzy62a41t/?_rt=b&_fmt=json&ctst={{}}"
                                                           .format(card["contestantId"])
                    )
                    .json()["contestant"][0]["name"],
                    'contestantId': card["contestantId"],
                    'periodId': card["periodId"],
                    'timeMin': card["timeMin"],
                    'playerId': card["playerId"],
                    'playerName': card["playerName"],
                    'cardType': card["type"],
                }
                for card in matchstats
            ]
        except:
            team_cards = [] # If there are no cards available 
        all_team_cards.append(team_cards)

    # Add list to dataframe 
    df['card_events'] = all_team_cards
    return df


def get_matchstats_goals(df: pd.DataFrame) -> pd.DataFrame:
    """Currenty assistPlayerName is not supported, since this does not occur in every goal"""
    
    # Container for new column 
    all_team_goals = []
    print("Get Goal Events..\n")

    # Loop through df to get all match id's
    for match in tqdm(df.index):
        try:
            matchstats = (
                requests.get(
                    f"http://api.performfeeds.com/soccerdata/matchstats/6bxvue6su4ev1690mzy62a41t/?_rt=b&_fmt=json&fx={{}}".format(df['id'][match])
                )

                # Access goal information from live data 
                .json()["liveData"]["goal"]
            )

            # For every event, create dict with info and add to list 
            team_goals = [
                {
                    'contestantName': requests.get(
                        f"http://api.performfeeds.com/soccerdata/team/6bxvue6su4ev1690mzy62a41t/?_rt=b&_fmt=json&ctst={{}}".format(
                            goal["contestantId"])
                    ).json()["contestant"][0]["name"],
                    'contestantId': goal["contestantId"],
                    'periodId': goal["periodId"],
                    'timeMin': goal["timeMin"],
                    'scorerId': goal["scorerId"],
                    'scorerName' : goal["scorerName"]
                }
                for goal in matchstats
            ]
        except:
                team_goals = [] # If there are no goals available 
        all_team_goals.append(team_goals)

    # Add list to dataframe 
    df['goal_events'] = all_team_goals
    return df

def get_venue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Function to get venues for matches 
    """

    # Container for new venues column 
    all_venues = []
    print("Get venues..\n")

    # Loop through match id's 
    for match in tqdm(df.index):
        try:

            # Enter match id in API call 
            response = requests.get(f'http://api.performfeeds.com/soccerdata/matchstats/6bxvue6su4ev1690mzy62a41t/?_rt=b&_fmt=json&fx={{}}'.format(
                df['id'][match])
                ).json()
            
            # Access venue information in json if available 
            venue = response['matchInfo']['venue']['longName']
        except:
            venue = ""
        all_venues.append(venue)

    # Add list to dataframe 
    df['venue'] = all_venues
    return df
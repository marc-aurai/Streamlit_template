import requests
import pandas as pd
from tqdm import tqdm

def get_tournamentschedule(
    table_kind="tournamentschedule", competition_season_id="d1k1pqdg2yvw8e8my74yvrdw4"
) -> tuple[str, str, pd.DataFrame]:
    url = f"http://api.performfeeds.com/soccerdata/{{}}/6bxvue6su4ev1690mzy62a41t/{{}}?_rt=b&_fmt=json".format(
        table_kind, competition_season_id
    )
    response = requests.get(url).json()
    df_matches = pd.DataFrame()
    df_matches = pd.concat(
        [
            pd.concat(
                [df_matches, pd.DataFrame(response["matchDate"][matches]["match"])]
            )
            for matches in range(len(response["matchDate"]))
        ],
        ignore_index=True,
    )
    return (
        response["competition"]["name"],
        table_kind,
        df_matches[
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
    all_team_cards = []
    print("Get Card Events..\n")
    for match in tqdm(df.index):
        try:
            matchstats = (
                requests.get(
                    f"http://api.performfeeds.com/soccerdata/matchstats/6bxvue6su4ev1690mzy62a41t/?_rt=b&_fmt=json&fx={{}}".format(df['id'][match])
                )
                .json()["liveData"]["card"]
            )
            team_cards = [
                [
                    requests.get(
                        f"http://api.performfeeds.com/soccerdata/team/6bxvue6su4ev1690mzy62a41t/?_rt=b&_fmt=json&ctst={{}}".format(
                            card["contestantId"]
                        )
                    ).json()["contestant"][0]["name"],
                    card["contestantId"],
                    card["periodId"],
                    card["timeMin"],
                    card["playerName"],
                    card["type"],
                ]
                for card in matchstats
            ]
        except:
                team_cards = []
        all_team_cards.append(team_cards)
    df['card_events'] = all_team_cards
    return df


def get_matchstats_goals(df: pd.DataFrame) -> pd.DataFrame:
    """Currenty assistPlayerName is not supported, since this does not occur in every goal"""
    all_team_goals = []
    print("Get Goal Events..\n")
    for match in tqdm(df.index):
        try:
            matchstats = (
                requests.get(
                    f"http://api.performfeeds.com/soccerdata/matchstats/6bxvue6su4ev1690mzy62a41t/?_rt=b&_fmt=json&fx={{}}".format(df['id'][match])
                )
                .json()["liveData"]["goal"]
            )
            team_goals = [
                [
                    requests.get(
                        f"http://api.performfeeds.com/soccerdata/team/6bxvue6su4ev1690mzy62a41t/?_rt=b&_fmt=json&ctst={{}}".format(
                            goal["contestantId"]
                        )
                    ).json()["contestant"][0]["name"],
                    goal["contestantId"],
                    goal["periodId"],
                    goal["timeMin"],
                    goal["scorerName"]
                ]
                for goal in matchstats
            ]
        except:
                team_goals = []
        all_team_goals.append(team_goals)
    df['goal_events'] = all_team_goals
    return df

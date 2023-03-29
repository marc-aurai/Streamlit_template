import pandas as pd
import requests
from utils.opta_feeds import (
    get_matchstats_cards,
    get_matchstats_goals,
    get_tournamentschedule,
)


def get_espn_data(csv_name: str) -> pd.DataFrame:
    df_espn = pd.read_csv(
        "./espn_scraper/scraper_data/{}.csv".format(csv_name), sep=";"
    )
    return df_espn


def refactor_df(df_tournament: pd.DataFrame) -> pd.DataFrame:
    df_tournament["awayContestantCode"] = df_tournament[
        "awayContestantCode"
    ].str.replace("NEC", "N.E.C.", regex=True)
    df_tournament["homeContestantCode"] = df_tournament[
        "homeContestantCode"
    ].str.replace("NEC", "N.E.C.", regex=True)
    df_tournament["awayContestantCode"] = df_tournament[
        "awayContestantCode"
    ].str.replace("AJX", "AJA", regex=True)
    df_tournament["homeContestantCode"] = df_tournament[
        "homeContestantCode"
    ].str.replace("AJX", "AJA", regex=True)
    return df_tournament


def merge(df_espn: pd.DataFrame, df_tournament: pd.DataFrame) -> pd.DataFrame:
    df_merged = pd.merge(
        df_espn,
        df_tournament,
        how="left",
        left_on=["date", "home_abbrev", "away_abbrev"],
        right_on=["date", "homeContestantCode", "awayContestantCode"],
    )
    df_merged.drop(
        df_merged.filter(regex="Unname"), axis=1, inplace=True
    )  # Drop unnamed columns
    return df_merged


if __name__ == "__main__":
    df_espn = get_espn_data(csv_name="articles_28")
    competition, table_kind, df_tournament = get_tournamentschedule()
    df_tournament = refactor_df(df_tournament)
    df_cards = get_matchstats_cards(df_tournament)
    df_goals = get_matchstats_goals(df_cards)

    df_merged = merge(df_espn, df_goals)

    df_tournament.to_csv(
        "./opta/data/{}_{}.csv".format(table_kind, competition), sep=";"
    )
    df_merged.to_csv("./opta/data/merged/merged_{}.csv".format(table_kind), sep=";")
    df_cards.to_csv("./opta/data/merged/cards.csv", sep=";")
    df_goals.to_csv("./opta/data/merged/goals.csv", sep=";")

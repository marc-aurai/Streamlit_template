import pandas as pd
import requests
from utils.opta_feeds import (
    get_matchstats_cards,
    get_matchstats_goals,
    get_tournamentschedule,
    get_venue,
)


def get_espn_data(csv_name: str) -> pd.DataFrame:
    """ Loads the scraped ESPN data from: /espn_scraper/scraper_data

    Args:
        csv_name (str): Name of the scraped ESPN dataset you want to load

    Returns:
        pd.DataFrame: Returns the dataset as a pandas dataframe
    """
    df_espn = pd.read_csv(
        "./espn_scraper/scraper_data/{}.csv".format(csv_name), sep=";"
    )
    return df_espn



def merge(df_espn: pd.DataFrame, df_tournament: pd.DataFrame) -> pd.DataFrame:
    """ Merge different OPTA tables with each other. Furthermore, this function merges the scraped ESPN Data with OPTA data.

    Args:
        df_espn (pd.DataFrame): Dataframe with ESPN Data
        df_tournament (pd.DataFrame): Dataframe with all matches from the selected cup/tournaments -> ()

    Returns:
        pd.DataFrame: Merged dataframe with ESPN data and OPTA Data
    """
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
    df_espn = get_espn_data(csv_name="articles_eredivisie22_23")
    competition, table_kind, df_tournament = get_tournamentschedule()
    df_cards = get_matchstats_cards(df_tournament)
    df_venues = get_venue(df_cards)
    df_goals = get_matchstats_goals(df_venues)

    df_merged = merge(df_espn, df_goals)

    df_tournament.to_csv(
        "./opta/data/{}_{}.csv".format(table_kind, competition), sep=";"
    )
    df_merged.to_csv("./opta/data/merged/merged.csv", sep=";", index=False)
    df_merged.to_excel("./opta/data/merged/merged.xlsx", index=False)

    df_cards.to_csv("./opta/data/merged/cards.csv", sep=";")
    df_goals.to_csv("./opta/data/merged/goals.csv", sep=";")

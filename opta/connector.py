import pandas as pd
from utils.opta_feeds import (
    get_matchstats_cards,
    get_matchstats_goals,
    get_tournamentschedule,
    get_venue,
    get_matchstats_possession,
)


def get_espn_data(csv_name: str) -> pd.DataFrame:
    """ Loads the scraped ESPN data from: /espn_scraper/scraper_data as a pandas dataframe

    Args:
        csv_name (str): Name of the scraped ESPN dataset you want to load

    Returns:
        pd.DataFrame: Returns the ESPN dataset as a pandas dataframe
    """
    df_espn = pd.read_csv(
        "./espn_scraper/scraper_data/{}.csv".format(csv_name), sep=";"
    )
    return df_espn


def refactor_df(df_tournament: pd.DataFrame) -> pd.DataFrame:
    """ Club abbreviation Modifications. E.g. NEC -> N.E.C.

    Args:
        df_tournament (pd.DataFrame): Dataframe that includes all matches, from the selected competitions.

    Returns:
        pd.DataFrame: Returns a refactored Dataframe
    """
    opta_team_abbreviations = ["NEC", "AJX", "ZWO"]
    espn_team_abbreviations = ["N.E.C.", "AJA", "PEC"]
    for opta_abbr, espn_abbr in zip(opta_team_abbreviations, espn_team_abbreviations):
        df_tournament["awayContestantCode"] = df_tournament[
            "awayContestantCode"
        ].str.replace(opta_abbr, espn_abbr, regex=True)
        df_tournament["homeContestantCode"] = df_tournament[
            "homeContestantCode"
        ].str.replace(opta_abbr, espn_abbr, regex=True)
    return df_tournament


def merge(df_espn: pd.DataFrame, df_tournament: pd.DataFrame) -> pd.DataFrame:
    """ Merge different OPTA tables with each other. 
    Furthermore, this function merges the scraped ESPN Data with OPTA data.

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
    df_espn = get_espn_data(csv_name="articles_eredivisie")
    
    df_tournament = get_tournamentschedule()
    df_tournament = refactor_df(df_tournament)
    df_possession = get_matchstats_possession(df_tournament)
    df_cards = get_matchstats_cards(df_possession)
    df_venues = get_venue(df_cards)
    df_goals = get_matchstats_goals(df_venues)

    df_merged = merge(df_espn, df_goals)
    df_merged.to_csv("./opta/data/merged/merged.csv", sep=";", index=False)

import os

import pandas as pd
from dotenv import load_dotenv
from utils.opta_feeds import (
    get_matchstats_cards,
    get_matchstats_goals,
    get_matchstats_possession,
    get_tournamentschedule,
    get_venue,
    get_trainer,
    get_keepers,
)

load_dotenv()
outletAuthKey_ereD = os.getenv("outletAuthKey_ereD")
outletAuthKey_KKD = os.getenv("outletAuthKey_KKD")


def get_espn_data(csv_name: str) -> pd.DataFrame:
    """Loads the scraped ESPN data from: /espn_scraper/scraper_data as a pandas dataframe

    Args:
        csv_name (str): Name of the scraped ESPN dataset you want to load

    Returns:
        pd.DataFrame: Returns the ESPN dataset as a pandas dataframe
    """
    df_espn = pd.read_csv(
        "./espn_scraper/scraper_data/{}.csv".format(csv_name), sep=";"
    )
    return df_espn.dropna()


def refactor_df(
    df_tournament: pd.DataFrame,
    opta_team_abbreviations: list,
    espn_team_abbreviations: list,
) -> pd.DataFrame:
    """Club abbreviation Modifications. E.g. NEC -> N.E.C.

    Args:
        df_tournament (pd.DataFrame): Dataframe that includes all matches, from the selected competitions.

    Returns:
        pd.DataFrame: Returns a refactored Dataframe
    """
    for opta_abbr, espn_abbr in zip(opta_team_abbreviations, espn_team_abbreviations):
        df_tournament["awayContestantCode"] = df_tournament[
            "awayContestantCode"
        ].str.replace(opta_abbr, espn_abbr, regex=True)
        df_tournament["homeContestantCode"] = df_tournament[
            "homeContestantCode"
        ].str.replace(opta_abbr, espn_abbr, regex=True)
    return df_tournament


def merge(df_espn: pd.DataFrame, df_tournament: pd.DataFrame) -> pd.DataFrame:
    """Merge different OPTA tables with each other.
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


def eredivisie() -> pd.DataFrame:
    """Concatenates the ESPN scraped data (Eredivisie articles)
    with the right matches and its data from OPTA Tables.

    Returns:
        pd.DataFrame: Returns a dataframe with ESPN and OPTA concatenated.
    """
    print("Eredivisie.. \n")
    df_espn = get_espn_data(csv_name="articles_eredivisie")

    df_tournament = get_tournamentschedule(
        outletAuthKey=outletAuthKey_ereD,
        competitions=[
            "d1k1pqdg2yvw8e8my74yvrdw4",
            "dp0vwa5cfgx2e733gg98gfhg4",
            "bp1sjjiswd4t3nw86vf6yq7hm",
        ],
    )

    df_tournament = refactor_df(
        df_tournament,
        opta_team_abbreviations=[
            "NEC",
            "AJX",
            "ZWO",
        ],
        espn_team_abbreviations=["N.E.C.", "AJA", "PEC"],
    )
    df_possession = get_matchstats_possession(
        df_tournament, outletAuthKey=outletAuthKey_ereD
    )
    df_cards = get_matchstats_cards(df_possession, outletAuthKey=outletAuthKey_ereD)
    df_venues = get_venue(df_cards, outletAuthKey=outletAuthKey_ereD)
    df_goals = get_matchstats_goals(df_venues, outletAuthKey=outletAuthKey_ereD)
    df_trainers = get_trainer(df_goals, outletAuthKey=outletAuthKey_ereD)
    df_keepers = get_keepers(df_trainers, outletAuthKey=outletAuthKey_ereD)

    df_merged = merge(df_espn, df_keepers).dropna()
    df_merged.to_csv("./opta/data/merged/merged_ereD.csv", sep=";", index=False)
    return df_merged


def KKD() -> pd.DataFrame:
    """Concatenates the ESPN scraped data (Keuken Kampioen Divisie articles)
    with the right matches and its data from OPTA Tables.

    Returns:
        pd.DataFrame: Returns a dataframe with ESPN and OPTA concatenated.
    """
    print("Keuken Kampioen Divisie.. \n")
    df_espn = get_espn_data(csv_name="articles_KKD2")

    df_tournament = get_tournamentschedule(
        outletAuthKey=outletAuthKey_KKD,
        competitions=[
            "1w03tfpd5nc6woo8j2nc9239w",
            "8arv967ero2aknwkin9m3zsic",
            "55a24w8bxnmf1o3vlhw9qh562",
        ],
    )

    df_tournament = refactor_df(
        df_tournament,
        opta_team_abbreviations=[
            "NEC",
            "AJX",
            "ZWO",
            "UT2",
            "OSS",
            "PSV",
            "AZ2",
            "EHV",
        ],
        espn_team_abbreviations=[
            "N.E.C.",
            "JAJ",
            "PEC",
            "JUT",
            "TOP",
            "JPS",
            "JAZ",
            "EIN",
        ],
    )
    df_possession = get_matchstats_possession(
        df_tournament, outletAuthKey=outletAuthKey_KKD
    )
    df_cards = get_matchstats_cards(df_possession, outletAuthKey=outletAuthKey_KKD)
    df_venues = get_venue(df_cards, outletAuthKey=outletAuthKey_KKD)
    df_goals = get_matchstats_goals(df_venues, outletAuthKey=outletAuthKey_KKD)
    df_trainers = get_trainer(df_goals, outletAuthKey=outletAuthKey_KKD)
    df_keepers = get_keepers(df_trainers, outletAuthKey=outletAuthKey_KKD)

    df_merged = merge(df_espn, df_keepers).dropna()
    df_merged.to_csv("./opta/data/merged/merged_KKD.csv", sep=";", index=False)
    return df_merged


if __name__ == "__main__":
    df_ereD = eredivisie()
    df_KKD = KKD()
    df_merged = pd.concat([df_ereD, df_KKD], ignore_index=True).dropna()
    df_merged.to_csv("./opta/data/merged/merged.csv", sep=";", index=False)

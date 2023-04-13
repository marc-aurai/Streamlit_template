import os

import pandas as pd
from dotenv import load_dotenv
from utils.soccer_prompt import prompt_engineering
from utils.opta_feeds import (
    get_keepers,
    get_matchstats_cards,
    get_matchstats_goals,
    get_matchstats_possession,
    get_tournamentschedule,
    get_trainer,
    get_venue,
    get_score,
    get_cup,
)

load_dotenv()
outletAuthKey_ereD = os.getenv("outletAuthKey_ereD")
outletAuthKey_KKD = os.getenv("outletAuthKey_KKD")


def competition(outletAuthKey_competition: str):
    df_tournament = get_tournamentschedule(
        outletAuthKey=outletAuthKey_competition,
        competitions=[
            "d1k1pqdg2yvw8e8my74yvrdw4",  # Eredivisie 22/23
        ],
    )
    return df_tournament

def streamlit_request(date):
    df_tournament = competition(
        outletAuthKey_ereD
    )  # Selecteer op datum vanuit streamlit
    df_matches_on_date = df_tournament.loc[df_tournament["date"] == date]

    df = get_cup(df_matches_on_date, outletAuthKey_ereD, competition="d1k1pqdg2yvw8e8my74yvrdw4")
    df = get_score(df, outletAuthKey_ereD)
    df = get_matchstats_possession(df, outletAuthKey_ereD)
    df = get_matchstats_cards(df, outletAuthKey_ereD)
    df = get_venue(df, outletAuthKey_ereD)
    df = get_matchstats_goals(df, outletAuthKey_ereD)
    df = get_trainer(df, outletAuthKey_ereD)
    df = get_keepers(df, outletAuthKey_ereD)
    df_openai = prompt_engineering(df=df)
    return df_openai

if __name__ == "__main__":
    df_tournament = competition(
        outletAuthKey_ereD
    )  # Selecteer op datum vanuit streamlit
    df_matches_on_date = df_tournament.loc[df_tournament["date"] == "2023-03-14Z"]
    print(df_matches_on_date)

    df = get_cup(df_matches_on_date, outletAuthKey_ereD, competition="d1k1pqdg2yvw8e8my74yvrdw4")
    df = get_score(df, outletAuthKey_ereD)
    df = get_matchstats_possession(df, outletAuthKey_ereD)
    df = get_matchstats_cards(df, outletAuthKey_ereD)
    df = get_venue(df, outletAuthKey_ereD)
    df = get_matchstats_goals(df, outletAuthKey_ereD)
    df = get_trainer(df, outletAuthKey_ereD)
    df = get_keepers(df, outletAuthKey_ereD)
    print(df)
    # df.to_csv("./opta/data/automated_opta_pipeline.csv", sep=";", index=False)
    df_openai = prompt_engineering(df=df)
    print(df_openai)
    # df_openai.to_csv("./opta/data/automated_opta_pipeline_openai.csv", line_terminator="\n")
    # return df_openai
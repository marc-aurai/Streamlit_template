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
    get_rankStatus,
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


if __name__ == "__main__":
    df = (
        competition(outletAuthKey_ereD)
        .pipe(get_cup, outletAuthKey_ereD, competition="d1k1pqdg2yvw8e8my74yvrdw4")
        .pipe(get_score,outletAuthKey_ereD)
        .pipe(get_matchstats_possession, outletAuthKey_ereD)
        .pipe(get_matchstats_cards, outletAuthKey_ereD)
        .pipe(get_venue, outletAuthKey_ereD)
        .pipe(get_matchstats_goals, outletAuthKey_ereD)
        .pipe(get_trainer, outletAuthKey_ereD)
        .pipe(get_keepers, outletAuthKey_ereD)
        .pipe(get_rankStatus, outletAuthKey_ereD, competition="d1k1pqdg2yvw8e8my74yvrdw4").dropna()
        .pipe(prompt_engineering)
    )

    df.to_csv("./pages/data/eredivisie.csv", line_terminator="\n")
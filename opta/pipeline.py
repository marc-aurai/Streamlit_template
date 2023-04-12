import os

import pandas as pd
from dotenv import load_dotenv
from sklearn.pipeline import Pipeline
from utils.opta_feeds import (get_keepers, get_matchstats_cards,
                              get_matchstats_goals, get_matchstats_possession,
                              get_tournamentschedule, get_trainer, get_venue)

load_dotenv()
outletAuthKey_ereD = os.getenv("outletAuthKey_ereD")
outletAuthKey_KKD = os.getenv("outletAuthKey_KKD")


def competition(outletAuthKey_competition: str):
    df_tournament = get_tournamentschedule(
        outletAuthKey=outletAuthKey_competition,
        competitions=[
            "d1k1pqdg2yvw8e8my74yvrdw4", # Eredivisie 22/23
        ],
    )
    return df_tournament


if __name__ == "__main__":
    df_tournament = competition(outletAuthKey_ereD) # Selecteer op datum vanuit streamlit
    df_matches_on_date = df_tournament.loc[df_tournament["date"] == "2023-03-19Z"]
    print(df_matches_on_date)
    opta_pipeline = Pipeline([
        ('Possession', get_matchstats_possession(outletAuthKey=outletAuthKey_ereD)),
        ('Cards', get_matchstats_cards(outletAuthKey=outletAuthKey_ereD)),
        ('Venue', get_venue(outletAuthKey=outletAuthKey_ereD)),
        ('Goals', get_matchstats_goals(outletAuthKey=outletAuthKey_ereD)),
        ('Trainers', get_trainer(outletAuthKey=outletAuthKey_ereD)),
        ('Keepers', get_keepers(outletAuthKey=outletAuthKey_ereD))
    ])

    df_opta = opta_pipeline.fit(df_matches_on_date)
    print(type(df_opta))
    # df_opta.to_csv("./opta/data/automated_opta_pipeline.csv", sep=";", index=False)
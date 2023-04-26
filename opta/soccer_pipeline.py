import argparse
import os

import pandas as pd
from dotenv import load_dotenv
from googletrans import Translator
from utils.opta_feeds import (
    get_cup,
    get_formations,
    get_injuries,
    get_keepers,
    get_matchstats_cards,
    get_matchstats_goals,
    get_matchstats_possession,
    get_rankStatus,
    get_score,
    get_tournamentschedule,
    get_trainer,
    get_venue,
)
from utils.soccer_prompt import prompt_engineering

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument(
    "--competitie_name",
    help="Geef de naam van de competitie. Bijvoorbeeld: Eredivisie..",
    type=str,
    default="eredivisie",
)
parser.add_argument(
    "--competitie_id",
    help="Opta ID van de competitie. Bijvoorbeeld Eredivisie 22/23 = d1k1pqdg2yvw8e8my74yvrdw4",
    type=str,
    default="d1k1pqdg2yvw8e8my74yvrdw4",
)
parser.add_argument(
    "--outletAuthKey",
    help="De authorisatie key vanuit OPTA die je wilt gebruiken: "+str([key for key in list(dict(os.environ).keys()) if key.startswith('outlet')]),
    type=str,
    default="outletAuthKey_ereD",
)
args = parser.parse_args()

outletAuthKey = os.getenv(str(args.outletAuthKey))

def competition(outletAuthKey_competition: str) -> pd.DataFrame:
    df_tournament = get_tournamentschedule(
        outletAuthKey=outletAuthKey_competition,
        competitions=[
            "d1k1pqdg2yvw8e8my74yvrdw4",  # Eredivisie 22/23
        ],
    )
    return df_tournament


if __name__ == "__main__":
    competitie_name = args.competitie_name
    competition_ID = args.competitie_id
    df, player_stats = (
        competition(outletAuthKey)
        .pipe(get_cup, outletAuthKey, competition=competition_ID)
        .pipe(get_score, outletAuthKey)
        .pipe(get_matchstats_possession, outletAuthKey)
        .pipe(get_matchstats_cards, outletAuthKey)
        .pipe(get_venue, outletAuthKey)
        .pipe(get_matchstats_goals, outletAuthKey)
        .pipe(get_trainer, outletAuthKey)
        .pipe(get_keepers, outletAuthKey)
        .pipe(get_injuries, outletAuthKey, competition=competition_ID)
        .pipe(get_rankStatus, outletAuthKey, competition=competition_ID)
        .pipe(get_formations, outletAuthKey)
        .dropna()
        .pipe(prompt_engineering)
    )

    df.to_csv("./pages/data/{}.csv".format(competitie_name), line_terminator="\n")
    player_stats.to_csv(
        "./pages/data/{}_playerstats.csv".format(competitie_name), line_terminator="\n"
    )

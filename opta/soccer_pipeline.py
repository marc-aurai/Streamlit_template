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
from utils.aws_secrets import get_secret
from utils.S3_write import data_to_S3


load_dotenv()


def _argParser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--folder_name",
        help="Geef de naam van de folder waarin je de dataset wilt opslaan in de S3 bucket.",
        type=str,
        default="no_name",
    )
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
        default="d1k1pqdg2yvw8e8my74yvrdw4", # Eredivisie 22/23
    )
    parser.add_argument(
        "--outletAuthKey",
        help="De authorisatie key vanuit OPTA die je wilt gebruiken: "
        + str(
            [key for key in list(dict(os.environ).keys()) if key.startswith("outlet")]
        ),
        type=str,
        default="outletAuthKey_ereD",
    )
    args = parser.parse_args()
    return args


def _OptaKey(args) -> str:
    try:
        outletAuthKey = get_secret(
            secret_name="dev/{}".format(str(args.outletAuthKey)), region="eu-central-1"
        )
        outletAuthKey = outletAuthKey["outletAuthKey"]
        print("AWS Secret FOUND.")
        return outletAuthKey
    except:
        print("AWS Secret not found.")
    try:
        outletAuthKey = os.getenv(str(args.outletAuthKey))
        return outletAuthKey
    except:
        print("Local .env Secret not found.")


if __name__ == "__main__":
    args = _argParser()
    outletAuthKey = _OptaKey(args=args)
    competitie_name = args.competitie_name
    competition_ID = args.competitie_id
    df, player_stats = (
        get_tournamentschedule(
            outletAuthKey,
            competitions=[
                competition_ID,  
            ],
        )
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
    try:
        status = data_to_S3(
            file_name="./pages/data/{}.csv".format(competitie_name),
            bucket="gpt-ai-tool-wsc",
            object_name="prompt_OPTA_data/{}/{}.csv".format(args.folder_name, competitie_name),
        )
        status = data_to_S3(
            file_name="./pages/data/{}_playerstats.csv".format(competitie_name),
            bucket="gpt-ai-tool-wsc",
            object_name="prompt_OPTA_data/{}/{}_playerstats.csv".format(args.folder_name, competitie_name),
        )
    except:
        print("Not able to write to S3 Bucket")

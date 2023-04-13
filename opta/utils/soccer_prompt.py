import pandas as pd
from utils.prompt_engineering import (
    date,
    competition,
    final_score,
    home_vs_away,
    venue,
    card_events,
    goal_events,
    possession,
    trainer,
    keeper,
)


def select_features(df: pd.DataFrame) -> pd.DataFrame:
    return df[
        [
            "score_home",
            "score_away",
            "date",
            "cup",
            "possession_home",
            "possession_away",
            "card_events",
            "venue",
            "goal_events",
            "homeContestantId",
            "awayContestantId",
            "trainer_home",
            "trainer_away",
            "keeper_home",
            "keeper_away",
            "homeContestantOfficialName",
            "awayContestantOfficialName",
        ]
    ]

def prompt_engineering(df: pd.DataFrame):
    df_selection = select_features(df=df)
    dates = date(df_selection)
    home_versus_away = home_vs_away(df_selection)
    venue_names = venue(df_selection)
    competition_names = competition(df_selection)
    final_scores = final_score(df_selection)
    goals = goal_events(df_selection)
    cards = card_events(df_selection)
    possesion_stats = possession(df_selection)
    trainers = trainer(df_selection)
    keepers = keeper(df_selection)
    prompt_df = pd.DataFrame(
        {
            "dates": dates,
            "home_vs_away": home_versus_away,
            "venue": venue_names,
            "competition": competition_names,
            "final_score": final_scores,
            "possession": possesion_stats,
            "trainers": trainers,
            "keepers": keepers,
            "goal_events": goals,
            "card_events": cards,
        }
    )
    # Flatten list of goal and card events per match.
    prompt_df["goal_events"] = [
        ", ".join(map(str, l)) for l in prompt_df["goal_events"]
    ]
    prompt_df["card_events"] = [
        ", ".join(map(str, l)) for l in prompt_df["card_events"]
    ]

    openai_df = pd.DataFrame()
    openai_df["date"] = df_selection["date"]
    openai_df["match"] = (
        df_selection["homeContestantOfficialName"]
        + " vs "
        + df_selection["awayContestantOfficialName"]
    )

    openai_df["prompt"] = (
        "Geef de samenvatting een pakkende titel en schrijf een voetbal wedstrijd samenvatting inclusief paragrafen met de volgende informatie:\n"
        + prompt_df.dates.values
        + " "
        + prompt_df.home_vs_away.values
        + " "
        + prompt_df.venue.values
        + ".\n"
        + prompt_df.competition.values
        + ".\n"
        + prompt_df.final_score.values
        + ".\n"
        + prompt_df.goal_events.values
        + ".\n"
        + prompt_df.card_events.values
        + ".\n"
        + prompt_df.possession.values
        + ".\n"
        + prompt_df.trainers.values
        + ".\n"
        + prompt_df.keepers.values
        + ".\n\n###\n\n"  # stop sequence, tip from openAI
    )
    return openai_df

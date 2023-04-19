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
    rank_status_home,
    rank_status_away,
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
            "last_six_home",
            "last_six_away",
            "rank_home",
            "rank_away",
            "rank_status_home",
            "rank_status_away",
            "home_injuries",
            "away_injuries",
            "formation_home",
            "formation_away",
        ]
    ]


def prompt_engineering(df: pd.DataFrame):
    df_selection = select_features(df=df)
    prompt_df = pd.DataFrame(
        {
            "dates": date(df_selection),
            "home_vs_away": home_vs_away(df_selection),
            "venue": venue(df_selection),
            "competition": competition(df_selection),
            "final_score": final_score(df_selection),
            "possession": possession(df_selection),
            "trainers": trainer(df_selection),
            "keepers": keeper(df_selection),
            "goal_events": goal_events(df_selection),
            "card_events": card_events(df_selection),
            "rank_status_home": rank_status_home(df_selection),
            "rank_status_away": rank_status_away(df_selection),
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
    openai_df = df_selection[
        [
            "date",
            "last_six_home",
            "last_six_away",
            "rank_home",
            "rank_away",
            "rank_status_home",
            "rank_status_away",
            "home_injuries",
            "away_injuries",
            "formation_home",
            "formation_away",
        ]
    ].copy()
    openai_df["home_team"] = df_selection["homeContestantOfficialName"]
    openai_df["away_team"] = df_selection["awayContestantOfficialName"]
    openai_df["trainers"] = prompt_df["trainers"]
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
        + prompt_df.rank_status_home.values
        + prompt_df.rank_status_away.values
        # + prompt_df.keepers.values
        + "\n\n###\n\n"  # stop sequence, tip from openAI
    )
    return openai_df

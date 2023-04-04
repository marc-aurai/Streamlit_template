import pandas as pd
from utils.prompt_engineering import (
    date,
    competition,
    final_score,
    home_vs_away,
    venue,
    card_events,
    goal_events,
    article_completion,
)


def get_data() -> pd.DataFrame:
    return pd.read_csv("./opta/data/merged/merged.csv", sep=";").dropna()


def select_features(df: pd.DataFrame) -> pd.DataFrame:
    return df[
        [
            "home_team",
            "away_team",
            "score_home",
            "score_away",
            "date",
            "cup",
            "article_title",
            "article",
            "possession_home",
            "possession_away",
            "card_events",
            "venue",
            "goal_events",
        ]
    ]


if __name__ == "__main__":
    df = get_data()
    df_selection = select_features(df=df)
    dates = date(df_selection)
    competitions = competition(df_selection)
    final_scores = final_score(df_selection)
    prompt_df = pd.DataFrame(
        {
            "dates": dates,
            "competition": competitions,
            "final_score": final_scores,
        })
    prompt_df.to_csv("./openai_GPT3/train_data/train.csv")
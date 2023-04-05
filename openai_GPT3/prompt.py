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
    home_versus_away = home_vs_away(df_selection)
    venue_names = venue(df_selection)
    competition_names = competition(df_selection)
    final_scores = final_score(df_selection)
    goals = goal_events(df_selection)
    cards = card_events(df_selection)
    prompt_df = pd.DataFrame(
        {
            "dates": dates,
            "home_vs_away": home_versus_away,
            "venue": venue_names,
            "competition": competition_names,
            "final_score": final_scores,
            "goal_events": goals,
            "card_events": cards,
        }
    )
    # Flatten list of goal and card events per match.
    prompt_df['goal_events'] = [', '.join(map(str, l)) for l in prompt_df['goal_events']]
    prompt_df['card_events'] = [', '.join(map(str, l)) for l in prompt_df['card_events']] 
    prompt_df.to_csv("./openai_GPT3/train_data/train.csv")

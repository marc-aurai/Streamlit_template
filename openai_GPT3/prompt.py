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
    possession,
    trainer,
    keeper,
)


training_name = "training_2"


def get_data() -> pd.DataFrame:
    return pd.read_csv("./opta/data/merged/merged_ereD.csv", sep=";").dropna()


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
            "homeContestantId",
            "awayContestantId",
            "trainer_home",
            "trainer_away",
            "keeper_home",
            "keeper_away",
            "type_article",
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
    completion = article_completion(df_selection)
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
            "completion": completion,
            "type_article": df_selection.type_article.to_list()
        }
    )
    # Flatten list of goal and card events per match.
    prompt_df["goal_events"] = [
        ", ".join(map(str, l)) for l in prompt_df["goal_events"]
    ]
    prompt_df["card_events"] = [
        ", ".join(map(str, l)) for l in prompt_df["card_events"]
    ]
    prompt_df.to_csv(
        "./openai_GPT3/train_data/{}/train.csv".format(training_name),
        line_terminator="\n",
        sep=";",
    ) # Original dataframe

    openai_df = pd.DataFrame()
    openai_df["prompt"] = (
        prompt_df.type_article
        + "\n"
        + prompt_df.dates
        + " "
        + prompt_df.home_vs_away
        + " "
        + prompt_df.venue
        + ".\n"
        + prompt_df.competition
        + ".\n"
        + prompt_df.final_score
        + ".\n"
        + prompt_df.goal_events
        + ".\n"
        + prompt_df.card_events
        + ".\n"
        + prompt_df.possession
        + ".\n"
        + prompt_df.trainers
        + ".\n"
        + prompt_df.keepers
        + ".\n\n###\n\n"  # stop sequence, tip from openAI
    )
    openai_df["completion"] = (
        " " + prompt_df["completion"]
    )  # start your completion with a space, tip from openai
    openai_df.to_csv(
        "./openai_GPT3/train_data/{}/openai_train.csv".format(training_name),
        line_terminator="\n",
    )

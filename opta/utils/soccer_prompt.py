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
            "matchLength",
            "sum_matchLength_home",
            "sum_matchLength_away",
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
            "homeContestantName",
            "awayContestantName",
            "homeContestantCode",
            "awayContestantCode",
            "last_six_home",
            "last_six_away",
            "rank_home",
            "rank_away",
            "rank_status_home",
            "rank_status_away",
            "lastRank_home",
            "lastRank_away",
            "home_injuries",
            "away_injuries",
            "formation_home",
            "formation_away",
            "player_stats_home",
            "player_stats_away",
            "MatchStatsHome",
            "MatchStatsAway",
            "SchotenOpDoel_Home",
            "SchotenOpDoel_Away",
            "substitutions_home",
            "substitutions_away",
            "goalMakers",
            "cardsHistoryRed",
            "cardsHistoryYellow",
            "GoalCounter",
            "AssistCounter",
            "minsPlayedCounter",
            "penaltyHome",
            "penaltyAway",
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
            "lastRank_home",
            "lastRank_away",
            "home_injuries",
            "away_injuries",
            "formation_home",
            "formation_away",
            "substitutions_home",
            "substitutions_away",
            "score_home",
            "score_away",
            "goalMakers",
            "cardsHistoryRed",
            "cardsHistoryYellow",
            "homeContestantId",
            "awayContestantId",
            "homeContestantCode",
            "awayContestantCode",
        ]
    ].copy()
    openai_df["home_team"] = df_selection["homeContestantName"]
    openai_df["away_team"] = df_selection["awayContestantName"]
    openai_df["trainers"] = prompt_df["trainers"]
    openai_df["keepers"] = prompt_df["keepers"]
    openai_df["match"] = (
        df_selection["homeContestantName"]
        + " vs "
        + df_selection["awayContestantName"]
    )

    openai_df["_date_match_venue"] = prompt_df.dates + " " + prompt_df.home_vs_away + " " + prompt_df.venue
    openai_df["_competition"] = prompt_df.competition
    openai_df["_goalEvents"] = prompt_df.goal_events
    openai_df["_goalEventsOrginal"] = df_selection.goal_events
    openai_df["_cardEvents"] = prompt_df.card_events
    openai_df["_possession"] = prompt_df.possession
    openai_df["_rankStatus_home"] = prompt_df.rank_status_home
    openai_df["_rankStatus_away"] = prompt_df.rank_status_away

    player_stats = pd.DataFrame()
    player_stats = df_selection[
        [
            "date",
            "matchLength",
            "sum_matchLength_home",
            "sum_matchLength_away",
            "homeContestantId",
            "awayContestantId",
            "player_stats_home",
            "player_stats_away",
            "substitutions_home",
            "substitutions_away",
            "MatchStatsHome", 
            "MatchStatsAway",
            "SchotenOpDoel_Home",
            "SchotenOpDoel_Away",
            "GoalCounter",
            "AssistCounter",
            "minsPlayedCounter",
            "penaltyHome",
            "penaltyAway",
        ]
    ].copy()
    player_stats["match"] = openai_df["match"]

    openai_df["prompt"] = (
        "Geef het artikel een lijst met 4 pakkende titels en schrijf een voetbal wedstrijd artikel inclusief paragrafen.\n"
        # + "De eerste keer dat iemand genoemd wordt dient de voornaam en achternaam gebruikt te worden.\n" 
        # + "Wanneer een persoon voor de tweede keer benoemd wordt dient alleen de achternaam gebruikt te worden.\n"
        + "Gebruik de volgende informatie:\n"
        + prompt_df.final_score.values
        + ".\n"
    )
    
    return openai_df, player_stats

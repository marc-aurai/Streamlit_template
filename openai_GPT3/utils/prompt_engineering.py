import pandas as pd
from datetime import datetime as dt
import locale
import calendar
import ast


locale.setlocale(category=locale.LC_ALL, locale="nl_NL")


def date(df: pd.DataFrame) -> list:
    """Returns the date in a natural sentence with input format: 2023-03-19Z. As output: Op zaterdag 19 maart

    Args:
        df (pd.DataFrame): The merged dataset from ESPN and OPTA. 

    Returns:
        list: list of all converted dates from the input dataframe column ['date'].
    """
    dates = df["date"].tolist()
    dates = [dt.strptime(date, "%Y-%m-%dZ").date() for date in dates]
    dates = [
        "Op "+str(calendar.day_name[date.weekday()])+" "
        +str(date.day)+" "+str(date.strftime("%B"))
        for date in dates
    ]
    return dates


def home_vs_away(df: pd.DataFrame) -> list:
    """Returns the team names in a natural sentence who played the match with input format: 
    team name home + team name away. As output: speelde FC Twente thuis tegen AZ

    Args:
        df (pd.DataFrame): The merged dataset from ESPN and OPTA. 

    Returns:
        list: list of all converted team names from the input dataframe column ['home_team'] + ['away_team'].
    """
    home_versus_away = [
        "speelde " + str(home) + " thuis tegen " + str(away)
        for home, away in zip(df["home_team"].to_list(), df["away_team"].to_list())
    ]
    return home_versus_away


def venue(df: pd.DataFrame) -> list:
    """Returns the venue name in a natural sentence where the match was played with input format: 
    ['venue']. As output: in De Grolsch Veste

    Args:
        df (pd.DataFrame): The merged dataset from ESPN and OPTA. 

    Returns:
        list: list of all converted venue names from the input dataframe column ['venue'].
    """
    venue_names = [
        "in "+str(venue)
        for venue in df["venue"].to_list()
    ]    
    return venue_names


def competition(df: pd.DataFrame) -> list:
    """Returns the competition name in a natural sentence where the match was played with input format: 
    ['cup']. As output: De wedstrijd werd gespeeld in de 2022-23 Eredivisie, Regulier seizoen competitie.

    Args:
        df (pd.DataFrame): The merged dataset from ESPN and OPTA. 

    Returns:
        list: list of all converted competition names from the input dataframe column ['cup'].
    """
    competition_names = [
        "De wedstrijd werd gespeeld in de "+str(competition)+" competitie"
        for competition in df.cup.to_list()
    ]
    return competition_names


def final_score(df: pd.DataFrame) -> list:
    """Returns the final score from the match in a natural sentence with input format: 
    ['score_home'] + ['score_away'] + ['home_team'] + ['away_team']. 
    As output: FC Twente wint thuis met 2-1 van AZ.

    Args:
        df (pd.DataFrame): The merged dataset from ESPN and OPTA. 

    Returns:
        list: list of all converted final scores from the input dataframe columns 
        ['score_home'] + ['score_away'] + ['home_team'] + ['away_team']. 
    """
    final_score = [
        home_team+" wint thuis met "+str(home_score)+"-"+str(away_score)+" van "+away_team
        if home_score > away_score
        else away_team+" wint uit met "+str(home_score)+"-"+str(away_score)+" van "+home_team
        if home_score < away_score
        else home_team+" en "+away_team+" hebben gelijk gespeeld met "+str(home_score)+"-"+str(away_score)
        for home_score, away_score, home_team, away_team in zip(
            df["score_home"].to_list(),
            df["score_away"].to_list(),
            df["home_team"].to_list(),
            df["away_team"].tolist(),
        )
    ]
    return final_score


def goal_events(df: pd.DataFrame) -> list:
    """Returns the goal events from the match in a natural sentence with input format: 
    ['goal_events'] + ['homeContestantId'] + ['awayContestantId'] + ['home_team'] + ['away_team']. 
    As output: M. Ugalde scoorde voor Twente in de 1e helft in minuut 8, ....

    Args:
        df (pd.DataFrame): The merged dataset from ESPN and OPTA. 

    Returns:
        list: list of all converted goal events from the input dataframe columns 
        ['goal_events'] + ['homeContestantId'] + ['awayContestantId'] + ['home_team'] + ['away_team']. 
    """
    all_goals = []
    for all_matches_all_goals, home_id, away_id, home_team, away_team in zip(
        df['goal_events'].tolist(), 
        df['homeContestantId'].tolist(),
        df['awayContestantId'].tolist(),
        df['home_team'].tolist(), 
        df['away_team'].tolist(),
    ):
        goals_in_match = []
        for goals in ast.literal_eval(all_matches_all_goals):
            if goals['goalType'] == "G":
                goals_in_match.append(str(goals['scorerName'])+" scoorde voor "+
                                    str(goals["contestantName"])+" in de "+
                                    str(goals["periodId"])+"e helft in minuut "+
                                    str(goals["timeMin"]))
            if goals['goalType'] == "PG":
                goals_in_match.append(str(goals['scorerName'])+" scoorde een strafschop voor "+
                                    str(goals["contestantName"])+" in de "+
                                    str(goals["periodId"])+"e helft in minuut "+
                                    str(goals["timeMin"]))
            if goals['goalType'] == "OG":
                # Decide which team made a goal, caused by a OWN goal
                if goals['contestantId'] == home_id:
                    free_goal_for_team = away_team
                if goals['contestantId'] == away_id:
                    free_goal_for_team = home_team
                goals_in_match.append(str(goals['scorerName'])+" scoorde een eigen doelpunt voor "+
                                    str(free_goal_for_team)+" in de "+
                                    str(goals["periodId"])+"e helft in minuut "+
                                    str(goals["timeMin"]))
        all_goals.append(goals_in_match) if goals_in_match else all_goals.append(["Beide partijen wisten niet te scoren"])
    return all_goals


def card_events(df: pd.DataFrame) -> list:
    """Returns the card events from the match in a natural sentence with input format: 
    ['card_events']. 
    As output: Julio Pleguezuelo van Twente kreeg in de 2e helft in minuut 61 een gele kaart, ....

    Args:
        df (pd.DataFrame): The merged dataset from ESPN and OPTA. 

    Returns:
        list: list of all converted card events from the input dataframe columns 
        ['card_events'].
    """
    all_cards = []
    for all_matches_all_cards in df['card_events'].tolist():
        cards_in_match = []
        for cards in ast.literal_eval(all_matches_all_cards):
            kaart_type = "rode kaart" if cards['cardType'] == "RC" or cards['cardType'] == "Y2C" else "gele kaart"
            cards_in_match.append(str(cards['playerName'])+" van "+
                                  str(cards["contestantName"])+" kreeg in de "+
                                  str(cards["periodId"])+"e helft in minuut "+
                                  str(cards["timeMin"])+" een "+
                                  str(kaart_type))
        all_cards.append(cards_in_match) if cards_in_match else all_cards.append(["Beide partijen hebben geen kaarten gekregen van de scheidsrechter"])
    return all_cards


def possession(df: pd.DataFrame) -> list:
    """Returns the possession from both teams in a natural sentence with input format: 
    ['possession_home'] + ['possession_away'] + ['home_team'] + ['away_team']. 
    As output: FC Twente had meer balbezit dan AZ.

    Args:
        df (pd.DataFrame): The merged dataset from ESPN and OPTA. 

    Returns:
        list: list of all converted possession stats from the input dataframe columns 
        ['possession_home'] + ['possession_away'] + ['home_team'] + ['away_team'].
    """
    possessions = [
        home_team + " had meer balbezit dan " + away_team + " met " + str(possession_home) + " balbezit"
        if float(possession_home.strip("%")) > float(possession_away.strip("%")) 
        else away_team + " had meer balbezit dan " + home_team + " met " + str(possession_away) + " balbezit"
        if float(possession_home.strip("%")) < float(possession_away.strip("%")) 
        else " beide partijen hadden evenveel balbezit"
        for possession_home, possession_away, home_team, away_team in zip(
            df['possession_home'].to_list(), 
            df['possession_away'].to_list(), 
            df["home_team"].to_list(),
            df["away_team"].tolist()
        )
    ]
    return possessions


def trainer(df: pd.DataFrame) -> list:
    """Returns the trainers from both teams in a natural sentence with input format: 
    ['trainer_home'] + ['trainer_away'] + ['home_team'] + ['away_team']. 
    As output: <trainer_home> is de trainer van. <trainer_away> is de trainer van

    Args:
        df (pd.DataFrame): The merged dataset from ESPN and OPTA. 

    Returns:
        list: list of all converted trainers from the input dataframe columns 
        ['trainer_home'] + ['trainer_away'] + ['home_team'] + ['away_team']. 
    """
    trainers = [
        trainer_home + " is de trainer van " + home_team + ". " + 
        trainer_away + " is de trainer van " + away_team
        for trainer_home, trainer_away, home_team, away_team in zip(
            df['trainer_home'].to_list(), 
            df['trainer_away'].to_list(), 
            df["home_team"].to_list(),
            df["away_team"].tolist()
        )
    ]
    return trainers


def keeper(df: pd.DataFrame) -> list:
    """Returns the keepers from both teams in a natural sentence with input format: 
    ['keeper_home'] + ['keeper_away'] + ['home_team'] + ['away_team']. 
    As output: <keeper_home> is de keeper van. <keeper_away> is de keeper van

    Args:
        df (pd.DataFrame): The merged dataset from ESPN and OPTA. 

    Returns:
        list: list of all converted keepers from the input dataframe columns 
        ['keeper_home'] + ['keeper_away'] + ['home_team'] + ['away_team']. 
    """
    keepers = [
        keeper_home + " is de keeper van " + home_team + ". " + 
        keeper_away + " is de keeper van " + away_team
        for keeper_home, keeper_away, home_team, away_team in zip(
            df['keeper_home'].to_list(), 
            df['keeper_away'].to_list(), 
            df["home_team"].to_list(),
            df["away_team"].tolist()
        )
    ]
    return keepers


# met article title
def article_completion(df: pd.DataFrame) -> list:
    """Returns the article title combined with the complete article.

    Args:
        df (pd.DataFrame): The merged dataset from ESPN and OPTA. 

    Returns:
        list: list of all combined article titles + articles from the input dataframe columns 
        ['article_title'] + ['article']. 
    """
    completion = [article_title + "\n\n" + article
        for article_title, article in zip(
            df['article_title'].to_list(),
            df['article'].to_list(),
            )
    ]
    return completion

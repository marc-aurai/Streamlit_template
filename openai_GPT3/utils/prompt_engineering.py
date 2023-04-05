import pandas as pd
from datetime import datetime as dt
import locale
import calendar
import ast


locale.setlocale(category=locale.LC_ALL, locale="nl_NL")


def date(df: pd.DataFrame) -> list:
    dates = df["date"].tolist()
    dates = [dt.strptime(date, "%Y-%m-%dZ").date() for date in dates]
    dates = [
        "Op "+str(calendar.day_name[date.weekday()])+" "
        +str(date.day)+" "+str(date.strftime("%B"))
        for date in dates
    ]
    return dates


def home_vs_away(df: pd.DataFrame) -> list:
    home_versus_away = [
        "speelde " + str(home) + " thuis tegen " + str(away)
        for home, away in zip(df["home_team"].to_list(), df["away_team"].to_list())
    ]
    return home_versus_away


def venue(df: pd.DataFrame) -> list:
    venue_names = [
        "in "+str(venue)
        for venue in df["venue"].to_list()
    ]    
    return venue_names


def competition(df: pd.DataFrame) -> list:
    competition_names = [
        "De wedstrijd werd gespeeld in de "+str(competition)+" competitie"
        for competition in df.cup.to_list()
    ]
    return competition_names


def final_score(df: pd.DataFrame) -> list:
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
    all_goals = []
    for all_matches_all_goals in df['goal_events'].tolist():
        goals_in_match = []
        for goals in ast.literal_eval(all_matches_all_goals):
            goals_in_match.append(str(goals['scorerName'])+" scoorde voor "+
                                  str(goals["contestantName"])+" in de "+
                                  str(goals["periodId"])+"e helft in minuut "+
                                  str(goals["timeMin"]))
        all_goals.append(goals_in_match) if goals_in_match else all_goals.append(["Beide partijen wisten niet te scoren"])
    return all_goals


def card_events(df: pd.DataFrame) -> list:
    all_cards = []
    for all_matches_all_cards in df['card_events'].tolist():
        cards_in_match = []
        for cards in ast.literal_eval(all_matches_all_cards):
            kaart_type = "rode kaart" if cards['cardType'] == "RC" else "gele kaart"
            cards_in_match.append(str(cards['playerName'])+" van "+
                                  str(cards["contestantName"])+" kreeg in de "+
                                  str(cards["periodId"])+"e helft in minuut "+
                                  str(cards["timeMin"])+" een "+
                                  str(kaart_type))
        all_cards.append(cards_in_match) if cards_in_match else all_cards.append(["Beide partijen hebben geen kaarten gekregen van de scheidsrechter"])
    return all_cards


# met article title
def article_completion(df: pd.DataFrame) -> list:
    completion = [article_title + "\n\n" + article
        for article_title, article in zip(
            df['article_title'].to_list(),
            df['article'].to_list(),
            )
    ]
    return completion

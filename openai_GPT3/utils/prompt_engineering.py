import pandas as pd
from datetime import datetime as dt
import locale
import calendar

locale.setlocale(category=locale.LC_ALL, locale="nl_NL")


def date(df: pd.DataFrame) -> list:
    dates = df["date"].tolist()
    dates = [dt.strptime(date, "%Y-%m-%dZ").date() for date in dates]
    dates = [
        {
            "weekday": calendar.day_name[date.weekday()],
            "day_number": date.day,
            "month_name": date.strftime("%B"),
        }
        for date in dates
    ]
    print(dates)
    return dates


def competition(df: pd.DataFrame) -> list:
    return df.cup.tolist()


def final_score(df: pd.DataFrame) -> list:
    final_score = [
        [home_team+" wint thuis met "+str(home_score)+"-"+str(away_score)+" van "+away_team]
        if home_score > away_score
        else [away_team+" wint uit met "+str(home_score)+"-"+str(away_score)+" van "+home_team]
        if home_score < away_score
        else [home_team+" en "+away_team+" hebben gelijk gespeeld met "+str(home_score)+"-"+str(away_score)]
        for home_score, away_score, home_team, away_team in zip(
            df["score_home"].to_list(),
            df["score_away"].to_list(),
            df["home_team"].to_list(),
            df["away_team"].tolist(),
        )
    ]
    return final_score


def home_vs_away():
    pass


def venue():
    pass


def card_events():
    pass


def goal_events():
    pass


# met article title
def article_completion():
    pass

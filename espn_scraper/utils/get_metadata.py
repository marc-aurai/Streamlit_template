import datetime as dt
import math
from itertools import repeat

import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By

score_home_lst, score_away_lst, cup, titles, article, away, home, home_abbrev_lst, away_abbrev_lst, dates, espn_ids = map(
    lambda x: list(x), repeat([], 11)
)


def get_game_details(driver) -> str:
    try:
        game_details = driver.find_element(
            By.XPATH, '//*[@id="gamepackage-matchup-wrap--soccer"]/div[1]'
        ).text
    except:
        game_details = ""
    return game_details


def get_title(driver) -> str:
    try:
        title = driver.find_element(
            By.XPATH, '//*[@id="article-feed"]/div/article/div/header/h1'
        ).text
    except:
        title = ""
    return title


def get_teams(driver) -> str:
    try:
        team_home = driver.find_element(
            By.XPATH,
            '//*[@id="gamepackage-matchup-wrap--soccer"]/div[2]/div[1]/div/div[2]/div[1]/div/a/span[2]',
        ).text  # away en home are wrong on espn
        team_away = driver.find_element(
            By.XPATH,
            '//*[@id="gamepackage-matchup-wrap--soccer"]/div[2]/div[3]/div/div[3]/div[2]/div/a/span[2]',
        ).text  # away en home are wrong on espn

        home_abbrev = driver.find_element(
            By.XPATH,
            '//*[@id="gamepackage-matchup-wrap--soccer"]/div[2]/div[1]/div/div[2]/div[1]/div/a/span[3]',
        ).get_attribute('textContent')
        away_abbrev = driver.find_element(
            By.XPATH,
            '//*[@id="gamepackage-matchup-wrap--soccer"]/div[2]/div[3]/div/div[3]/div[2]/div/a/span[3]',
        ).get_attribute('textContent')
    except:
        team_away = ""
        team_home = ""
        home_abbrev = ""
        away_abbrev = ""
    return team_home, team_away, home_abbrev, away_abbrev


def get_score(driver):
    try:
        score_home = driver.find_element(
            By.XPATH,
            '//*[@id="gamepackage-matchup-wrap--soccer"]/div[2]/div[1]/div/div[3]/span',
        ).text
        score_away = driver.find_element(
            By.XPATH,
            '//*[@id="gamepackage-matchup-wrap--soccer"]/div[2]/div[3]/div/div[1]/span',
        ).text
    except:
        score_home = ""
        score_away = ""
    return float(score_home or math.nan), float(score_away or math.nan)


def get_content(driver) -> str:
    try:
        content = driver.find_element(
            By.XPATH, '//*[@id="article-feed"]/div/article/div/div[2]'
        )
        code = content.get_attribute("innerHTML")
        html = bs(code, "html.parser")

        article_paragraphs = []
        for paragraph in html.find_all("p"):
            article_paragraphs.append(str(paragraph.get_text()) + "\n\n")
        text = html.text

        split = text.split(
            "FacebookTwitterFacebook MessengerPinterestEmail"
        )  # Splitting on this long string containing info we do not need
        date = dt.datetime.strftime(
            dt.datetime.strptime(str(split[0]), "%d %b %Y").date(), "%Y-%m-%dZ"
        )
        article = " ".join(article_paragraphs)
        article = article[::-1].replace("\n\n"[::-1], "\n\n###\n\n"[::-1], 1)[
            ::-1
        ]  # Separator at the end of the prompt
    except:
        date = ""
        article = ""
    return date, article


def create_dataframe(
    espn_ids: list,
    score_home_lst: list,
    score_away_lst: list,
    cup: list,
    titles: list,
    dates: list,
    article: list,
    home: list,
    away: list,
    home_abbreviations: list,
    away_abbreviations: list,
):
    df = pd.DataFrame(
        {
            "espn_id": espn_ids,
            "home_team": home,
            "away_team": away,
            "home_abbrev": home_abbreviations,
            "away_abbrev": away_abbreviations,
            "score_home": score_home_lst,
            "score_away": score_away_lst,
            "date": dates,
            "cup": cup,
            "article_title": titles,
            "article": article,
        }
    )
    df = df.dropna()
    # df = df[df["article_title"].str.contains("EMPTY") == False]
    # df = df[df["article"].str.contains("EMPTY") == False]
    df["score_home"] = df["score_home"].astype(int)
    df["score_away"] = df["score_away"].astype(int)
    df.to_csv("./espn_scraper/scraper_data/articles_2428.csv", sep=";")


def format_data(
    espn_id,
    score_home,
    score_away,
    game_details,
    title,
    team_home,
    team_away,
    home_abbr,
    away_abbr,
    date,
    article_text,
) -> list:
    espn_ids.append(espn_id)
    score_home_lst.append(score_home)
    score_away_lst.append(score_away)
    cup.append(game_details)
    titles.append(title)
    dates.append(date)
    article.append(article_text)
    home.append(team_home)
    away.append(team_away)
    home_abbrev_lst.append(home_abbr)
    away_abbrev_lst.append(away_abbr)
    return (
        espn_ids,
        score_home_lst,
        score_away_lst,
        cup,
        titles,
        dates,
        article,
        home,
        away,
        home_abbrev_lst,
        away_abbrev_lst,
    )

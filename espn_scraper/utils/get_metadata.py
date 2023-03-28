import pandas as pd
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By


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
        team_away = driver.find_element(
            By.XPATH,
            '//*[@id="gamepackage-matchup-wrap--soccer"]/div[2]/div[1]/div/div[2]/div[1]/div/a/span[2]',
        ).text
        team_home = driver.find_element(
            By.XPATH,
            '//*[@id="gamepackage-matchup-wrap--soccer"]/div[2]/div[3]/div/div[3]/div[2]/div/a/span[2]',
        ).text
    except:
        team_away = ""
        team_home = ""
    return team_home, team_away


def get_content(driver) -> str:
    try:
        content = driver.find_element(
            By.XPATH, '//*[@id="article-feed"]/div/article/div/div[2]'
        )
        code = content.get_attribute("innerHTML")
        html = bs(code, "html.parser")
        text = html.text

        # Splitting on this long string containing info we do not need
        split = text.split("FacebookTwitterFacebook MessengerPinterestEmail")
        date = split[0]
        text = split[1]
    except:
        date = ""
        text = ""
    return date, text


def create_dataframe(
    date: list, cup: list, home: list, away: list, titles: list, text: list
):
    df = pd.DataFrame(
        {
            "date": date,
            "cup": cup,
            "home_team": home,
            "away_team": away,
            "article_title": titles,
            "article": text,
        }
    )
    df.to_csv("./espn_scraper/scraper_data/articles_.csv", sep=";")

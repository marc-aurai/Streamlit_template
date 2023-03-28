import requests
from selenium import webdriver
from utils.get_metadata import (
    create_dataframe,
    get_content,
    get_game_details,
    get_teams,
    get_title,
)

cup, titles, text, away, home, dates = ([],) * 6


def initialize():
    return webdriver.Chrome()


def format_data(game_details, title, team_home, team_away, date, article_text) -> list:
    cup.append(game_details)
    titles.append(title)
    dates.append(date)
    text.append(article_text)
    home.append(team_home)
    away.append(team_away)
    return cup, titles, dates, text, home, away


def scrape_espn(driver, start_id=637328, stop_id=637332):
    for i in range(start_id, stop_id):
        url = f"https://www.espn.nl/voetbal/verslag?wedstrijdId={i}"
        driver.get(url)
        game_details = get_game_details(driver)
        title = get_title(driver)
        team_home, team_away = get_teams(driver)
        date, text = get_content(driver)

        cup, titles, dates, text, home, away = format_data(
            game_details, title, team_home, team_away, date, text
        )

    create_dataframe(dates, cup, home, away, titles, text)


if __name__ == "__main__":
    driver = initialize()
    scrape_espn(driver=driver)

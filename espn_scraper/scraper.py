import requests
from selenium import webdriver
from tqdm import tqdm
from utils.get_metadata import (create_dataframe, format_data, get_content,
                                get_game_details, get_score, get_teams,
                                get_title)


def initialize():
    return webdriver.Chrome()


def scrape_espn(driver, start_id=637408, stop_id=637412):
    for i in tqdm(range(start_id, stop_id)):
        url = f"https://www.espn.nl/voetbal/verslag?wedstrijdId={i}"
        driver.get(url)
        score_home, score_away = get_score(driver)
        game_details = get_game_details(driver)
        title = get_title(driver)
        team_home, team_away, home_abbrev, away_abbrev = get_teams(driver)
        date, article = get_content(driver)

        (
            espn_ids,
            score_home_lst,
            score_away_lst,
            cup,
            titles,
            dates,
            articles,
            home,
            away,
            home_abbrev_lst,
            away_abbrev_lst,
        ) = format_data(
            i,
            score_home,
            score_away,
            game_details,
            title,
            team_home,
            team_away,
            home_abbrev,
            away_abbrev,
            date,
            article,
        )

    create_dataframe(
        espn_ids, score_home_lst, score_away_lst, cup, titles, dates, articles, home, away, home_abbrev_lst, away_abbrev_lst
    )


if __name__ == "__main__":
    driver = initialize()
    scrape_espn(driver=driver)

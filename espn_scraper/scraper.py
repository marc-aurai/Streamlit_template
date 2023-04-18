import requests
import json
from selenium import webdriver
from tqdm import tqdm
from utils.elements import (create_dataframe, format_data, get_content,
                                get_game_details, get_score, get_teams,
                                get_title)


def initialize():
    return webdriver.Chrome()

def get_ESPN_urls():
    eredivisie_ids = json.load(open("./ESPN_ids_data/content-objects-overig.json"))
    urls = []
    for publicatie in eredivisie_ids['contentObjects']:
        urls.append(publicatie['commonProperties']['publishEnvironments']['5']['publishedFullURL'])
    return urls


def scrape_espn(driver, urls):
    for i in tqdm(range(len(urls))):
        try:
            url = f"{urls[i]}"
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
                url.replace('https://www.espn.nl/voetbal/verslag?wedstrijdId=', ''),
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
        except:
            print("URL not found..")

    create_dataframe(
        espn_ids, score_home_lst, score_away_lst, cup, titles, dates, articles, home, away, home_abbrev_lst, away_abbrev_lst
    )


if __name__ == "__main__":
    driver = initialize()
    urls = get_ESPN_urls()
    scrape_espn(driver=driver, urls=urls)

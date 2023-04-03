# Get all Eredivisies ID's
import pandas as pd
import requests


def get_competetions() -> dict:
    competetions = requests.get(
        f"https://api.performfeeds.com/soccerdata/tournamentcalendar/6bxvue6su4ev1690mzy62a41t?_rt=b&_fmt=json"
    )
    return competetions.json()


def get_eredivisies(
    competitions: dict, which_competition="Eredivisie"
) -> tuple[pd.DataFrame, str]:
    eredivisie = [
        (competition)
        for competition in competitions["competition"]
        #if competition["name"] == which_competition
    ]
    eredivisie_season = [
        [season["id"], season["name"], season["startDate"], season["endDate"]]
        for season in eredivisie[0]["tournamentCalendar"]
    ]
    df_competetion = pd.DataFrame(eredivisie_season)
    df_competetion.columns = ["id", "name", "startDate", "endDate"]
    return df_competetion, which_competition


if __name__ == "__main__":
    competitions = get_competetions()
    df_competetion, which_competition = get_eredivisies(
        competitions=competitions, which_competition="Eredivisie"
    )
    df_competetion.to_csv("./opta/data/competitions/{}.csv".format("all_competitions"), sep=";")

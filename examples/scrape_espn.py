import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from time import sleep
import pandas as pd

# https://www.espn.nl/voetbal/wedstrijd?wedstrijdId=637428 = laatst beschikbare verslag op 27/03/2023

# For opening chrome web driver
driver = webdriver.Chrome()

#TODO Marc: toevoegen kolommen: goals away, goals home (uitslag?)
# Goals away en goals home bevatten dan (een lijst met) spelers die doelpunt hebben gemaakt die wedstrijd 


# creating containers for data 
df = pd.DataFrame()

cup = []
titles = []
all_text = []
away = []
home = []
all_dates = []

# looping through range of numbers, last in range corresponding to last id of verslag
for i in range(637328, 637428):

    url = f"https://www.espn.nl/voetbal/verslag?wedstrijdId={i}"
    driver.get(url)


    # Get game details and title of article 
    try:
        game_details = driver.find_element(By.XPATH, '//*[@id="gamepackage-matchup-wrap--soccer"]/div[1]').text
    except: 
        game_details = ""
        
    try:
        title = driver.find_element(By.XPATH,'//*[@id="article-feed"]/div/article/div/header/h1').text
    except:
        title = ""

    # Get match details (team and score)
    try: 
        team_away = driver.find_element(By.XPATH, '//*[@id="gamepackage-matchup-wrap--soccer"]/div[2]/div[1]/div/div[2]/div[1]/div/a/span[2]').text
        team_home = driver.find_element(By.XPATH, '//*[@id="gamepackage-matchup-wrap--soccer"]/div[2]/div[3]/div/div[3]/div[2]/div/a/span[2]').text
        
    except: 
        team_away = ""
        team_home = ""
    
    # Get content text and split from date
    try: 
        content = driver.find_element(By.XPATH, '//*[@id="article-feed"]/div/article/div/div[2]')
        code = content.get_attribute('innerHTML')
        html = bs(code, 'html.parser')
        text = html.text

        # Splitting on this long string containing info we do not need 
        split = text.split('FacebookTwitterFacebook MessengerPinterestEmail')
        date = split[0]
        text = split[1]

    except:
        date = ""
        text = ""
    
    # adding info to corresponding lists
    cup.append(game_details)
    titles.append(title)
    all_dates.append(date)
    all_text.append(text)
    home.append(team_home)
    away.append(team_away)

# adding lists to dataframe 
df['dates'] = all_dates
df['cup'] = cup
df['home'] = home
df['away'] = away
df['title'] = titles
df['articles'] = all_text

# writing to file
df.to_csv('100_articles_v2.csv', sep=';')
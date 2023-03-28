import requests
import pandas as pd 
import json


# # Tournament schedule API
# response = requests.get("https://api.performfeeds.com/soccerdata/tournamentschedule/6bxvue6su4ev1690mzy62a41t/d1k1pqdg2yvw8e8my74yvrdw4?_rt=b&_fmt=json")

# tournament_schedule = response.json()

# # Create df 
# data = pd.DataFrame.from_dict(tournament_schedule['matchDate'])

# # Normalize match data (contains basic information)
# matches = pd.json_normalize(data['match'])

# # Loop through df and get all match dicts
# all = []
# for item in data['match']:
#     all.append(item)

# # Unpack
# all = [x for y in data['match'] for x in y]
# df = pd.DataFrame(all)

# # Select small portion of dataframe (first 100 matches) for sample data 
# df_small = df[:100]

# # List for storing info 
# match_data = [] 

# # Get ID's for first 100 
# for id in df_small['id']:

# # API call for match stats     
#     response = requests.get(f"http://api.performfeeds.com/soccerdata/matchstats/6bxvue6su4ev1690mzy62a41t?_rt=b&_fmt=json&fx={id}")
#     matchstats = response.json()

#     match_data.append(matchstats)

# # Save data with extended info 
# with open(f"../data/matchstats/comb_matchstats.json", "w") as fp:
#     json.dump(match_data,fp) 


# API call for squat information (players in team)  
response = requests.get(f'http://api.performfeeds.com/soccerdata/squads/6bxvue6su4ev1690mzy62a41t?_rt=b&_fmt=json&tmcl=d1k1pqdg2yvw8e8my74yvrdw4')
squat_info = response.json()

with open(f"./squat_info.json", "w") as fp:
    json.dump(squat_info,fp) 
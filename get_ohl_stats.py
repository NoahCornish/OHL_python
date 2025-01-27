import pandas as pd
import requests
import os
from datetime import datetime

def fetch_json_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# URL
url_reg = "https://lscluster.hockeytech.com/feed/?feed=modulekit&view=statviewtype&type=topscorers&key=2976319eb44abe94&fmt=json&client_code=ohl&lang=en&league_code=&season_id=79&first=0&limit=50000&sort=active&stat=all&order_direction="

# Fetch and process data
json_data = fetch_json_data(url_reg)

# Process player stats data
df = pd.DataFrame(json_data['SiteKit']['Statviewtype'])
df = df.drop(columns=['birthtown', 'birthprov', 'birthcntry', 'loose_ball_recoveries', 'caused_turnovers', 
                      'turnovers', 'phonetic_name', 'last_years_club', 'suspension_games_remaining', 
                      'suspension_indefinite'], errors='ignore')

numeric_columns = ['player_id', 'active', 'age', 'rookie', 'jersey_number', 'team_id', 'games_played', 
                   'goals', 'assists', 'points', 'points_per_game', 'plus_minus', 'power_play_goals', 
                   'power_play_assists', 'game_winning_goals', 'empty_net_goals', 'penalty_minutes', 
                   'shots_on', 'faceoff_pct', 'num_teams']

df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

df['birthdate_year'] = df['birthdate_year'].str.split("'").str[1].astype(float) + 2000

df['birthdate'] = pd.to_datetime(df['birthdate'], errors='coerce', format='%B %d %Y')

LeagueStats_2024 = df[df['active'] == 1][[
    'name', 'rookie', 'jersey_number', 'birthdate', 'birthdate_year', 'height', 'weight', 'position', 
    'team_name', 'games_played', 'goals', 'assists', 'points', 'points_per_game', 'plus_minus', 
    'power_play_goals', 'power_play_assists', 'game_winning_goals', 'empty_net_goals', 'penalty_minutes'
]]

LeagueStats_2024.columns = [
    'Name', 'Rookie', 'JN', 'BD', 'BD_Y', 'Hgt', 'Wgt', 'Pos', 'Team', 'GP', 'G', 'A', 'PTS', 'Pts/G', 
    '+/-', 'PPG', 'PPA', 'GWG', 'ENG', 'PIM'
]

LeagueStats_2024 = LeagueStats_2024[LeagueStats_2024['Pos'] != 'G']
LeagueStats_2024['PPP'] = LeagueStats_2024['PPG'] + LeagueStats_2024['PPA']
LeagueStats_2024['PPP_Percentage'] = (LeagueStats_2024['PPP'] / LeagueStats_2024['PTS']) * 100
LeagueStats_2024['PPP_Percentage'] = LeagueStats_2024['PPP_Percentage'].round(1)

LeagueStats_2024['Rookie'] = LeagueStats_2024['Rookie'].replace({1: 'YES', 0: 'NO'})
LeagueStats_2024['RNK'] = (2 * LeagueStats_2024['G']) + (1.5 * LeagueStats_2024['A']) + \
                          (1 * LeagueStats_2024['+/-']) - (1 * LeagueStats_2024['PIM'])

# Create an output directory for team-specific files
output_dir = "OHL_STATS"
os.makedirs(output_dir, exist_ok=True)

# Save the overall league stats as a CSV file
overall_file_path = os.path.join(output_dir, "LeagueStats_2024_2025.csv")
LeagueStats_2024.to_csv(overall_file_path, index=False)

# Save stats for each team in separate files
teams = LeagueStats_2024['Team'].unique()
for team in teams:
    team_df = LeagueStats_2024[LeagueStats_2024['Team'] == team]
    team_file_path = os.path.join(output_dir, f"{team.replace(' ', '_')}.csv")
    team_df.to_csv(team_file_path, index=False)

print(f"League stats and individual team stats saved in '{output_dir}' folder.")

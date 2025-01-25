import requests
import pandas as pd
from datetime import datetime

# Store season ID
season_id = 76

# OHL team IDs
ohl_teams = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 34]

# Create an empty list to store player data
output = []

# Iterate over each team ID
for team_id in ohl_teams:
    # Construct the URL
    url = f"https://lscluster.hockeytech.com/feed/?feed=modulekit&view=roster&key=2976319eb44abe94&fmt=json&client_code=ohl&lang=en&season_id={season_id}&team_id={team_id}&fmt=json"
    
    # Fetch data from the URL
    response = requests.get(url)
    json_data = response.json()
    
    # Extract player list and exclude the last item (coaches/managers)
    player_list = json_data.get("SiteKit", {}).get("Roster", [])[:-1]
    
    # Process each player in the roster
    for player in player_list:
        try:
            # Create a dictionary for each player
            player_bio = {
                "player_id": int(player.get("player_id", None)),
                "full_name": player.get("name", None),
                "last_name": player.get("last_name", None),
                "first_name": player.get("first_name", None),
                "pos": player.get("position", None),
                "shoots": player.get("shoots", None),
                "height": float(player.get("height", 0)) if player.get("height") else None,
                "weight": float(player.get("weight", 0)) if player.get("weight") else None,
                "birthdate": datetime.strptime(player.get("birthdate", "1900-01-01"), "%Y-%m-%d").date() if player.get("birthdate") else None,
                "latest_team_id": int(player.get("latest_team_id", None)) if player.get("latest_team_id") else None,
                "team_name": player.get("team_name", None),
                "division": player.get("division", None),
                "jersey_number": int(player.get("tp_jersey_number", None)) if player.get("tp_jersey_number") else None,
                "rookie": int(player.get("rookie", None)) if player.get("rookie") else None,
            }
            output.append(player_bio)
        except Exception as e:
            print(f"Error processing player data: {e}")

# Convert the list of player data to a Pandas DataFrame
output_df = pd.DataFrame(output).drop_duplicates()

# Save the DataFrame to a CSV file
output_df.to_csv("rosters_updated.csv", index=False)

print("Roster data has been saved to rosters_updated.csv.")

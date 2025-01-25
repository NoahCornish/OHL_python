# Created by Noah Cornish
# Last Edits - January 25th, 2025

import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import sys

# Store season ID
season_id = 76

# OHL team IDs
ohl_teams = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 34]

# Create an empty list to store player data
output = []

# Total number of teams and sleep time per team
total_teams = len(ohl_teams)
total_duration = 30  # Total duration in seconds
sleep_time = total_duration / total_teams  # Sleep time between requests

# Calculate the estimated completion time
start_time = datetime.now()
end_time = start_time + timedelta(seconds=total_duration)

# Print start and estimated completion times
print(f"Script started at: {start_time.strftime('%H:%M:%S')}")
print(f"Estimated completion time: {end_time.strftime('%H:%M:%S')}\n")

# Function to print a progress bar
def print_progress_bar(current, total, bar_length=40):
    progress = current / total
    block = int(bar_length * progress)
    bar = "#" * block + "-" * (bar_length - block)
    sys.stdout.write(f"\r[{bar}] {current}/{total} teams completed")
    sys.stdout.flush()

# Iterate over each team ID
for index, team_id in enumerate(ohl_teams, start=1):
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
            # Extract height and ensure proper formatting
            raw_height = player.get("height", None)
            formatted_height = None
            if raw_height:
                # Preserve original formatting as string (e.g., "6.00", "5.10")
                formatted_height = raw_height if "." in raw_height else f"{raw_height}.00"

            # Create a dictionary for each player
            player_bio = {
                "player_id": int(player.get("player_id", None)),
                "full_name": player.get("name", None),
                "last_name": player.get("last_name", None),
                "first_name": player.get("first_name", None),
                "pos": player.get("position", None),
                "shoots": player.get("shoots", None),
                "height": formatted_height,  # Keep as a properly formatted string
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
    
    # Update the progress bar
    print_progress_bar(index, total_teams)
    
    # Sleep for the calculated duration to ensure total run time is 30 seconds
    if index < total_teams:  # No need to sleep after the last team
        time.sleep(sleep_time)

# Convert the list of player data to a Pandas DataFrame
output_df = pd.DataFrame(output).drop_duplicates()

# Save the DataFrame to a CSV file
output_df.to_csv(f"OHL_ROSTERS_2024_2025.csv", index=False)

print("\n\nRoster data has been saved to the working directory.")
print(f"Script completed at: {datetime.now().strftime('%H:%M:%S')}")

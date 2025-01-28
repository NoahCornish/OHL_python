import pandas as pd
import os

# File paths
stats_file = "docs/OHL_STATS/LeagueStats_2024_2025.csv"
schedule_file = "OHL_Schedule_2024_2025.csv"

def load_data(stats_file, schedule_file):
    """Load player stats and schedule data."""
    if not os.path.exists(stats_file) or not os.path.exists(schedule_file):
        raise FileNotFoundError("One or both data files are missing.")

    stats_df = pd.read_csv(stats_file)
    schedule_df = pd.read_csv(schedule_file)

    return stats_df, schedule_df

def calculate_team_stats(stats_df):
    """Aggregate player stats to calculate team-level stats."""
    team_stats = stats_df.groupby('Team').agg({
        'G': 'sum',
        'A': 'sum',
        'PTS': 'sum',
        'Pts/G': 'mean',
        'PPG': 'sum',
        'PPA': 'sum',
        'PIM': 'sum',
        'RNK': 'mean'
    }).rename(columns={
        'G': 'total_goals',
        'A': 'total_assists',
        'PTS': 'total_points',
        'Pts/G': 'avg_points_per_game',
        'PPG': 'total_powerplay_goals',
        'PPA': 'total_powerplay_assists',
        'PIM': 'total_penalty_minutes',
        'RNK': 'avg_rank'
    })

    return team_stats

def calculate_team_records(schedule_df):
    """Calculate team records based on schedule data."""
    team_records = {}

    for _, row in schedule_df.iterrows():
        home_team = row['HomeTeam']
        away_team = row['AwayTeam']
        home_goals = row['HomeGoals']
        away_goals = row['AwayGoals']

        # Update home team record
        if home_team not in team_records:
            team_records[home_team] = {'wins': 0, 'losses': 0, 'total_games': 0}
        team_records[home_team]['total_games'] += 1
        if home_goals > away_goals:
            team_records[home_team]['wins'] += 1
        else:
            team_records[home_team]['losses'] += 1

        # Update away team record
        if away_team not in team_records:
            team_records[away_team] = {'wins': 0, 'losses': 0, 'total_games': 0}
        team_records[away_team]['total_games'] += 1
        if away_goals > home_goals:
            team_records[away_team]['wins'] += 1
        else:
            team_records[away_team]['losses'] += 1

    return team_records

def predict_game_winner(home_team, away_team, team_stats, team_records):
    """Predict the winner of a game based on team stats and records."""
    # Retrieve team stats
    home_stats = team_stats.loc[home_team]
    away_stats = team_stats.loc[away_team]

    # Retrieve team records
    home_record = team_records.get(home_team, {'wins': 0, 'losses': 0, 'total_games': 1})
    away_record = team_records.get(away_team, {'wins': 0, 'losses': 0, 'total_games': 1})

    # Calculate team strength
    home_strength = (
        home_stats['total_points'] + home_stats['avg_rank'] * 10 +
        (home_record['wins'] / home_record['total_games']) * 100
    )

    away_strength = (
        away_stats['total_points'] + away_stats['avg_rank'] * 10 +
        (away_record['wins'] / away_record['total_games']) * 100
    )

    # Calculate probabilities
    total_strength = home_strength + away_strength
    home_prob = home_strength / total_strength
    away_prob = away_strength / total_strength

    # Convert probabilities to American odds
    if home_prob > away_prob:
        home_odds = -int(100 / home_prob)
        away_odds = int(100 * ((1 - away_prob) / away_prob))
    else:
        away_odds = -int(100 / away_prob)
        home_odds = int(100 * ((1 - home_prob) / home_prob))

    # Ensure positive odds are prefixed with '+'
    home_odds = f"+{home_odds}" if home_odds > 0 else str(home_odds)
    away_odds = f"+{away_odds}" if away_odds > 0 else str(away_odds)

    # Predict winner
    winner = home_team if home_prob > away_prob else away_team

    return winner, home_odds, away_odds



def get_top_players(stats_df, team, top_n=3):
    """Get the top N players from a team based on points."""
    team_players = stats_df[stats_df['Team'] == team]
    top_players = team_players.nlargest(top_n, 'PTS')[['Name', 'Pos', 'PTS']]
    return top_players

def main():
    try:
        stats_df, schedule_df = load_data(stats_file, schedule_file)

        # Calculate team stats and records
        team_stats = calculate_team_stats(stats_df)
        team_records = calculate_team_records(schedule_df)

        # User selects a date for games
        selected_date = input("Enter a date to view games (YYYY-MM-DD): ").strip()
        games_on_date = schedule_df[schedule_df['Date'] == selected_date]

        if games_on_date.empty:
            print(f"No games found for {selected_date}.")
            return

        print("\nGames on selected date:")
        for idx, game in enumerate(games_on_date.itertuples(), start=1):
            print(f"{idx}: {game.HomeTeam} vs {game.AwayTeam}")

        # User selects a game
        selected_game_index = int(input("Select a game by number: ")) - 1
        if selected_game_index < 0 or selected_game_index >= len(games_on_date):
            print("Invalid selection. Please try again.")
            return

        selected_game = games_on_date.iloc[selected_game_index]

        home_team = selected_game['HomeTeam']
        away_team = selected_game['AwayTeam']

        # Predict game winner
        winner, home_odds, away_odds = predict_game_winner(home_team, away_team, team_stats, team_records)
        print(f"\nPrediction: {winner} is more likely to win.")
        print(f"Odds: {home_team}: {home_odds}, {away_team}: {away_odds}")

        # Show top players for each team
        print(f"\nTop players for {home_team}:")
        print(get_top_players(stats_df, home_team))

        print(f"\nTop players for {away_team}:")
        print(get_top_players(stats_df, away_team))

    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
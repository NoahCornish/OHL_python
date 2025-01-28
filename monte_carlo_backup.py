import pandas as pd
import os
import numpy as np  # Import numpy for Poisson distribution

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
    home_stats = team_stats.loc[home_team]
    away_stats = team_stats.loc[away_team]

    home_record = team_records.get(home_team, {'wins': 0, 'losses': 0, 'total_games': 1})
    away_record = team_records.get(away_team, {'wins': 0, 'losses': 0, 'total_games': 1})

    home_strength = (
        home_stats['total_points'] + home_stats['avg_rank'] * 10 +
        (home_record['wins'] / home_record['total_games']) * 100
    )
    away_strength = (
        away_stats['total_points'] + away_stats['avg_rank'] * 10 +
        (away_record['wins'] / away_record['total_games']) * 100
    )

    total_strength = home_strength + away_strength
    home_prob = home_strength / total_strength
    away_prob = away_strength / total_strength

    if home_prob > away_prob:
        home_odds = -int(100 / home_prob)
        away_odds = int(100 * ((1 - away_prob) / away_prob))
    else:
        away_odds = -int(100 / away_prob)
        home_odds = int(100 * ((1 - home_prob) / home_prob))

    home_odds = f"+{home_odds}" if home_odds > 0 else str(home_odds)
    away_odds = f"+{away_odds}" if away_odds > 0 else str(away_odds)

    winner = home_team if home_prob > away_prob else away_team

    return winner, home_odds, away_odds, home_prob, away_prob

def simulate_scores(home_prob, away_prob, num_simulations=1000000):
    """Simulate game scores based on probabilities."""
    score_simulations = []
    for _ in range(num_simulations):
        home_score = np.random.poisson(home_prob * 5)  # Scale probability for score prediction
        away_score = np.random.poisson(away_prob * 5)  # Scale probability for score prediction
        score_simulations.append((home_score, away_score))

    # Aggregate score counts
    score_counts = pd.DataFrame(score_simulations, columns=['HomeScore', 'AwayScore'])
    score_counts['Result'] = score_counts.apply(lambda x: 'HomeWin' if x['HomeScore'] > x['AwayScore']
                                                else 'AwayWin' if x['AwayScore'] > x['HomeScore']
                                                else 'Draw', axis=1)

    # Calculate shutout probabilities
    home_shutout_prob = len(score_counts[(score_counts['AwayScore'] == 0) & (score_counts['HomeScore'] > 0)]) / num_simulations * 100
    away_shutout_prob = len(score_counts[(score_counts['HomeScore'] == 0) & (score_counts['AwayScore'] > 0)]) / num_simulations * 100

    # Top scenarios for each team winning (sort by count)
    top_home_wins = (
        score_counts[score_counts['Result'] == 'HomeWin']
        .value_counts(['HomeScore', 'AwayScore'], sort=False)
        .reset_index(name='Count')
        .nlargest(5, 'Count', keep='all')
    )
    top_away_wins = (
        score_counts[score_counts['Result'] == 'AwayWin']
        .value_counts(['AwayScore', 'HomeScore'], sort=False)
        .reset_index(name='Count')
        .nlargest(5, 'Count', keep='all')
    )

    # Add probability
    total_simulations = len(score_simulations)
    top_home_wins['Probability'] = (top_home_wins['Count'] / total_simulations * 100).round(2)
    top_away_wins['Probability'] = (top_away_wins['Count'] / total_simulations * 100).round(2)

    return top_home_wins, top_away_wins, home_shutout_prob, away_shutout_prob

def fetch_games_and_run_simulations(selected_date, stats_df, schedule_df, team_stats, team_records):
    """Fetch games on a selected date and run simulations for each game."""
    games_on_date = schedule_df[schedule_df['Date'] == selected_date]
    if games_on_date.empty:
        print(f"No games found for {selected_date}.")
        return

    print("\nGames on selected date:")
    for index, game in games_on_date.iterrows():
        print(f"{index}: {game['HomeTeam']} vs {game['AwayTeam']}")

    # User selects a game
    selected_game_index = int(input("Select a game by index: "))
    selected_game = games_on_date.iloc[selected_game_index]

    home_team = selected_game['HomeTeam']
    away_team = selected_game['AwayTeam']

    winner, home_odds, away_odds, home_prob, away_prob = predict_game_winner(
        home_team, away_team, team_stats, team_records
    )

    print(f"\nDetailed Report for {home_team} vs {away_team}")
    print(f"Prediction: {winner} is more likely to win.")
    print(f"Odds: {home_team}: {home_odds}, {away_team}: {away_odds}")

    # Run simulations
    top_home_wins, top_away_wins, home_shutout_prob, away_shutout_prob = simulate_scores(home_prob, away_prob, num_simulations=1000000)

    print("\nMost Likely Scenarios for {home_team} Winning:")
    print(top_home_wins)

    print(f"\nMost Likely Scenarios for {away_team} Winning:")
    print(top_away_wins)

    print(f"\nShutout Probabilities:")
    print(f"{home_team} shuts out {away_team}: {home_shutout_prob:.2f}%")
    print(f"{away_team} shuts out {home_team}: {away_shutout_prob:.2f}%")

def main():
    try:
        stats_df, schedule_df = load_data(stats_file, schedule_file)
        team_stats = calculate_team_stats(stats_df)
        team_records = calculate_team_records(schedule_df)

        selected_date = input("Enter a date to view games (YYYY-MM-DD): ").strip()
        fetch_games_and_run_simulations(selected_date, stats_df, schedule_df, team_stats, team_records)

    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()

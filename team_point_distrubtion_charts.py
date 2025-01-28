import pandas as pd
import plotly.express as px

# Load the data
data_file = "LeagueStats_2024_2025.csv"
data = pd.read_csv(data_file)

# Function to filter players by team
def filter_by_team(team_name):
    return data[data['Team'] == team_name]

# Generate visualizations
# 1. Distribution of players across teams
team_distribution = data['Team'].value_counts().reset_index()
team_distribution.columns = ['Team', 'Number of Players']
fig1 = px.bar(team_distribution, x='Team', y='Number of Players', title='Number of Players per Team')
fig1.show()

# 2. Points distribution for a selected team
def plot_points_distribution(team_name):
    team_data = filter_by_team(team_name)
    fig2 = px.histogram(team_data, x='PTS', nbins=10, title=f'Points Distribution for {team_name}')
    fig2.show()

# 3. Top players by points for a selected team
def plot_top_players_by_points(team_name, top_n=10):
    team_data = filter_by_team(team_name).sort_values(by='PTS', ascending=False).head(top_n)
    fig3 = px.bar(team_data, x='Name', y='PTS', title=f'Top {top_n} Players by Points for {team_name}')
    fig3.show()

# Example usage
# Uncomment the lines below to test specific teams
plot_points_distribution("London Knights")
# plot_top_players_by_points("Ottawa 67's")

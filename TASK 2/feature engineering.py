import pandas as pd

df = pd.read_csv("FIFA_2022_Full_Matches_Cleaned.csv")

# Reshape dataset for analysis per team
home_df = df[['Home Team', 'Home Goals', 'Away Goals', 'Winner', 'Stage']].copy()
home_df.rename(columns={'Home Team': 'Team', 'Home Goals': 'Goals For', 'Away Goals': 'Goals Against'}, inplace=True)

away_df = df[['Away Team', 'Home Goals', 'Away Goals', 'Winner', 'Stage']].copy()
away_df.rename(columns={'Away Team': 'Team', 'Away Goals': 'Goals For', 'Home Goals': 'Goals Against'}, inplace=True)

teams_df = pd.concat([home_df, away_df])
teams_df['Win'] = teams_df['Winner'] == teams_df['Team']

# Aggregate performance per team
team_stats = teams_df.groupby('Team').agg({
    'Goals For':'sum',
    'Goals Against':'sum',
    'Win':'sum'
}).reset_index()

# Add finalist label
finalists = df[df['Stage'] == 'Final'][['Home Team', 'Away Team']].melt()['value'].unique()
team_stats['Finalist'] = team_stats['Team'].apply(lambda x: 1 if x in finalists else 0)

print(team_stats.head())

from sklearn.preprocessing import StandardScaler

X = team_stats[['Goals For', 'Goals Against', 'Win']]
y = team_stats['Finalist']

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

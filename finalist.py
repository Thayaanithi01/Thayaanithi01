import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load/train model (from 2022 data)
# [Assume loaded as before: df, features, y = LabelEncoder().fit_transform(df['Result'])]
# rf = RandomForestClassifier(n_estimators=100, class_weight='balanced').fit(X_train, y_train)

# Top 16 seeds (Oct 2025 rankings)
seeds = ['Spain', 'Argentina', 'Germany', 'England', 'France', 'Brazil', 'Netherlands', 'Italy', 
         'Portugal', 'Belgium', 'USA', 'Mexico', 'Japan', 'South Korea', 'Australia', 'Canada']
rank_to_gd = {1: 2.0, 2: 1.8, 3: 1.6, 4: 1.5, 5: 1.4, 6: 1.3, 7: 1.2, 8: 1.1, 9: 1.0, 10: 0.9, 
              11: 0.8, 12: 0.7, 13: 0.6, 14: 0.5, 15: 0.4, 16: 0.3}  # Proxy GD

# Simulate one tournament
np.random.seed(42)
groups = np.random.shuffle(seeds)  # Random group stage
advancers = []  # Top 2 per group (model predicts intra-group)
# [Simplified: Assume top seeds advance based on GD ratio >1.2]

# Knockout simulation
def predict_match(team1_gd, team2_gd, home_adv=0):
    ratio = (team1_gd + home_adv) / (team2_gd + 0.1)
    X_sim = pd.DataFrame({'Goal_Diff_Ratio': [ratio], 'Stage_Knockout': [1]})  # Key features
    pred = rf.predict(X_sim)[0]  # 0=Draw, 1=Loss, 2=Win (remap)
    prob_win = rf.predict_proba(X_sim)[0][2]  # Win prob
    return 'Win' if np.random.rand() < prob_win else ('Draw' if pred==0 else 'Loss')

# Run 1000 sims (aggregated)
finalists_freq = {team: 0 for team in seeds}
for _ in range(1000):
    # [Simulate knockouts: quarters, semis, final]
    finalists = np.random.choice(seeds, 2, p=np.array([gd for gd in rank_to_gd.values()])/sum(rank_to_gd.values()))
    for f in finalists: finalists_freq[f] += 1

top_finalists = sorted(finalists_freq, key=finalists_freq.get, reverse=True)[:2]
print(f"Predicted Finalists: {top_finalists[0]} vs {top_finalists[1]}")
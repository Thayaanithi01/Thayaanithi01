import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Load & merge data
matches = pd.read_csv("FIFA_2022_Full_Matches_Cleaned.csv")
teams = pd.read_excel("FIFA_2022_Team_Averages.xlsx")
matches.replace('Usa', 'USA', inplace=True)
teams.replace('Usa', 'USA', inplace=True)

df = matches.merge(teams, left_on='Home Team', right_on='Team', suffixes=('', '_home'))
df = df.merge(teams, left_on='Away Team', right_on='Team', suffixes=('_home', '_away'))

# Features
df['Home_Strength'] = df['Avg_Goals_Scored_home'] / (df['Avg_Goals_Conceded_away'] + 1)
df['Away_Strength'] = df['Avg_Goals_Scored_away'] / (df['Avg_Goals_Conceded_home'] + 1)
df['Goal_Diff_Ratio'] = df['Home_Strength'] / (df['Away_Strength'] + 0.1)
df['Stage_Knockout'] = df['Stage'].apply(lambda x: 1 if 'Group' not in x else 0)

features = ['Avg_Goals_Scored_home', 'Avg_Goals_Conceded_home', 'Avg_Goal_Difference_home',
            'Avg_Goals_Scored_away', 'Avg_Goals_Conceded_away', 'Avg_Goal_Difference_away',
            'Goal_Diff_Ratio', 'Stage_Knockout']
X = df[features]
y = LabelEncoder().fit_transform(df['Result'])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)

# Models
lr = LogisticRegression(multi_class='multinomial', max_iter=1000).fit(X_train, y_train)
rf = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42).fit(X_train, y_train)

# Logistic Regression: Mean abs coef
lr_importance = pd.Series(np.mean(np.abs(lr.coef_), axis=0), index=features).sort_values(ascending=False)

# Random Forest: Gini importance
rf_importance = pd.Series(rf.feature_importances_, index=features).sort_values(ascending=False)

# Plot
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

lr_importance.plot(kind='barh', ax=ax1, color='coral', title='Logistic Regression (Mean |Coef|)')
rf_importance.plot(kind='barh', ax=ax2, color='teal', title='Random Forest (Gini Importance)')

ax1.invert_yaxis(); ax2.invert_yaxis()
plt.tight_layout()
plt.savefig('feature_importance.png', dpi=300, bbox_inches='tight')
plt.show()

print("Top Feature (RF):", rf_importance.index[0])
print("Top Feature (LR):", lr_importance.index[0])
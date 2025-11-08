# fifa_app.py
# FIFA 2026 Predictor – Full Flask Application (Web UI + Backend)
# Run: python fifa_app.py
# Open: http://127.0.0.1:8000

import os
import pandas as pd
import numpy as np
import joblib
import subprocess
import time
import threading
from flask import Flask, render_template_string, request

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# -------------------------------------------------
# 1. Flask app + data folder
# -------------------------------------------------
app = Flask(__name__)
os.makedirs("data", exist_ok=True)

# -------------------------------------------------
# 2. 2026 qualified teams (28 – Nov 2025)
# -------------------------------------------------
QUALIFIED_TEAMS = [
    'USA','Canada','Mexico','Iran','South Korea','Australia','Uzbekistan','Jordan',
    'Iraq','Qatar','Saudi Arabia','Morocco','Egypt','Senegal','Algeria','Tunisia',
    'South Africa','Cape Verde','Gabon','Nigeria','Argentina','Brazil','Colombia',
    'Ecuador','Uruguay','Paraguay','New Zealand','England','Spain','Germany',
    'France','Italy','Jamaica','Panama','Costa Rica'
]
CONFED = ['Host']*3 + ['AFC']*8 + ['CAF']*9 + ['CONMEBOL']*6 + ['OFC']*1 + ['UEFA']*5 + ['CONCACAF']*3
pd.DataFrame({'Team':QUALIFIED_TEAMS,'Confederation':CONFED})\
  .to_csv("data/2026_qualifiers.csv", index=False)

# -------------------------------------------------
# 3. Load / create demo data
# -------------------------------------------------
def load_and_prepare():
    csv_path = "data/2022_matches.csv"
    xlsx_path = "data/2022_teams.xlsx"

    if os.path.exists(csv_path) and os.path.exists(xlsx_path):
        matches = pd.read_csv(csv_path)
        teams   = pd.read_excel(xlsx_path)
    else:
        np.random.seed(42)
        teams_list = ['Spain','Brazil','Germany','Argentina','France','England',
                      'Italy','Portugal','Netherlands','Belgium']
        matches = pd.DataFrame({
            'Home Team': np.random.choice(teams_list, 48),
            'Away Team': np.random.choice(teams_list, 48),
            'Result'   : np.random.choice(['Win','Draw','Loss'], 48),
            'Stage'    : np.random.choice(['Group A','Group B','Round of 16','Quarter-final'],48)
        })
        teams = pd.DataFrame({
            'Team'                : teams_list,
            'Avg_Goals_Scored'    : np.random.uniform(1.5,3.0,10),
            'Avg_Goals_Conceded'  : np.random.uniform(0.5,1.5,10),
            'Avg_Goal_Difference': np.random.uniform(0.5,2.0,10)
        })
        matches.to_csv(csv_path, index=False)
        teams.to_excel(xlsx_path, index=False)

    matches.replace('Usa','USA', inplace=True)
    teams.replace('Usa','USA', inplace=True)

    df = matches.merge(teams, left_on='Home Team', right_on='Team', suffixes=('','_home'))
    df = df.merge(teams, left_on='Away Team', right_on='Team', suffixes=('_home','_away'))

    df['Goal_Diff_Ratio'] = (df['Avg_Goals_Scored_home']/(df['Avg_Goals_Conceded_away']+1)) / \
                            (df['Avg_Goals_Scored_away']/(df['Avg_Goals_Conceded_home']+1)+0.1)
    df['Stage_Knockout'] = df['Stage'].apply(lambda x: 1 if 'Group' not in x else 0)

    features = ['Avg_Goals_Scored_home','Avg_Goals_Conceded_home','Avg_Goal_Difference_home',
                'Avg_Goals_Scored_away','Avg_Goals_Conceded_away','Avg_Goal_Difference_away',
                'Goal_Diff_Ratio','Stage_Knockout']
    X = df[features]
    le = LabelEncoder()
    y = le.fit_transform(df['Result'])
    return X, y, le, features

# -------------------------------------------------
# 4. Train / load model
# -------------------------------------------------
MODEL_PATH = "rf_model.pkl"
if os.path.exists(MODEL_PATH):
    model, le, features = joblib.load(MODEL_PATH)
else:
    X, y, le, features = load_and_prepare()
    X_train, _, y_train, _ = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
    model.fit(X_train, y_train)
    joblib.dump((model, le, features), MODEL_PATH)

# -------------------------------------------------
# 5. Simulation (fixed bug)
# -------------------------------------------------
def simulate_finalists(n_sims=1000):
    q = pd.read_csv("data/2026_qualifiers.csv")
    gd_map = {'Host':1.5,'AFC':1.0,'CAF':0.8,'CONMEBOL':1.8,'OFC':0.5,'UEFA':1.6,'CONCACAF':1.2}
    q['GD'] = q['Confederation'].map(gd_map)
    finalists = {t:0 for t in q['Team']}
    np.random.seed(42)

    for _ in range(n_sims):
        teams = q.sample(frac=1).copy()
        while len(teams) > 1:
            winners = []
            for i in range(0, len(teams), 2):
                if i + 1 >= len(teams):
                    winners.append(teams.iloc[i]['Team'])
                    break
                t1, t2 = teams.iloc[i], teams.iloc[i+1]
                ratio = (t1['GD']+0.2)/(t2['GD']+0.1)
                X_sim = pd.DataFrame({f:0 for f in features}, index=[0])
                X_sim['Goal_Diff_Ratio'] = ratio
                X_sim['Stage_Knockout'] = 1
                prob = model.predict_proba(X_sim)[0]
                win_idx = le.transform(['Win'])[0]
                win_prob = prob[win_idx]
                winner = t1['Team'] if np.random.rand() < win_prob else t2['Team']
                winners.append(winner)
            teams = pd.DataFrame({'Team':winners,
                                 'GD':[q[q['Team']==w]['GD'].iloc[0] for w in winners]})
        for f in teams['Team'].head(2):
            finalists[f] += 1

    # ---- FIXED PART ----
    top_pairs = sorted(finalists.items(), key=lambda x: x[1], reverse=True)[:5]
    probs = {team: round(cnt / n_sims * 100, 1) for team, cnt in top_pairs}
    final_match = f"{top_pairs[0][0]} vs {top_pairs[1][0]}"
    # --------------------
    return final_match, probs

# -------------------------------------------------
# 6. HTML UI (embedded)
# -------------------------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>FIFA 2026 Predictor</title>
  <style>
    body{font-family:Arial;background:#0f172a;color:#e2e8f0;text-align:center;padding:40px;}
    h1{color:#60a5fa;}
    button{margin:10px;padding:12px 24px;background:#1e40af;color:#fff;border:none;
           border-radius:8px;cursor:pointer;font-weight:bold;}
    button:hover{background:#1d4ed8;}
    .out{margin:20px;padding:20px;background:#1e293b;border-radius:12px;display:none;}
    .out.show{display:block;}
    .final{font-size:1.8em;color:#60a5fa;}
  </style>
</head>
<body>
  <h1>FIFA 2026 World Cup Predictor</h1>
  <p>28 Teams Qualified</p>
  <form method="POST">
    <button type="submit" name="action" value="summary">View Summary</button>
    <button type="submit" name="action" value="predict">Predict Finalists</button>
  </form>

  {% if summary %}
  <div class="out show">
    <h3>Dataset Summary</h3>
    <p>2022 Matches: <strong>{{ summary.matches }}</strong></p>
    <p>2022 Teams:   <strong>{{ summary.teams }}</strong></p>
    <p>2026 Qualified: <strong>{{ summary.qualified }}</strong></p>
  </div>
  {% endif %}

  {% if final %}
  <div class="out show">
    <h3>Final Prediction</h3>
    <p class="final">{{ final }}</p>
    <h4>Top 5 Contenders:</h4>
    <ul style="list-style:none;padding:0;">
      {% for t,p in probs.items() %}
      <li><strong>{{ t }}</strong>: {{ p }}%</li>
      {% endfor %}
    </ul>
  </div>
  {% endif %}
</body>
</html>
"""

# -------------------------------------------------
# 7. Routes
# -------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    summary = None
    final = None
    probs = {}

    if request.method == "POST":
        act = request.form.get("action")
        if act == "summary":
            matches = len(pd.read_csv("data/2022_matches.csv"))
            teams   = len(pd.read_excel("data/2022_teams.xlsx"))
            qual    = len(pd.read_csv("data/2026_qualifiers.csv"))
            summary = {"matches": matches, "teams": teams, "qualified": qual}
        elif act == "predict":
            final, probs = simulate_finalists()

    return render_template_string(HTML_TEMPLATE, summary=summary, final=final, probs=probs)

# -------------------------------------------------
# 8. Auto-open browser (Windows)
# -------------------------------------------------
def open_browser():
    time.sleep(1)
    subprocess.run(["start", "http://127.0.0.1:8000"], shell=True)

# -------------------------------------------------
# 9. Run
# -------------------------------------------------
if __name__ == "__main__":
    print("Starting FIFA 2026 Flask Application...")
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host="0.0.0.0", port=8000, debug=True)
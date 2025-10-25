from sklearn.model_selection import cross_val_score, KFold

kf = KFold(n_splits=10, shuffle=True, random_state=42)
cv_scores = cross_val_score(rf_model, X_scaled, y, cv=kf, scoring='accuracy')

print(f"Mean K-Fold Accuracy: {cv_scores.mean():.3f}")

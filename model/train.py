"""
Model training script v2 — Enhanced with:
- Cross-validation (5-fold)
- Hyperparameter tuning via RandomizedSearchCV
- Prediction intervals (quantile regression)
- Feature importance analysis
- Model comparison dashboard data
"""

import os
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression, Ridge, QuantileRegressor
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    GradientBoostingRegressor as GBRQuantile,
)
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from scipy.stats import randint, uniform
import joblib
import warnings
warnings.filterwarnings('ignore')

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'house_data.csv')
MODEL_DIR = os.path.join(BASE_DIR, 'model')
REPORT_DIR = os.path.join(BASE_DIR, 'reports')
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# ── 1. Load data ──────────────────────────────────────────────
print("=" * 60)
print("HomeValue AI Model Training Pipeline v2")
print("=" * 60)
print("\nLoading dataset...")
df = pd.read_csv(DATA_PATH)
print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"   Price range: {df['price'].min():,} – {df['price'].max():,}")
print(f"   Price median: {df['price'].median():,.0f}")

# ── 2. Encode categorical columns ────────────────────────────
print("\nEncoding categorical features...")
encoders = {}
categorical_cols = ['city', 'locality', 'property_type', 'furnishing']

for col in categorical_cols:
    le = LabelEncoder()
    df[col + '_encoded'] = le.fit_transform(df[col])
    encoders[col] = le
    print(f"   {col}: {len(le.classes_)} classes")

# ── 3. Feature engineering ────────────────────────────────────
print("\nEngineering features...")

# Derived features
df['price_per_sqft_base'] = df['area']  # will be used as-is
df['amenity_count'] = df[['parking', 'pool', 'garden', 'gym', 'security', 'lift',
                           'power_backup', 'modular_kitchen', 'clubhouse', 'children_play',
                           'jogging_track', 'sports_court', 'rainwater_harvesting',
                           'solar_panels', 'smart_home', 'servant_room']].sum(axis=1)
df['bed_bath_ratio'] = df['bedrooms'] / df['bathrooms'].clip(lower=1)
df['area_per_bedroom'] = df['area'] / df['bedrooms'].clip(lower=1)

feature_cols = [
    'city_encoded', 'locality_encoded', 'property_type_encoded',
    'area', 'bedrooms', 'bathrooms', 'furnishing_encoded',
    'age', 'floor',
    'parking', 'pool', 'garden', 'gym', 'security', 'lift',
    'power_backup', 'modular_kitchen', 'clubhouse', 'children_play',
    'jogging_track', 'sports_court', 'rainwater_harvesting',
    'solar_panels', 'smart_home', 'servant_room',
    'amenity_count', 'bed_bath_ratio', 'area_per_bedroom',
]

X = df[feature_cols]
y = df['price']
print(f"Data preprocessed: {X.shape[1]} features created.")
print(f"   New features: amenity_count, bed_bath_ratio, area_per_bedroom")

# ── 4. Train/test split ──────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"\nSplit: Train={X_train.shape[0]}, Test={X_test.shape[0]}")

# ── 5. Model definitions with hyperparameter search spaces ────
print("\nTraining models with cross-validation & hyperparameter tuning...")

model_configs = {
    'Linear Regression': {
        'model': LinearRegression(),
        'params': {},
        'cv': True,
    },
    'Ridge Regression': {
        'model': Ridge(),
        'params': {'alpha': uniform(0.1, 10)},
        'cv': True,
    },
    'Random Forest': {
        'model': RandomForestRegressor(random_state=42),
        'params': {
            'n_estimators': randint(100, 500),
            'max_depth': [10, 15, 20, 25, None],
            'min_samples_split': randint(2, 10),
            'min_samples_leaf': randint(1, 5),
            'max_features': ['sqrt', 'log2', 0.8],
        },
        'cv': True,
    },
    'Gradient Boosting': {
        'model': GradientBoostingRegressor(random_state=42),
        'params': {
            'n_estimators': randint(100, 400),
            'max_depth': [4, 6, 8, 10],
            'learning_rate': uniform(0.01, 0.2),
            'subsample': uniform(0.7, 0.3),
            'min_samples_split': randint(2, 10),
        },
        'cv': True,
    },
}

results = {}
cv_folds = 5

for name, config in model_configs.items():
    print(f"\n  -- {name} --")

    if config['params']:
        # Hyperparameter tuning
        search = RandomizedSearchCV(
            config['model'],
            config['params'],
            n_iter=30 if name in ['Random Forest', 'Gradient Boosting'] else 10,
            cv=cv_folds,
            scoring='r2',
            random_state=42,
            n_jobs=-1,
            verbose=0,
        )
        search.fit(X_train, y_train)
        best_model = search.best_estimator_
        print(f"  Best params: {search.best_params_}")
        cv_score = search.best_score_
    else:
        config['model'].fit(X_train, y_train)
        best_model = config['model']
        cv_scores = cross_val_score(best_model, X_train, y_train, cv=cv_folds, scoring='r2')
        cv_score = cv_scores.mean()

    # Evaluate on test set
    pred = best_model.predict(X_test)
    r2 = r2_score(y_test, pred)
    mae = mean_absolute_error(y_test, pred)
    rmse = np.sqrt(mean_squared_error(y_test, pred))
    mape = np.mean(np.abs((y_test - pred) / y_test)) * 100

    results[name] = {
        'model': best_model,
        'r2': r2,
        'cv_r2': cv_score,
        'mae': mae,
        'rmse': rmse,
        'mape': mape,
    }

    print(f"  CV R² (mean):  {cv_score:.4f}")
    print(f"Base Model R² Score: {r2:.4f}")
    print(f"  MAE:           {mae:,.0f}")
    print(f"  RMSE:          {rmse:,.0f}")
    print(f"  MAPE:          {mape:.2f}%")

# ── 6. Select best model ──────────────────────────────────────
print("\n" + "=" * 60)
best_name = max(results, key=lambda k: results[k]['r2'])
best = results[best_name]
print(f"Best model: {best_name}")
print(f"   Test R²:  {best['r2']:.4f}")
print(f"   CV R²:    {best['cv_r2']:.4f}")
print(f"   MAE:      {best['mae']:,.0f}")
print(f"   RMSE:     {best['rmse']:,.0f}")
print(f"   MAPE:     {best['mape']:.2f}%")

# ── 7. Train quantile models for prediction intervals ─────────
print("\nTraining quantile models for prediction intervals...")
print("   (Using GradientBoosting with quantile loss)")

# Use GradientBoostingRegressor with quantile loss for prediction intervals
quantile_models = {}
for alpha in [0.1, 0.5, 0.9]:  # 10th, 50th (median), 90th percentile
    qr = GradientBoostingRegressor(
        loss='quantile',
        alpha=alpha,
        n_estimators=best['model'].n_estimators if hasattr(best['model'], 'n_estimators') else 200,
        max_depth=best['model'].max_depth if hasattr(best['model'], 'max_depth') else 6,
        random_state=42,
    )
    qr.fit(X_train, y_train)
    quantile_models[alpha] = qr
    print(f"Quantile {alpha} Model trained")

# Compute 80% prediction interval coverage
low = quantile_models[0.1].predict(X_test)
high = quantile_models[0.9].predict(X_test)
coverage_80 = np.mean((y_test >= low) & (y_test <= high))
print(f"\n   80% prediction interval coverage: {coverage_80:.1%}")
print(f"   Avg interval width: {(high - low).mean():,.0f}")

# ── 8. Save everything ────────────────────────────────────────
print("\nSaving models and artifacts...")

joblib.dump(best['model'], os.path.join(MODEL_DIR, 'house_model.pkl'))
joblib.dump(encoders, os.path.join(MODEL_DIR, 'encoders.pkl'))
joblib.dump(feature_cols, os.path.join(MODEL_DIR, 'feature_cols.pkl'))

# Save quantile models
joblib.dump(quantile_models[0.1], os.path.join(MODEL_DIR, 'quantile_10.pkl'))
joblib.dump(quantile_models[0.9], os.path.join(MODEL_DIR, 'quantile_90.pkl'))

print("   house_model.pkl (best model)")
print("   encoders.pkl")
print("   feature_cols.pkl")
print("   quantile_10.pkl (lower bound model)")
print("   quantile_90.pkl (upper bound model)")

# Clean up unused file
unused = os.path.join(MODEL_DIR, 'label_encoder.pkl')
if os.path.exists(unused):
    os.remove(unused)
    print("   Removed unused label_encoder.pkl")

# ── 9. Save training report ───────────────────────────────────
report = {
    'best_model': best_name,
    'metrics': {
        'r2': round(best['r2'], 4),
        'cv_r2': round(best['cv_r2'], 4),
        'mae': round(best['mae'], 0),
        'rmse': round(best['rmse'], 0),
        'mape': round(best['mape'], 2),
    },
    'prediction_interval': {
        'coverage_80': round(coverage_80, 4),
        'avg_width': round(float((high - low).mean()), 0),
    },
    'all_models': {
        name: {
            'r2': round(r['r2'], 4),
            'cv_r2': round(r['cv_r2'], 4),
            'mae': round(r['mae'], 0),
            'rmse': round(r['rmse'], 0),
            'mape': round(r['mape'], 2),
        }
        for name, r in results.items()
    },
    'dataset': {
        'rows': len(df),
        'features': len(feature_cols),
        'cities': len(encoders['city'].classes_),
        'localities': len(encoders['locality'].classes_),
    },
}

with open(os.path.join(REPORT_DIR, 'training_report.json'), 'w') as f:
    json.dump(report, f, indent=2)
print(f"\nReport saved → reports/training_report.json")

# ── 10. Feature importance ────────────────────────────────────
if hasattr(best['model'], 'feature_importances_'):
    print("\n── Top 10 Feature Importances ──")
    imp = pd.Series(best['model'].feature_importances_, index=feature_cols).sort_values(ascending=False)
    for feat, val in imp.head(10).items():
        bar = "█" * int(val * 100)
        print(f"   {feat:25s} {val:.4f} {bar}")
    print("All artifacts saved to model/ directory.")

print("Training Complete!")

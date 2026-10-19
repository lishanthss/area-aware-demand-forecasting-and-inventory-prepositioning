import pandas as pd
import joblib
import os

# Base directory = src
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load feature schema
FEATURES_PATH = os.path.join(BASE_DIR, "feature_columns.pkl")
training_columns = joblib.load(FEATURES_PATH)
# Paths
MODEL_PATH = os.path.join(BASE_DIR, "demand_model.pkl")
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "real_sales.csv")

# Load model
model = joblib.load(MODEL_PATH)
# Load quantile models (for uncertainty)
model_q10 = joblib.load(os.path.join(BASE_DIR, "demand_model_q10.pkl"))
model_q50 = joblib.load(os.path.join(BASE_DIR, "demand_model_q50.pkl"))
model_q90 = joblib.load(os.path.join(BASE_DIR, "demand_model_q90.pkl"))


# Example future input
new_input = {
    "month": 11,
    "day_of_week": 4,
    "rain": 0,
    "temperature": 28,
    "is_festival": 1,
    "city_Sao Paulo": 1,
    "product_Computers": 1
}

input_df = pd.DataFrame([new_input])

# Align input with training feature schema
for col in training_columns:
    if col not in input_df.columns:
        input_df[col] = 0

# Ensure correct column order
input_df = input_df[training_columns]

# Predict
# Use quantile models for uncertainty
low = max(0.0, float(model_q10.predict(input_df)[0]))
mid = max(0.0, float(model_q50.predict(input_df)[0]))
high = max(0.0, float(model_q90.predict(input_df)[0]))

print(f"[Forecast] Demand forecast: {round(mid, 1)} units")
print(f"[Uncertainty] Range: {round(low, 1)} - {round(high, 1)} units (90% CI)")


# Inventory decision
THRESHOLD = 5
if high > THRESHOLD:
    print("Action: Pre-stock product in regional fulfillment center")
else:
    print("Action: Keep stock in central warehouse")

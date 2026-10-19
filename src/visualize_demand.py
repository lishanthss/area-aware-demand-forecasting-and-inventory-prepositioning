import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(BASE_DIR, "demand_model.pkl"))
features = joblib.load(os.path.join(BASE_DIR, "feature_columns.pkl"))

cities = ["Sao Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre"]
product = "BedBathTable"
temperature = 26.0
rain = 0
festival = 0

demands = []
for city in cities:
    data = {
        "month": 6,
        "day_of_week": 2,
        "temperature": temperature,
        "rain": rain,
        "is_festival": festival,
        f"city_{city}": 1,
        f"product_{product}": 1
    }
    df = pd.DataFrame([data])
    for col in features:
        if col not in df.columns:
            df[col] = 0
    df = df[features]
    pred = max(0.0, float(model.predict(df)[0]))
    demands.append(round(pred, 2))

plt.figure(figsize=(9, 5))
bars = plt.bar(cities, demands, color=['#4f46e5', '#6366f1', '#818cf8', '#a855f7', '#c084fc'])
plt.title(f"Predicted Daily Demand by City ({product})", fontsize=13, fontweight='bold')
plt.xlabel("City", fontsize=11)
plt.ylabel("Forecasted Units / Day", fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.5)

for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2.0, yval + 0.05, f"{yval}", ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
output_img = os.path.join(BASE_DIR, "..", "images", "predicted_demand.png")
plt.savefig(output_img, dpi=150)
print(f"Chart saved to {output_img}")
plt.show()
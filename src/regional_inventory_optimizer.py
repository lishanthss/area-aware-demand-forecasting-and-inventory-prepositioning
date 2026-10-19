import joblib
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Load trained model
model = joblib.load(os.path.join(BASE_DIR, "demand_model.pkl"))

# Load training feature schema
training_columns = joblib.load(os.path.join(BASE_DIR, "feature_columns.pkl"))

# Product and external signals
product = "BedBathTable"
temperature = 26
rain = 0
festival = 0

# Cities we want to compare
cities = ["Sao Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre"]


def predict_city_demand(city):

    data = {
        "temperature": temperature,
        "rain": rain,
        "is_festival": festival,
        f"city_{city}": 1,
        f"product_{product}": 1
    }

    df = pd.DataFrame([data])

    # align with training schema
    for col in training_columns:
        if col not in df.columns:
            df[col] = 0

    df = df[training_columns]

    prediction = model.predict(df)[0]

    # convert numpy float to normal rounded number
    prediction = max(0.0, round(float(prediction), 2))

    return prediction


# Predict demand for each city
city_predictions = {}

for city in cities:
    city_predictions[city] = predict_city_demand(city)

print("\nCITY DEMAND FORECAST")
print("----------------------")

for city, demand in city_predictions.items():
    print(f"{city}: {demand} units")


# Define regional grouping
regions = {
    "Southeast_Region": ["Sao Paulo", "Rio de Janeiro", "Belo Horizonte"],
    "South_Region": ["Curitiba", "Porto Alegre"]
}

# Calculate regional demand
regional_demand = {}

for region, city_list in regions.items():

    total = 0

    for c in city_list:
        total += city_predictions[c]

    regional_demand[region] = round(total, 2)


print("\nREGIONAL DEMAND")
print("----------------")

for region, demand in regional_demand.items():
    print(f"{region}: {demand} units")


# Determine high and low demand regions
highest_region = max(regional_demand, key=regional_demand.get)
lowest_region = min(regional_demand, key=regional_demand.get)

difference = regional_demand[highest_region] - regional_demand[lowest_region]

transfer_amount = int(difference / 2)

print("\nINVENTORY RECOMMENDATION")
print("-------------------------")

if transfer_amount > 0:

    print(
        f"Predicted demand is higher in {highest_region}."
    )

    print(
        f"Recommended action: Move about {transfer_amount} units of {product} "
        f"from {lowest_region} warehouse to {highest_region} warehouse."
    )

else:

    print(
        "Demand is balanced across regions. No inventory transfer required."
    )
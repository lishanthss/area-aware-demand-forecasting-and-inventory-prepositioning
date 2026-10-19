import pandas as pd

# Example predicted demand
city_demand = {
    "Sao Paulo": 25,
    "Rio de Janeiro": 12,
    "Belo Horizonte": 5,
    "Curitiba": 4,
    "Porto Alegre": 3
}

df = pd.DataFrame(list(city_demand.items()), columns=["city", "predicted_demand"])

avg_demand = df["predicted_demand"].mean()

df["surplus"] = avg_demand - df["predicted_demand"]

surplus_cities = df[df["surplus"] > 0].to_dict('records')
shortage_cities = df[df["surplus"] < 0].to_dict('records')

print("Average demand:", round(avg_demand))
print()

print("Surplus cities:")
for c in surplus_cities:
    print(f"- {c['city']}: {round(c['surplus'])} units surplus")
print()

print("High demand cities:")
for c in shortage_cities:
    print(f"- {c['city']}: {round(abs(c['surplus']))} units needed")
print()

for low in surplus_cities:
    for high in shortage_cities:
        if low["surplus"] <= 0:
            break
        if high["surplus"] >= 0:
            continue
            
        transfer_units = int(min(low["surplus"], abs(high["surplus"])))
        
        if transfer_units > 0:
            print(f"Move {transfer_units} units from {low['city']} warehouse to {high['city']} warehouse")
            low["surplus"] -= transfer_units
            high["surplus"] += transfer_units
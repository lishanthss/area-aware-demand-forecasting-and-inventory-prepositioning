import random

regions = ["Southeast_Region", "South_Region"]

stockouts_without = 0
stockouts_with = 0

simulations = 1000

for _ in range(simulations):

    initial_stock = {
        "Southeast_Region": random.randint(15, 35),
        "South_Region": random.randint(15, 35)
    }

    # Demand with stochastic volatility (Southeast metro demand vs South region demand)
    demand = {
        "Southeast_Region": random.uniform(20, 35),
        "South_Region": random.uniform(5, 18)
    }

    # scenario 1: without system
    for r in regions:
        if demand[r] > initial_stock[r]:
            stockouts_without += 1

    # scenario 2: dynamic transfer logic
    southeast_diff = demand["Southeast_Region"] - initial_stock["Southeast_Region"]
    south_diff = demand["South_Region"] - initial_stock["South_Region"]

    new_stock = {
        "Southeast_Region": initial_stock["Southeast_Region"],
        "South_Region": initial_stock["South_Region"]
    }

    if southeast_diff > 0 and south_diff < 0:
        transfer = min(southeast_diff, abs(south_diff))
        new_stock["Southeast_Region"] += transfer
        new_stock["South_Region"] -= transfer
    elif south_diff > 0 and southeast_diff < 0:
        transfer = min(south_diff, abs(southeast_diff))
        new_stock["South_Region"] += transfer
        new_stock["Southeast_Region"] -= transfer

    for r in regions:
        if demand[r] > new_stock[r]:
            stockouts_with += 1

print("\nSimulation Results")
print("-------------------")

print("Stockouts without system:", stockouts_without)
print("Stockouts with system:", stockouts_with)

reduction = ((stockouts_without - stockouts_with) / stockouts_without) * 100

print("Stockout reduction:", round(reduction,2), "%")
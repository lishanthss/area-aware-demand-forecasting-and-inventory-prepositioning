import os
import json
import urllib.request
import pandas as pd
from datetime import datetime
import holidays

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(BASE_DIR, "..", "data", "olist_raw")
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
OUTPUT_PATH = os.path.join(DATA_DIR, "real_sales.csv")
BACKUP_PATH = os.path.join(DATA_DIR, "real_sales_india_backup.csv")

# 1. Backup original real_sales.csv if not already backed up
if os.path.exists(OUTPUT_PATH) and not os.path.exists(BACKUP_PATH):
    import shutil
    shutil.copy(OUTPUT_PATH, BACKUP_PATH)
    print(f"Backed up existing real_sales.csv to {BACKUP_PATH}")

print("\n--- STEP 1: Loading Olist Raw Tables ---")
orders = pd.read_csv(os.path.join(RAW_DIR, "olist_orders_dataset.csv"))
items = pd.read_csv(os.path.join(RAW_DIR, "olist_order_items_dataset.csv"))
customers = pd.read_csv(os.path.join(RAW_DIR, "olist_customers_dataset.csv"))
products = pd.read_csv(os.path.join(RAW_DIR, "olist_products_dataset.csv"))
translations = pd.read_csv(os.path.join(RAW_DIR, "product_category_name_translation.csv"))

# Filter delivered orders in consistent date range 2017-01-01 to 2018-08-31
orders = orders[orders['order_status'] == 'delivered'].copy()
orders['date'] = pd.to_datetime(orders['order_purchase_timestamp']).dt.strftime('%Y-%m-%d')
orders = orders[(orders['date'] >= '2017-01-01') & (orders['date'] <= '2018-08-31')].copy()
print(f"Delivered orders in window (2017-01-01 to 2018-08-31): {len(orders):,}")

# Merge with customers to get city
df_merged = orders[['order_id', 'customer_id', 'date']].merge(
    customers[['customer_id', 'customer_city']], on='customer_id', how='inner'
)

# Merge with order items
df_merged = df_merged.merge(
    items[['order_id', 'product_id']], on='order_id', how='inner'
)

# Merge with products & english category translation
products = products.merge(translations, on='product_category_name', how='left')
df_merged = df_merged.merge(
    products[['product_id', 'product_category_name_english']], on='product_id', how='inner'
)

# Standardize City and Product names
city_map = {
    'sao paulo': 'Sao Paulo',
    'rio de janeiro': 'Rio de Janeiro',
    'belo horizonte': 'Belo Horizonte',
    'curitiba': 'Curitiba',
    'porto alegre': 'Porto Alegre',
    'salvador': 'Salvador'
}

product_map = {
    'bed_bath_table': 'BedBathTable',
    'health_beauty': 'HealthBeauty',
    'sports_leisure': 'SportsLeisure',
    'furniture_decor': 'FurnitureDecor',
    'computers_accessories': 'Computers',
    'housewares': 'Housewares',
    'watches_gifts': 'WatchesGifts',
    'toys': 'Toys'
}

df_merged = df_merged[
    df_merged['customer_city'].isin(city_map.keys()) &
    df_merged['product_category_name_english'].isin(product_map.keys())
].copy()

df_merged['city'] = df_merged['customer_city'].map(city_map)
df_merged['product'] = df_merged['product_category_name_english'].map(product_map)

# Group to get units sold per date, city, product
actual_sales = df_merged.groupby(['date', 'city', 'product']).size().reset_index(name='units_sold')
print(f"Aggregated actual sales rows: {len(actual_sales):,}")

print("\n--- STEP 2: Creating Complete Regular Time-Series Grid ---")
all_dates = pd.date_range(start='2017-01-01', end='2018-08-31', freq='D').strftime('%Y-%m-%d')
target_cities = list(city_map.values())
target_products = list(product_map.values())

grid = pd.MultiIndex.from_product(
    [all_dates, target_cities, target_products],
    names=['date', 'city', 'product']
).to_frame().reset_index(drop=True)

# Merge actual sales with complete grid (fill 0 for dates with no orders)
sales_grid = grid.merge(actual_sales, on=['date', 'city', 'product'], how='left')
sales_grid['units_sold'] = sales_grid['units_sold'].fillna(0).astype(int)

# Extract time features
date_dt = pd.to_datetime(sales_grid['date'])
sales_grid['month'] = date_dt.dt.month
sales_grid['day_of_week'] = date_dt.dt.dayofweek

print(f"Full grid shape: {sales_grid.shape}")

print("\n--- STEP 3: Fetching Real Historical Weather via Open-Meteo API ---")
city_coords = {
    'Sao Paulo': (-23.55, -46.63),
    'Rio de Janeiro': (-22.90, -43.17),
    'Belo Horizonte': (-19.92, -43.94),
    'Curitiba': (-25.42, -49.27),
    'Porto Alegre': (-30.03, -51.23),
    'Salvador': (-12.97, -38.51)
}

weather_records = []
for c_name, (lat, lon) in city_coords.items():
    print(f"Fetching real historical weather for {c_name} (lat={lat}, lon={lon})...")
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}&start_date=2017-01-01&end_date=2018-08-31&"
        f"daily=temperature_2m_max,precipitation_sum&timezone=America%2FSao_Paulo"
    )
    req = urllib.request.Request(url, headers={'User-Agent': 'AreaAwareLogistics/1.0'})
    res = json.loads(urllib.request.urlopen(req).read().decode('utf-8'))
    daily = res['daily']
    for d, temp, precip in zip(daily['time'], daily['temperature_2m_max'], daily['precipitation_sum']):
        weather_records.append({
            'date': d,
            'city': c_name,
            'temperature': round(float(temp), 1) if temp is not None else 25.0,
            'precipitation_mm': round(float(precip), 1) if precip is not None else 0.0,
            'rain': 1 if (precip is not None and precip > 1.0) else 0
        })

df_weather = pd.DataFrame(weather_records)
print(f"Total weather records collected: {len(df_weather):,}")

# Merge weather into grid
sales_grid = sales_grid.merge(df_weather, on=['date', 'city'], how='left')

print("\n--- STEP 4: Harmonizing Real Holiday & Festival Calendars ---")
br_holidays = holidays.Brazil(years=[2017, 2018])
# Add major Brazilian e-commerce events (Black Friday dates)
black_fridays = {'2017-11-24', '2017-11-25', '2017-11-26', '2017-11-27'}  # Black Friday weekend 2017

def check_festival(date_str):
    d = datetime.strptime(date_str, '%Y-%m-%d').date()
    if d in br_holidays or date_str in black_fridays:
        return 1
    return 0

sales_grid['is_festival'] = sales_grid['date'].apply(check_festival)

# Reorder columns to align with system schema
final_df = sales_grid[[
    'date', 'city', 'product', 'units_sold', 'month', 'day_of_week',
    'temperature', 'rain', 'is_festival'
]]

# Save harmonized dataset
final_df.to_csv(OUTPUT_PATH, index=False)

print("\n=======================================================")
print(" SUCCESS: Real Harmonized Dataset Created!")
print("=======================================================")
print(f"Saved to: {OUTPUT_PATH}")
print(f"Total Rows: {len(final_df):,}")
print(f"Unique Cities: {final_df['city'].unique().tolist()}")
print(f"Unique Products: {final_df['product'].unique().tolist()}")
print("\nDataset Sample:")
print(final_df.head(10))
print("\nUnits Sold Summary:")
print(final_df['units_sold'].describe())
print(f"Festival day percentage: {round(final_df['is_festival'].mean() * 100, 2)}%")
print(f"Rainy day percentage: {round(final_df['rain'].mean() * 100, 2)}%")
print(f"Average temperature: {round(final_df['temperature'].mean(), 1)} °C")

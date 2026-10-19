import os
import urllib.request

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "olist_raw")
os.makedirs(RAW_DIR, exist_ok=True)

BASE_URL = "https://raw.githubusercontent.com/olist/work-at-olist-data/master/datasets"
FILES = [
    "olist_orders_dataset.csv",
    "olist_order_items_dataset.csv",
    "olist_customers_dataset.csv",
    "olist_sellers_dataset.csv",
    "olist_products_dataset.csv",
    "product_category_name_translation.csv"
]

print("Starting download of Olist datasets...")
for filename in FILES:
    dest_path = os.path.join(RAW_DIR, filename)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        print(f"Already downloaded: {filename} ({round(os.path.getsize(dest_path)/(1024*1024), 2)} MB)")
        continue
    url = f"{BASE_URL}/{filename}"
    print(f"Downloading {filename} from {url} ...")
    urllib.request.urlretrieve(url, dest_path)
    size_mb = round(os.path.getsize(dest_path) / (1024 * 1024), 2)
    print(f"Downloaded {filename} ({size_mb} MB)")

print("\nAll Olist raw files are in:", os.path.abspath(RAW_DIR))

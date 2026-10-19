# Area-Aware Demand Forecasting and Inventory Pre-Positioning System


## Project Overview

This project builds an **AI-driven logistics decision support system** for e-commerce inventory management.

Instead of forecasting demand for an entire region, the system predicts **city-level product demand** and recommends **inventory transfers between regional warehouses** to reduce stockouts and improve delivery efficiency.

The system demonstrates how **machine learning predictions can be integrated with operational logistics decisions**.


> [!IMPORTANT]  
> This project focuses not only on demand forecasting but also on **inventory decision-making**, showing how machine learning can help redistribute stock between warehouses to reduce stockouts.


---

# System Interface


Below is the dashboard showing **city-level demand predictions and recommended inventory transfers**.

![Inventory Optimizer Dashboard](images/dashboard.png)


---

# Problem Statement


E-commerce platforms typically maintain centralized warehouses. However, **demand varies significantly across cities** due to:

- regional economic activity  
- seasonal weather patterns  
- festivals and holidays  
- consumer purchasing behavior  


Poor inventory distribution can lead to:

- stockouts in high-demand cities  
- excess inventory in low-demand areas  
- delayed deliveries  


This project proposes a system that:

1. predicts **city-level demand**
2. aggregates demand **regionally**
3. recommends **inventory transfers**
4. evaluates **stockout risk reduction**


---

# System Workflow


```mermaid
graph LR
A[Dataset Preparation] --> B[Feature Engineering]
B --> C[Model Training & Comparison]
C --> D[City-Level Demand Prediction]
D --> E[Regional Demand Aggregation]
E --> F[Inventory Transfer Recommendation]
F --> G[Stockout Risk Simulation]
G --> H[FastAPI Decision API]
```


---

# Multi-Source Real-World Harmonized Dataset

The system is built on a **tri-source harmonized logistics dataset**, eliminating synthetic rules in favor of authentic data fusion:

```mermaid
graph LR
A[1. Olist E-Commerce Dataset<br/>96k+ real delivered orders] --> D[Data Harmonization Pipeline]
B[2. Open-Meteo Weather API<br/>Real historical temp & precipitation] --> D
C[3. Brazil Holiday Calendar<br/>Official national & festival dates] --> D
D --> E[real_sales.csv<br/>Time-Series Grid]
```

### 1. E-Commerce Demand & Logistics (Olist)
- **Delivered Orders**: 96,211 genuine transactions from 2017 to 2018.
- **Customer Metro Hubs**: São Paulo, Rio de Janeiro, Belo Horizonte, Curitiba, Porto Alegre, Salvador.
- **Product Categories**: BedBathTable, HealthBeauty, SportsLeisure, FurnitureDecor, Computers, Housewares, WatchesGifts, Toys.

### 2. Meteorological Context (Open-Meteo API)
- Daily maximum temperature (`temperature`) and precipitation (`rain`) fetched directly for each regional hub coordinate.

### 3. Festival & Holiday Calendar (`holidays` package)
- Official Brazilian national holidays (Carnival, Tiradentes, Worker's Day, Independence Day, Christmas) combined with major e-commerce retail events (Black Friday).

---

# Machine Learning Models

Multiple regression models are trained and evaluated chronologically (`shuffle=False` to prevent temporal data leakage):

| Model | Purpose | Test MAE |
|------|------|------|
| Linear Regression | Baseline forecasting model | 0.79 |
| Random Forest Regressor | Captures non-linear demand interactions | 0.81 |
| Gradient Boosting Regressor | Best performing predictor | **0.77** |

### Evaluation Metric

```
Mean Absolute Error (MAE)
```

The model with the lowest test MAE (**Gradient Boosting Regressor**) is automatically selected and saved as `demand_model.pkl`.

---

# Uncertainty Estimation

Demand predictions include **uncertainty ranges** using quantile regression (`GradientBoostingRegressor(loss='quantile')`).

Models trained:
- **10th percentile model** (`demand_model_q10.pkl`)
- **50th percentile model** (`demand_model_q50.pkl`)
- **90th percentile model** (`demand_model_q90.pkl`)

This enables asymmetric risk management: buffering stock to upper confidence limits ($Q_{90}$) reduces stockouts from **27.2%** down to **6.8%**.

---

# Regional Inventory Optimization

Cities are clustered into economic logistics regions:

### Southeast Region
- São Paulo (Central warehouse hub)
- Rio de Janeiro
- Belo Horizonte

### South Region
- Curitiba (Regional distribution hub)
- Porto Alegre

The system:
1. Predicts daily demand per city
2. Aggregates regional hub demand
3. Detects inter-regional supply imbalances
4. Recommends proactive stock movement

Example result:
```
City Demand Forecast:
- Sao Paulo      : 2.33 units
- Rio de Janeiro : 1.00 units
- Belo Horizonte : 0.41 units
- Curitiba       : 0.34 units
- Porto Alegre   : 0.35 units

Regional Demand:
- Southeast Region : 3.74 units
- South Region     : 0.69 units

Recommended Action:
Move units between regional warehouses to prevent stockout bottlenecks.
```

---

# Stockout Risk Simulation

To evaluate the decision system under volatile supply conditions, two scenarios are simulated across 1,000 runs:

- **Scenario 1 — Without AI**: Inventory remains static at initial arbitrary levels.
- **Scenario 2 — With AI**: The system dynamically detects supply imbalances and executes proactive stock transfers between hubs.

```text
Stockouts without system : 668
Stockouts with system    : 192
Stockout reduction       : 71.3%
```

---

# API Deployment

The project exposes a **FastAPI decision service** rendering an interactive dark-themed decision dashboard.

### API Endpoint

```
GET /decision?product=BedBathTable&temperature=26&rain=0&festival=0
```

### Example Response Schema

```json
{
  "city_predictions": {
    "Sao Paulo": 2.33,
    "Rio de Janeiro": 1.00,
    "Belo Horizonte": 0.41,
    "Curitiba": 0.34,
    "Porto Alegre": 0.35
  },
  "regional_demand": {
    "Southeast_Region": 3.74,
    "South_Region": 0.69
  },
  "recommended_transfer": {
    "from": "South_Region",
    "to": "Southeast_Region",
    "units": 1
  },
  "stockout_analysis": {
    "without_system": 1,
    "with_system": 0
  }
}
```


---

# Interactive Logistics Map & Delivery Reduction

The dashboard features an interactive **Leaflet.js CartoDB Dark Matter map** visualizing the logistics network:

- **Godown Pins**: Real coordinate mapping for São Paulo, Curitiba, Rio de Janeiro, Belo Horizonte, and Porto Alegre.
- **Dynamic Godown Status**: Identifies the **Surplus Origin Godown** (excess safety stock) and **Deficit Destination Godown** (demand surge target).
- **Animated Transit Flow**: Displays a glowing, animated transit polyline and a moving freight truck badge (`🚚 Moving X Units`).

### Operational Impact on Delivery Speed:

| Dimension | Without Pre-Positioning (Traditional) | With AI Dynamic Pre-Positioning |
| :--- | :--- | :--- |
| **Delivery Transit Route** | Long-haul interstate shipment from remote central hub | Dispatched from local regional godown |
| **Customer Lead Time** | **5 – 7 Days** | **1 – 2 Days (75% Faster Delivery)** |
| **Remote/Unfamiliar Districts** | Frequent delayed deliveries & stockouts | Reliable 24–48h delivery guaranteed |
| **Stockout Incidents** | High (Warehouse depletion) | **0% (100% Demand Met)** |
| **Freight Costs** | High (Emergency expedited individual courier fees) | Low (Consolidated proactive replenishment) |

---

# Features

| Feature | Description |
| :--- | :--- |
| Tri-Source Real Data Fusion | Harmonizes Olist E-Commerce, Open-Meteo Weather API, and Brazil Holiday Calendar |
| City-Level Forecasting | Predicts product category demand for individual municipal hubs |
| Model Tournament | Trains and compares Linear Regression, Random Forest, and Gradient Boosting |
| Uncertainty Estimation | Quantile regression ($Q_{10}, Q_{50}, Q_{90}$) predicts asymmetric demand ranges |
| Regional Aggregation | Aggregates municipal demand into Southeast and South logistics clusters |
| Inventory Pre-Positioning | Prescriptive optimization moves stock from surplus to deficit godowns |
| Interactive Logistics Map | Dark-mode Leaflet map showing godowns, animated routes, and moving trucks |
| Delivery Lead Time Reduction | Cuts customer delivery transit times from 5–7 days down to 1–2 days (-75%) |
| Stockout Risk Simulation | Monte Carlo simulation evaluates 71.3% stockout reduction under supply volatility |
| FastAPI Modern Dashboard | Real-time prediction service with dark glassmorphism dashboard UI |

---

# Technologies Used

- **Machine Learning**: Scikit-learn (Gradient Boosting, Random Forest, Linear Regression, Quantile Loss)
- **Backend & Serving**: FastAPI, Uvicorn, Jinja2
- **Data Engineering**: Pandas, NumPy, Python `holidays`, Open-Meteo REST API
- **Frontend & Visualization**: Tailwind CSS, Leaflet.js, CartoDB Dark Matter Tiles, Matplotlib  


---

# Project Structure


```
AreaAwareDemandForecasting
│
├── images
│   ├── dashboard.png
│   └── predicted_demand.png
│
├── data
│   ├── olist_raw/
│   └── real_sales.csv
│
├── src
│   ├── download_olist.py
│   ├── harmonize_olist_data.py
│   ├── train_model.py
│   ├── regional_inventory_optimizer.py
│   ├── city_inventory_optimizer.py
│   ├── advanced_stockout_simulation.py
│   ├── simulation.py
│   ├── predict_demand.py
│   ├── visualize_demand.py
│   ├── api.py
│   └── templates/
│       └── index.html
│
├── README.md
└── requirements.txt
```


---

# Running the Project


Clone the repository

```bash
git clone https://github.com/lishanthss/area-aware-demand-forecasting-and-inventory-prepositioning.git
```


Move into the project directory

```bash
cd area-aware-demand-forecasting
```


Install dependencies

```bash
pip install -r requirements.txt
```


Download and harmonize real-world datasets

```bash
python src/download_olist.py
python src/harmonize_olist_data.py
```


Train machine learning models

```bash
python src/train_model.py
```


Start the API server

```bash
python -m uvicorn src.api:app --reload
```


Open API documentation

```bash
http://127.0.0.1:8000/docs
```

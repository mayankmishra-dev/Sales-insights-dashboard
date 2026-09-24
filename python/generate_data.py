"""
generate_data.py
-----------------
Generates a realistic, synthetic retail sales dataset used throughout this project.
Run this once to (re)create data/sales_data.csv.

Why synthetic data?
Real company sales data is confidential, so a randomized-but-realistic dataset
is generated here with believable seasonality, regional spread, and product mix
so the SQL + Power BI + EDA work on something that behaves like real business data.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# ---------------------------------------------------------------
# Reference (dimension) data
# ---------------------------------------------------------------
regions = ["North", "South", "East", "West", "Central"]

products = [
    ("Wireless Mouse", "Electronics", 599),
    ("Mechanical Keyboard", "Electronics", 2499),
    ("USB-C Hub", "Electronics", 1299),
    ("27in Monitor", "Electronics", 12999),
    ("Bluetooth Speaker", "Electronics", 1999),
    ("Office Chair", "Furniture", 6499),
    ("Standing Desk", "Furniture", 14999),
    ("Bookshelf", "Furniture", 3499),
    ("Table Lamp", "Furniture", 899),
    ("Notebook Set", "Stationery", 199),
    ("Whiteboard", "Stationery", 1499),
    ("Sticky Notes Pack", "Stationery", 99),
    ("Backpack", "Accessories", 1799),
    ("Water Bottle", "Accessories", 349),
    ("Wall Clock", "Home Decor", 749),
    ("Photo Frame Set", "Home Decor", 549),
]

customer_segments = ["Consumer", "Small Business", "Corporate", "Enterprise"]

n_customers = 400
customer_ids = [f"CUST{str(i).zfill(4)}" for i in range(1, n_customers + 1)]
customer_segment_map = {c: np.random.choice(customer_segments, p=[0.5, 0.25, 0.18, 0.07]) for c in customer_ids}
customer_region_map = {c: np.random.choice(regions) for c in customer_ids}

# ---------------------------------------------------------------
# Generate transactions across 2 years with seasonality
# ---------------------------------------------------------------
start_date = datetime(2023, 1, 1)
end_date = datetime(2024, 12, 31)
n_days = (end_date - start_date).days + 1

rows = []
order_id = 100000

for day_offset in range(n_days):
    current_date = start_date + timedelta(days=day_offset)
    month = current_date.month

    # Seasonality: festive/holiday boost in Oct-Dec, dip in Feb, summer bump in Jun
    seasonal_factor = 1.0
    if month in (10, 11, 12):
        seasonal_factor = 1.6
    elif month == 2:
        seasonal_factor = 0.75
    elif month in (6, 7):
        seasonal_factor = 1.2

    weekday_factor = 1.3 if current_date.weekday() >= 5 else 1.0  # weekend bump
    base_orders = np.random.poisson(lam=6 * seasonal_factor * weekday_factor)

    for _ in range(base_orders):
        order_id += 1
        product_name, category, unit_price = products[np.random.randint(len(products))]
        customer_id = np.random.choice(customer_ids)
        quantity = np.random.choice([1, 1, 1, 2, 2, 3, 4], p=[0.35, 0.2, 0.15, 0.15, 0.08, 0.04, 0.03])

        # Small random price fluctuation (discounts / offers)
        discount_pct = np.random.choice([0, 0, 0, 5, 10, 15, 20], p=[0.4, 0.15, 0.1, 0.15, 0.1, 0.06, 0.04])
        gross_amount = unit_price * quantity
        discount_amount = round(gross_amount * discount_pct / 100, 2)
        net_sales = round(gross_amount - discount_amount, 2)

        # Cost of goods ~ 55-70% of unit price, category dependent
        cost_ratio = {
            "Electronics": 0.68,
            "Furniture": 0.62,
            "Stationery": 0.45,
            "Accessories": 0.55,
            "Home Decor": 0.50,
        }[category]
        cost = round(unit_price * quantity * cost_ratio, 2)
        profit = round(net_sales - cost, 2)

        region = customer_region_map[customer_id]
        segment = customer_segment_map[customer_id]

        rows.append({
            "OrderID": order_id,
            "OrderDate": current_date.strftime("%Y-%m-%d"),
            "CustomerID": customer_id,
            "CustomerSegment": segment,
            "Region": region,
            "ProductName": product_name,
            "Category": category,
            "UnitPrice": unit_price,
            "Quantity": quantity,
            "DiscountPct": discount_pct,
            "GrossAmount": gross_amount,
            "NetSales": net_sales,
            "Cost": cost,
            "Profit": profit,
        })

df = pd.DataFrame(rows)

# Inject a small amount of realistic "messiness" then clean it in the EDA script
# (a few duplicate rows and a few missing discount values) so the cleaning step
# in the README/EDA script has real work to show.
dupe_sample = df.sample(15, random_state=1)
df = pd.concat([df, dupe_sample], ignore_index=True)
missing_idx = df.sample(25, random_state=2).index
df.loc[missing_idx, "DiscountPct"] = np.nan

import os
out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "sales_data.csv")
df.to_csv(out_path, index=False)
print(f"Generated {len(df)} rows -> {out_path}")

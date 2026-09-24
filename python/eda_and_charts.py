"""
eda_and_charts.py
------------------
Loads the raw sales data, replicates the SQL cleaning steps in pandas,
runs exploratory analysis, and saves the chart set used in the README
(and referenced as the Power BI dashboard visuals) to /images.

Run with:  python python/eda_and_charts.py
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "sales_data.csv")
IMG_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

sns.set_theme(style="darkgrid")
PALETTE = ["#4C6EF5", "#F76707", "#12B886", "#F03E3E", "#AE3EC9"]
plt.rcParams.update({
    "figure.facecolor": "#1B1F2A",
    "axes.facecolor": "#1B1F2A",
    "axes.edgecolor": "#3A3F4B",
    "axes.labelcolor": "#E8E8E8",
    "text.color": "#E8E8E8",
    "xtick.color": "#C7C9D1",
    "ytick.color": "#C7C9D1",
    "grid.color": "#2E3340",
    "axes.titlecolor": "#FFFFFF",
    "font.size": 11,
})

# ---------------------------------------------------------------
# 1. Load + clean (mirrors sql/02_data_cleaning.sql)
# ---------------------------------------------------------------
df = pd.read_csv(DATA_PATH, parse_dates=["OrderDate"])

before = len(df)
df = df.drop_duplicates(subset=["CustomerID", "OrderDate", "ProductName", "Quantity", "NetSales"])
df["DiscountPct"] = df["DiscountPct"].fillna(0)
df = df[(df["NetSales"] > 0) & (df["Quantity"] > 0)]
after = len(df)

df["OrderYear"] = df["OrderDate"].dt.year
df["OrderMonth"] = df["OrderDate"].dt.month
df["OrderMonthName"] = df["OrderDate"].dt.strftime("%b")
df["ProfitMarginPct"] = (df["Profit"] / df["NetSales"] * 100).round(2)

print(f"Rows before cleaning: {before}")
print(f"Rows after cleaning:  {after}  (removed {before - after})")

# ---------------------------------------------------------------
# 2. KPI summary (printed to console -> used in README KPI cards)
# ---------------------------------------------------------------
total_sales = df["NetSales"].sum()
total_profit = df["Profit"].sum()
total_orders = df["OrderID"].nunique()
aov = total_sales / total_orders
margin = total_profit / total_sales * 100

print("\n--- KPI SUMMARY ---")
print(f"Total Sales:   ₹{total_sales:,.0f}")
print(f"Total Profit:  ₹{total_profit:,.0f}")
print(f"Total Orders:  {total_orders:,}")
print(f"AOV:           ₹{aov:,.0f}")
print(f"Overall Margin:{margin:,.1f}%")

# ---------------------------------------------------------------
# 3. Chart 1 — Monthly sales trend with growth
# ---------------------------------------------------------------
monthly = df.groupby([df["OrderDate"].dt.to_period("M")])["NetSales"].sum()
monthly.index = monthly.index.to_timestamp()

fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(monthly.index, monthly.values, marker="o", color=PALETTE[0], linewidth=2.5)
ax.fill_between(monthly.index, monthly.values, color=PALETTE[0], alpha=0.15)
ax.set_title("Monthly Net Sales Trend (2023–2024)", fontsize=14, weight="bold")
ax.set_ylabel("Net Sales (₹)")
fig.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "01_monthly_sales_trend.png"), dpi=150)
plt.close(fig)

# ---------------------------------------------------------------
# 4. Chart 2 — Region-wise sales & profit
# ---------------------------------------------------------------
region_perf = df.groupby("Region")[["NetSales", "Profit"]].sum().sort_values("NetSales", ascending=False)

fig, ax = plt.subplots(figsize=(9, 5))
x = range(len(region_perf))
ax.bar([i - 0.2 for i in x], region_perf["NetSales"], width=0.4, label="Net Sales", color=PALETTE[0])
ax.bar([i + 0.2 for i in x], region_perf["Profit"], width=0.4, label="Profit", color=PALETTE[2])
ax.set_xticks(list(x))
ax.set_xticklabels(region_perf.index)
ax.set_title("Region-wise Sales vs Profit", fontsize=14, weight="bold")
ax.legend(facecolor="#1B1F2A", labelcolor="#E8E8E8")
fig.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "02_region_sales_profit.png"), dpi=150)
plt.close(fig)

# ---------------------------------------------------------------
# 5. Chart 3 — Category share of sales (donut)
# ---------------------------------------------------------------
cat_sales = df.groupby("Category")["NetSales"].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(8.5, 7))
wedges, _, autotexts = ax.pie(
    cat_sales.values, autopct="%1.1f%%",
    colors=PALETTE, startangle=90, pctdistance=0.78,
    wedgeprops={"width": 0.4, "edgecolor": "#1B1F2A"}
)
for t in autotexts:
    t.set_color("#1B1F2A")
    t.set_weight("bold")
ax.set_title("Sales Share by Category", fontsize=14, weight="bold")
ax.legend(wedges, cat_sales.index, loc="center left", bbox_to_anchor=(1.0, 0.5),
          facecolor="#1B1F2A", labelcolor="#E8E8E8", frameon=False)
fig.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "03_category_share.png"), dpi=150)
plt.close(fig)

# ---------------------------------------------------------------
# 6. Chart 4 — Customer segmentation (AOV by segment)
# ---------------------------------------------------------------
seg_perf = df.groupby("CustomerSegment").agg(
    TotalSales=("NetSales", "sum"),
    Orders=("OrderID", "nunique")
)
seg_perf["AOV"] = seg_perf["TotalSales"] / seg_perf["Orders"]
seg_perf = seg_perf.sort_values("AOV", ascending=False)

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(seg_perf.index, seg_perf["AOV"], color=PALETTE[3])
ax.set_title("Average Order Value by Customer Segment", fontsize=14, weight="bold")
ax.set_ylabel("AOV (₹)")
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2, h + 20, f"₹{h:,.0f}",
            ha="center", color="#E8E8E8", fontsize=10)
fig.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "04_segment_aov.png"), dpi=150)
plt.close(fig)

# ---------------------------------------------------------------
# 7. Chart 5 — Bottom 25% "low-performing products" by profit
# ---------------------------------------------------------------
product_perf = df.groupby("ProductName")["Profit"].sum().sort_values()
low_performers = product_perf[product_perf <= product_perf.quantile(0.25)]

fig, ax = plt.subplots(figsize=(9, 6))
ax.barh(low_performers.index, low_performers.values, color=PALETTE[1])
ax.set_title("Bottom 25% Products by Total Profit", fontsize=14, weight="bold")
ax.set_xlabel("Total Profit (₹)")
fig.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "05_low_performing_products.png"), dpi=150)
plt.close(fig)

print(f"\nSaved 5 dashboard charts to: {IMG_DIR}")
print("Low-performing products (bottom 25% by profit):")
print(low_performers.round(0))

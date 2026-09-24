# Power BI Dashboard — Build Guide

This project's Power BI dashboard is built on top of `sales_clean` (from
`sql/02_data_cleaning.sql`) or directly on `data/sales_data.csv`. A `.pbix`
file is a binary Power BI file, so it isn't something that can be generated
by a script — this guide gives the exact steps and DAX so the dashboard
can be rebuilt in Power BI Desktop in about 20 minutes and saved as
`SalesInsights.pbix` for the repo.

## 1. Get Data
`Home → Get Data → SQL Server` (point to `sales_insights.sales_clean`)
**or** `Get Data → Text/CSV` → select `data/sales_data.csv`.

## 2. Data Model
Single flat table is fine for this dataset size. Optionally split into:
- `FactSales` (OrderID, CustomerID, ProductName, OrderDate, NetSales, Profit, Quantity …)
- `DimDate` (auto date table, or `CALENDAR(MIN(FactSales[OrderDate]), MAX(FactSales[OrderDate]))`)
- `DimProduct` (ProductName, Category)
- `DimCustomer` (CustomerID, CustomerSegment, Region)

Mark `DimDate` as a Date Table (`Table tools → Mark as Date Table`).

## 3. DAX Measures
```DAX
Total Sales = SUM(FactSales[NetSales])

Total Profit = SUM(FactSales[Profit])

Total Orders = DISTINCTCOUNT(FactSales[OrderID])

AOV = DIVIDE([Total Sales], [Total Orders])

Profit Margin % = DIVIDE([Total Profit], [Total Sales])

Sales LM =
CALCULATE([Total Sales], DATEADD(DimDate[Date], -1, MONTH))

Sales Growth % = DIVIDE([Total Sales] - [Sales LM], [Sales LM])

YTD Sales = TOTALYTD([Total Sales], DimDate[Date])
```

## 4. Calculated Column (low performers flag)
```DAX
ProductProfitRank =
RANKX(ALL(FactSales[ProductName]), CALCULATE([Total Profit]), , ASC)
```

## 5. Report Pages
1. **Overview** — KPI cards (Total Sales, Total Profit, Total Orders, AOV, Growth %),
   monthly trend line chart, region map/bar chart.
2. **Product Performance** — table with `ProductProfitRank`, bar chart of bottom 25%
   products, category donut chart.
3. **Customer Insights** — segment breakdown, top 10 customers table, AOV by segment.

## 6. Drill-through
Right-click a Region bar → `Add drill-through` → target page "Product Performance",
filtered by Region, so a viewer can click South → see South's product breakdown.

## 7. Save & Export
`File → Save As → SalesInsights.pbix` and place it in this `powerbi_notes/` folder
(or a top-level `powerbi/` folder) before pushing to GitHub. GitHub won't render the
`.pbix` file inline — that's normal; that's exactly why the `images/` folder in this
repo holds exported PNG screenshots of every page, so the dashboard is visible directly
on the GitHub README even for people without Power BI installed.

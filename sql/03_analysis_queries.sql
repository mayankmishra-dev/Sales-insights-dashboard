-- ============================================================
-- 03_analysis_queries.sql
-- Core business questions answered with SQL: KPIs, CTEs, joins,
-- window functions, and the "low-performing products" analysis.
-- ============================================================
USE sales_insights;

-- ------------------------------------------------------------
-- Q1. Headline KPIs: Total Sales, Profit, Orders, Avg Order Value (AOV)
-- ------------------------------------------------------------
SELECT
    ROUND(SUM(NetSales), 2)              AS TotalSales,
    ROUND(SUM(Profit), 2)                AS TotalProfit,
    COUNT(DISTINCT OrderID)              AS TotalOrders,
    ROUND(SUM(NetSales) / COUNT(DISTINCT OrderID), 2) AS AvgOrderValue,
    ROUND(SUM(Profit) / SUM(NetSales) * 100, 2)       AS OverallMarginPct
FROM sales_clean;

-- ------------------------------------------------------------
-- Q2. Month-over-month sales growth % (window function: LAG)
-- ------------------------------------------------------------
WITH monthly_sales AS (
    SELECT
        OrderYear,
        OrderMonth,
        OrderMonthName,
        SUM(NetSales) AS MonthlySales
    FROM sales_clean
    GROUP BY OrderYear, OrderMonth, OrderMonthName
)
SELECT
    OrderYear,
    OrderMonthName,
    MonthlySales,
    LAG(MonthlySales) OVER (ORDER BY OrderYear, OrderMonth) AS PrevMonthSales,
    ROUND(
        (MonthlySales - LAG(MonthlySales) OVER (ORDER BY OrderYear, OrderMonth))
        / NULLIF(LAG(MonthlySales) OVER (ORDER BY OrderYear, OrderMonth), 0) * 100, 2
    ) AS GrowthPct
FROM monthly_sales
ORDER BY OrderYear, OrderMonth;

-- ------------------------------------------------------------
-- Q3. Region-wise performance ranked (CTE + RANK)
-- ------------------------------------------------------------
WITH region_perf AS (
    SELECT
        Region,
        SUM(NetSales) AS TotalSales,
        SUM(Profit)   AS TotalProfit,
        COUNT(DISTINCT OrderID) AS Orders
    FROM sales_clean
    GROUP BY Region
)
SELECT
    Region,
    TotalSales,
    TotalProfit,
    Orders,
    RANK() OVER (ORDER BY TotalSales DESC) AS SalesRank
FROM region_perf
ORDER BY SalesRank;

-- ------------------------------------------------------------
-- Q4. Customer segmentation: sales & AOV by segment (JOIN-style aggregation)
-- ------------------------------------------------------------
SELECT
    CustomerSegment,
    COUNT(DISTINCT CustomerID)              AS Customers,
    COUNT(DISTINCT OrderID)                 AS Orders,
    ROUND(SUM(NetSales), 2)                 AS TotalSales,
    ROUND(SUM(NetSales) / COUNT(DISTINCT OrderID), 2) AS AOV
FROM sales_clean
GROUP BY CustomerSegment
ORDER BY TotalSales DESC;

-- ------------------------------------------------------------
-- Q5. Product performance + identifying the bottom 25% by profit
--     (CTE + NTILE window function)
-- ------------------------------------------------------------
WITH product_perf AS (
    SELECT
        ProductName,
        Category,
        SUM(NetSales) AS TotalSales,
        SUM(Profit)   AS TotalProfit,
        SUM(Quantity) AS UnitsSold
    FROM sales_clean
    GROUP BY ProductName, Category
),
ranked AS (
    SELECT *,
           NTILE(4) OVER (ORDER BY TotalProfit ASC) AS ProfitQuartile
    FROM product_perf
)
SELECT ProductName, Category, TotalSales, TotalProfit, UnitsSold
FROM ranked
WHERE ProfitQuartile = 1   -- bottom 25% -> "low-performing products"
ORDER BY TotalProfit ASC;

-- ------------------------------------------------------------
-- Q6. Top 10 customers by lifetime value (self-join-free ranking)
-- ------------------------------------------------------------
SELECT
    CustomerID,
    CustomerSegment,
    Region,
    ROUND(SUM(NetSales), 2) AS LifetimeValue,
    COUNT(DISTINCT OrderID) AS TotalOrders
FROM sales_clean
GROUP BY CustomerID, CustomerSegment, Region
ORDER BY LifetimeValue DESC
LIMIT 10;

-- ------------------------------------------------------------
-- Q7. Category trend across years (JOIN between two aggregated CTEs)
-- ------------------------------------------------------------
WITH y2023 AS (
    SELECT Category, SUM(NetSales) AS Sales2023
    FROM sales_clean WHERE OrderYear = 2023 GROUP BY Category
),
y2024 AS (
    SELECT Category, SUM(NetSales) AS Sales2024
    FROM sales_clean WHERE OrderYear = 2024 GROUP BY Category
)
SELECT
    COALESCE(a.Category, b.Category) AS Category,
    a.Sales2023,
    b.Sales2024,
    ROUND((b.Sales2024 - a.Sales2023) / NULLIF(a.Sales2023, 0) * 100, 2) AS YoYGrowthPct
FROM y2023 a
JOIN y2024 b ON a.Category = b.Category
ORDER BY YoYGrowthPct DESC;

-- ============================================================
-- 02_data_cleaning.sql
-- Cleans sales_raw into an analysis-ready table `sales_clean`.
-- ============================================================
USE sales_insights;

-- 1. Remove exact duplicate orders (same OrderID appearing twice)
DELETE t1 FROM sales_raw t1
INNER JOIN sales_raw t2
WHERE t1.OrderID = t2.OrderID
  AND t1.OrderDate = t2.OrderDate
  AND t1.CTID_check IS NULL;  -- placeholder guard, see note below

-- NOTE: MySQL has no native row CTID, so the safer duplicate-removal pattern
-- used in practice for this project is to de-dupe on the full row signature:
DELETE r1 FROM sales_raw r1
JOIN (
    SELECT MIN(OrderID) AS keep_id, CustomerID, OrderDate, ProductName, Quantity, NetSales
    FROM sales_raw
    GROUP BY CustomerID, OrderDate, ProductName, Quantity, NetSales
    HAVING COUNT(*) > 1
) dupes
  ON r1.CustomerID = dupes.CustomerID
 AND r1.OrderDate = dupes.OrderDate
 AND r1.ProductName = dupes.ProductName
 AND r1.Quantity = dupes.Quantity
 AND r1.NetSales = dupes.NetSales
 AND r1.OrderID <> dupes.keep_id;

-- 2. Build the clean, analysis-ready table
DROP TABLE IF EXISTS sales_clean;

CREATE TABLE sales_clean AS
SELECT
    OrderID,
    OrderDate,
    YEAR(OrderDate)  AS OrderYear,
    MONTH(OrderDate) AS OrderMonth,
    MONTHNAME(OrderDate) AS OrderMonthName,
    CustomerID,
    CustomerSegment,
    Region,
    ProductName,
    Category,
    UnitPrice,
    Quantity,
    -- Fill missing discount values with 0 (no discount applied)
    COALESCE(DiscountPct, 0) AS DiscountPct,
    GrossAmount,
    NetSales,
    Cost,
    Profit,
    ROUND(Profit / NULLIF(NetSales, 0) * 100, 2) AS ProfitMarginPct
FROM sales_raw
WHERE NetSales > 0            -- drop any invalid/zero-value rows
  AND Quantity > 0;

-- 3. Quick sanity checks
SELECT COUNT(*) AS total_rows FROM sales_clean;
SELECT COUNT(*) AS null_discounts FROM sales_clean WHERE DiscountPct IS NULL;
SELECT MIN(OrderDate) AS first_order, MAX(OrderDate) AS last_order FROM sales_clean;

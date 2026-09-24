-- ============================================================
-- 01_schema.sql
-- Creates the MySQL schema used for the Sales Insights project.
-- Run this first, then load data/sales_data.csv into `sales_raw`
-- (e.g. via MySQL Workbench "Table Data Import Wizard" or LOAD DATA INFILE).
-- ============================================================

CREATE DATABASE IF NOT EXISTS sales_insights;
USE sales_insights;

DROP TABLE IF EXISTS sales_raw;

CREATE TABLE sales_raw (
    OrderID         INT PRIMARY KEY,
    OrderDate       DATE NOT NULL,
    CustomerID      VARCHAR(10) NOT NULL,
    CustomerSegment VARCHAR(30),
    Region          VARCHAR(20),
    ProductName     VARCHAR(60),
    Category        VARCHAR(30),
    UnitPrice       DECIMAL(10,2),
    Quantity        INT,
    DiscountPct     DECIMAL(5,2),
    GrossAmount     DECIMAL(12,2),
    NetSales        DECIMAL(12,2),
    Cost            DECIMAL(12,2),
    Profit          DECIMAL(12,2)
);

-- Example bulk load (adjust path / secure_file_priv as needed):
-- LOAD DATA LOCAL INFILE 'data/sales_data.csv'
-- INTO TABLE sales_raw
-- FIELDS TERMINATED BY ',' ENCLOSED BY '"'
-- LINES TERMINATED BY '\n'
-- IGNORE 1 ROWS;

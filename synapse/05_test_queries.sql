-- Run these while connected to SalesMedallion.

SELECT TOP 10 * FROM gold.fact_sales;
SELECT TOP 10 * FROM gold.dim_customer;
SELECT TOP 10 * FROM gold.dim_product;
SELECT TOP 10 * FROM gold.dim_store;
SELECT TOP 10 * FROM gold.dim_date;

SELECT COUNT(*) AS FactRows
FROM gold.fact_sales;

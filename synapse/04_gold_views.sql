-- Run this while connected to SalesMedallion.
-- These are logical SQL views over the Gold Delta files in ADLS.

IF NOT EXISTS
(
    SELECT 1
    FROM sys.schemas
    WHERE name = 'gold'
)
BEGIN
    EXEC('CREATE SCHEMA gold');
END;
GO

CREATE OR ALTER VIEW gold.fact_sales
AS
SELECT *
FROM OPENROWSET
(
    BULK 'gold/fact_sales',
    DATA_SOURCE = 'SalesLake',
    FORMAT = 'DELTA'
) AS rows;
GO

CREATE OR ALTER VIEW gold.dim_customer
AS
SELECT *
FROM OPENROWSET
(
    BULK 'gold/dim_customer',
    DATA_SOURCE = 'SalesLake',
    FORMAT = 'DELTA'
) AS rows;
GO

CREATE OR ALTER VIEW gold.dim_product
AS
SELECT *
FROM OPENROWSET
(
    BULK 'gold/dim_product',
    DATA_SOURCE = 'SalesLake',
    FORMAT = 'DELTA'
) AS rows;
GO

CREATE OR ALTER VIEW gold.dim_store
AS
SELECT *
FROM OPENROWSET
(
    BULK 'gold/dim_store',
    DATA_SOURCE = 'SalesLake',
    FORMAT = 'DELTA'
) AS rows;
GO

CREATE OR ALTER VIEW gold.dim_date
AS
SELECT *
FROM OPENROWSET
(
    BULK 'gold/dim_date',
    DATA_SOURCE = 'SalesLake',
    FORMAT = 'DELTA'
) AS rows;
GO

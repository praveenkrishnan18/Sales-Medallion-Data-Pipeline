-- Run this while connected to SalesMedallion.
-- Replace <STORAGE_ACCOUNT> with the actual ADLS Gen2 account name.

IF NOT EXISTS
(
    SELECT 1
    FROM sys.external_data_sources
    WHERE name = 'SalesLake'
)
BEGIN
    CREATE EXTERNAL DATA SOURCE SalesLake
    WITH
    (
        LOCATION = 'https://<STORAGE_ACCOUNT>.dfs.core.windows.net/sales-lake',
        CREDENTIAL = SynapseManagedIdentity
    );
END;
GO

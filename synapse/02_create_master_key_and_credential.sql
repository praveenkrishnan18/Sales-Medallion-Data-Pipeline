-- Run this while connected to SalesMedallion, NOT master.
-- Never commit the real master-key password to source control.

IF NOT EXISTS
(
    SELECT 1
    FROM sys.symmetric_keys
    WHERE name = '##MS_DatabaseMasterKey##'
)
BEGIN
    CREATE MASTER KEY
    ENCRYPTION BY PASSWORD = '<SET_SECURE_MASTER_KEY_PASSWORD_LOCALLY>';
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.database_scoped_credentials
    WHERE name = 'SynapseManagedIdentity'
)
BEGIN
    CREATE DATABASE SCOPED CREDENTIAL SynapseManagedIdentity
    WITH IDENTITY = 'Managed Identity';
END;
GO

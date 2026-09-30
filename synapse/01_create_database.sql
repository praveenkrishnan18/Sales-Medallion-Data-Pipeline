-- Run this in the Synapse Built-in/serverless SQL endpoint.
-- Database creation is run from master.

IF DB_ID(N'SalesMedallion') IS NULL
BEGIN
    CREATE DATABASE SalesMedallion;
END;
GO

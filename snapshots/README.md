# Snapshots

Execution screenshots for the project, in build order.

| # | File | What it shows |
|---|------|---------------|
| 01 | `01_azure_resource_group.png` | Azure resource group with Databricks, Access Connector, and storage account |
| 02 | `02_unity_catalog_storage_credential.png` | Unity Catalog storage credential (managed identity) |
| 03 | `03_unity_catalog_external_location.png` | External location `ext_sales_lake` |
| 04 | `04_azure_role_assignment_access_connector.png` | Storage Blob Data Contributor role for the Access Connector |
| 05 | `05_external_location_grants.png` | Grants on the external location |
| 06 | `06_notebook_ingest_raw.png` | `01_ingest_raw.py` run, files landed in `raw/` |
| 07 | `07_notebook_bronze.png` | `02_bronze.py` run, Bronze Delta tables written |
| 08 | `08_notebook_silver.png` | `03_silver.py` run, Silver customers output |
| 09 | `09_notebook_gold.png` | `04_gold.py` run, five Gold tables listed |
| 10 | `10_synapse_workspace_creation.png` | Synapse workspace creation |
| 11 | `11_synapse_openrowset_fact_sales.png` | `OPENROWSET` query over Gold `fact_sales` |
| 12 | `12_synapse_gold_views_validation.png` | Gold views validated in `SalesMedallion` |
| 13 | `13_databricks_job_running.png` | Databricks job running |
| 14 | `14_databricks_job_succeeded.png` | Databricks job succeeded |

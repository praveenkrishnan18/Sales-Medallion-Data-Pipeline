# Project boundaries

## Included

- GitHub source-data ingestion
- Databricks serverless Job
- PySpark processing
- ADLS Gen2
- Delta Lake
- Unity Catalog
- Bronze/Silver/Gold medallion layers
- Gold dimensional model
- SCD Type 2 customer dimension
- Synapse Serverless SQL access layer
- Declarative Automation Bundle
- Azure DevOps CI/CD template

## Intentionally not included

- Azure Data Factory orchestration
- Dedicated Synapse SQL pool
- Power BI/reporting layer
- Kafka/streaming
- Airflow
- Snowflake
- ML/GenAI

ADF was tested during development but removed from the final design because the Databricks Job already owns the end-to-end workflow.

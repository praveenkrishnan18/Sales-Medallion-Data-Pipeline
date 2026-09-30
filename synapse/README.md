# Synapse Serverless Layer

Synapse Serverless is used as a SQL access layer over the Gold Delta data stored in ADLS Gen2.

It does not copy the Gold data into a separate warehouse.

Order of execution:

1. `01_create_database.sql` from `master`.
2. Open a new SQL script connected to `SalesMedallion`.
3. Run `02_create_master_key_and_credential.sql` with a locally supplied password.
4. Replace `<STORAGE_ACCOUNT>` and run `03_create_external_data_source.sql`.
5. Run `04_gold_views.sql`.
6. Run `05_test_queries.sql`.

Never commit the real master-key password, tokens, or credentials.

## Screenshots

Synapse workspace creation:

![Synapse workspace creation](../snapshots/10_synapse_workspace_creation.png)

Direct `OPENROWSET` read of the Gold `fact_sales` Delta folder:

![OPENROWSET query on fact_sales](../snapshots/11_synapse_openrowset_fact_sales.png)

Validation of the `gold` schema and views in `SalesMedallion`:

![Synapse Gold views validation](../snapshots/12_synapse_gold_views_validation.png)

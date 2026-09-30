# CI/CD

The Databricks portion is source-controlled with a Declarative Automation Bundle.

## Local lifecycle

```bash
databricks bundle validate -t dev
databricks bundle deploy -t dev
databricks bundle run -t dev sales_medallion_pipeline
```

## Azure DevOps

`azure-pipelines.yml` validates and deploys the Databricks bundle on pushes to `main`.

Create these Azure DevOps variables:

- `DATABRICKS_HOST` — workspace URL
- `DATABRICKS_CLIENT_ID` — service principal OAuth client ID
- `DATABRICKS_CLIENT_SECRET` — secret variable

Do not commit the client secret to the repository. Map secret variables into the script environment only.

For production, use a service principal and a production target rather than deploying the development target directly.

## Job run evidence

Successful end-to-end run of the four-task Databricks job:

![Databricks job succeeded](../snapshots/14_databricks_job_succeeded.png)

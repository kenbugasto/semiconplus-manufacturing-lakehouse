# Shutdown and Cleanup

## After every development session

1. Terminate all-purpose Databricks compute.
2. Stop SQL warehouses.
3. Confirm no Databricks jobs or pipelines are running.
4. Confirm no continuous streaming query remains active.
5. Review Azure Cost Analysis after billing data updates.

## Temporary resources

- Pause or remove the temporary Azure SQL database after JDBC testing.
- Use triggered streaming rather than continuously running streams.
- Remove temporary test outputs when no longer required.

## Budget enforcement

- Absolute Azure budget: USD 100
- Operational stop: USD 80
- Protected billing-delay reserve: USD 20
- Remove optional paid work when spending reaches USD 70.

## Protected resources

Do not directly modify Unity Catalog-managed files or resources inside the Azure Databricks-managed resource group.
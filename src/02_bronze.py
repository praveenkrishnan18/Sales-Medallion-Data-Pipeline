# Databricks notebook source

from pyspark.sql import functions as F

# ============================================================
# Configuration
# ============================================================

STORAGE_ACCOUNT = "<YOUR_STORAGE_ACCOUNT_NAME>"

BASE_PATH = (
    f"abfss://sales-lake@"
    f"{STORAGE_ACCOUNT}.dfs.core.windows.net"
)

RAW_PATH = f"{BASE_PATH}/raw"
BRONZE_PATH = f"{BASE_PATH}/bronze"


# ============================================================
# Helper
# ============================================================

def add_ingestion_metadata(df):
    return (
        df
        .withColumn("_source_file", F.col("_metadata.file_path"))
        .withColumn("_ingest_timestamp", F.current_timestamp())
    )


# ============================================================
# Customers
# ============================================================

customers_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{RAW_PATH}/customers/customers_*.csv")
)
customers_df = add_ingestion_metadata(customers_df)

(
    customers_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", f"{BRONZE_PATH}/customers")
    .saveAsTable("sales_catalog.bronze.customers")
)


# ============================================================
# Products
# ============================================================

products_df = (
    spark.read
    .option("multiLine", "true")
    .json(f"{RAW_PATH}/products/products.json")
)
products_df = add_ingestion_metadata(products_df)

(
    products_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", f"{BRONZE_PATH}/products")
    .saveAsTable("sales_catalog.bronze.products")
)


# ============================================================
# Stores
# ============================================================

stores_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{RAW_PATH}/stores/stores.csv")
)
stores_df = add_ingestion_metadata(stores_df)

(
    stores_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", f"{BRONZE_PATH}/stores")
    .saveAsTable("sales_catalog.bronze.stores")
)


# ============================================================
# Orders
# ============================================================

orders_df = (
    spark.read
    .option("header", "true")
    .option("inferSchema", "true")
    .csv(f"{RAW_PATH}/orders/orders_*.csv")
)
orders_df = add_ingestion_metadata(orders_df)

(
    orders_df.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", f"{BRONZE_PATH}/orders")
    .saveAsTable("sales_catalog.bronze.orders")
)

print("BRONZE INGESTION COMPLETED")

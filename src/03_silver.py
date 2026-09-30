# Databricks notebook source

from pyspark.sql import functions as F
from pyspark.sql.window import Window

# ============================================================
# Configuration
# ============================================================

STORAGE_ACCOUNT = "<YOUR_STORAGE_ACCOUNT_NAME>"

BASE_PATH = (
    f"abfss://sales-lake@"
    f"{STORAGE_ACCOUNT}.dfs.core.windows.net"
)

SILVER_PATH = f"{BASE_PATH}/silver"


# ============================================================
# Customers - clean + keep latest current state
# SCD Type 2 is intentionally handled in Gold.
# ============================================================

customers = spark.table("sales_catalog.bronze.customers")

customers_clean = (
    customers
    .withColumn("CustomerID", F.col("CustomerID").cast("int"))
    .withColumn("CustomerName", F.trim(F.col("CustomerName")))
    .withColumn("Email", F.lower(F.trim(F.col("Email"))))
    .withColumn("City", F.initcap(F.trim(F.col("City"))))
    .withColumn("State", F.initcap(F.trim(F.col("State"))))
    .withColumn("SignupDate", F.to_timestamp("SignupDate"))
    .withColumn("UpdatedDate", F.to_timestamp("UpdatedDate"))
)

customer_window = Window.partitionBy("CustomerID").orderBy(
    F.col("UpdatedDate").desc()
)

customers_silver = (
    customers_clean
    .withColumn("_rn", F.row_number().over(customer_window))
    .filter(F.col("_rn") == 1)
    .drop("_rn")
)

(
    customers_silver.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", f"{SILVER_PATH}/customers")
    .saveAsTable("sales_catalog.silver.customers")
)


# ============================================================
# Products
# ============================================================

products = spark.table("sales_catalog.bronze.products")

products_clean = (
    products
    .withColumn("ProductID", F.col("ProductID").cast("int"))
    .withColumn("ProductName", F.trim(F.col("ProductName")))
    .withColumn("Category", F.initcap(F.trim(F.col("Category"))))
    .withColumn("SubCategory", F.initcap(F.trim(F.col("SubCategory"))))
    .withColumn("Price", F.col("Price").cast("decimal(12,2)"))
    .withColumn("SupplierID", F.col("SupplierID").cast("int"))
    .withColumn("UpdatedDate", F.to_timestamp("UpdatedDate"))
    .filter(F.col("Price") > 0)
)

product_window = Window.partitionBy("ProductID").orderBy(
    F.col("UpdatedDate").desc()
)

products_silver = (
    products_clean
    .withColumn("_rn", F.row_number().over(product_window))
    .filter(F.col("_rn") == 1)
    .drop("_rn")
)

(
    products_silver.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", f"{SILVER_PATH}/products")
    .saveAsTable("sales_catalog.silver.products")
)


# ============================================================
# Stores
# ============================================================

stores = spark.table("sales_catalog.bronze.stores")

stores_silver = (
    stores
    .withColumn("StoreID", F.col("StoreID").cast("int"))
    .withColumn("StoreName", F.trim(F.col("StoreName")))
    .withColumn("City", F.initcap(F.trim(F.col("City"))))
    .withColumn("State", F.initcap(F.trim(F.col("State"))))
    .withColumn("Region", F.initcap(F.trim(F.col("Region"))))
    .dropDuplicates(["StoreID"])
)

(
    stores_silver.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", f"{SILVER_PATH}/stores")
    .saveAsTable("sales_catalog.silver.stores")
)


# ============================================================
# Orders
# ============================================================

orders = spark.table("sales_catalog.bronze.orders")

orders_clean = (
    orders
    .withColumn("OrderID", F.col("OrderID").cast("int"))
    .withColumn("CustomerID", F.col("CustomerID").cast("int"))
    .withColumn("ProductID", F.col("ProductID").cast("int"))
    .withColumn("StoreID", F.col("StoreID").cast("int"))
    .withColumn("OrderDate", F.to_timestamp("OrderDate"))
    .withColumn("Quantity", F.col("Quantity").cast("int"))
    .withColumn("UnitPrice", F.col("UnitPrice").cast("decimal(12,2)"))
    .withColumn("OrderStatus", F.initcap(F.trim(F.col("OrderStatus"))))
    .withColumn("UpdatedDate", F.to_timestamp("UpdatedDate"))
    .withColumn(
        "OrderAmount",
        F.col("Quantity") * F.col("UnitPrice")
    )
)

order_window = Window.partitionBy("OrderID").orderBy(
    F.col("UpdatedDate").desc()
)

orders_silver = (
    orders_clean
    .withColumn("_rn", F.row_number().over(order_window))
    .filter(F.col("_rn") == 1)
    .drop("_rn")
    .filter(F.col("Quantity") > 0)
    .filter(F.col("UnitPrice") > 0)
)

(
    orders_silver.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", f"{SILVER_PATH}/orders")
    .saveAsTable("sales_catalog.silver.orders")
)

print("SILVER LAYER CREATED")

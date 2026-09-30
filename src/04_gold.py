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

GOLD_PATH = f"{BASE_PATH}/gold"


# ============================================================
# Source tables
# ============================================================

customers_bronze = spark.table("sales_catalog.bronze.customers")
products_silver = spark.table("sales_catalog.silver.products")
stores_silver = spark.table("sales_catalog.silver.stores")
orders_silver = spark.table("sales_catalog.silver.orders")


# ============================================================
# 1. DIM_CUSTOMER - SCD Type 2
# ============================================================

customers = (
    customers_bronze
    .withColumn("CustomerID", F.col("CustomerID").cast("int"))
    .withColumn("CustomerName", F.trim(F.col("CustomerName")))
    .withColumn("Email", F.lower(F.trim(F.col("Email"))))
    .withColumn("City", F.initcap(F.trim(F.col("City"))))
    .withColumn("State", F.initcap(F.trim(F.col("State"))))
    .withColumn("SignupDate", F.to_timestamp("SignupDate"))
    .withColumn("UpdatedDate", F.to_timestamp("UpdatedDate"))
    .dropDuplicates(["CustomerID", "UpdatedDate"])
)

customer_window = Window.partitionBy("CustomerID").orderBy("UpdatedDate")

dim_customer = (
    customers
    .withColumn("EffectiveStart", F.col("UpdatedDate"))
    .withColumn("EffectiveEnd", F.lead("UpdatedDate").over(customer_window))
    .withColumn("IsCurrent", F.col("EffectiveEnd").isNull())
    .withColumn(
        "CustomerKey",
        F.sha2(
            F.concat_ws(
                "||",
                F.col("CustomerID").cast("string"),
                F.col("EffectiveStart").cast("string")
            ),
            256
        )
    )
    .select(
        "CustomerKey",
        "CustomerID",
        "CustomerName",
        "Email",
        "City",
        "State",
        "SignupDate",
        "EffectiveStart",
        "EffectiveEnd",
        "IsCurrent"
    )
)

(
    dim_customer.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", f"{GOLD_PATH}/dim_customer")
    .saveAsTable("sales_catalog.gold.dim_customer")
)


# ============================================================
# 2. DIM_PRODUCT
# ============================================================

dim_product = (
    products_silver
    .withColumn(
        "ProductKey",
        F.sha2(F.col("ProductID").cast("string"), 256)
    )
    .select(
        "ProductKey",
        "ProductID",
        "ProductName",
        "Category",
        "SubCategory",
        "Price",
        "SupplierID",
        "UpdatedDate"
    )
)

(
    dim_product.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", f"{GOLD_PATH}/dim_product")
    .saveAsTable("sales_catalog.gold.dim_product")
)


# ============================================================
# 3. DIM_STORE
# ============================================================

dim_store = (
    stores_silver
    .withColumn(
        "StoreKey",
        F.sha2(F.col("StoreID").cast("string"), 256)
    )
    .select(
        "StoreKey",
        "StoreID",
        "StoreName",
        "City",
        "State",
        "Region"
    )
)

(
    dim_store.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", f"{GOLD_PATH}/dim_store")
    .saveAsTable("sales_catalog.gold.dim_store")
)


# ============================================================
# 4. DIM_DATE
# ============================================================

date_bounds = (
    orders_silver
    .select(F.to_date("OrderDate").alias("Date"))
    .filter(F.col("Date").isNotNull())
    .agg(
        F.min("Date").alias("MinDate"),
        F.max("Date").alias("MaxDate")
    )
    .collect()[0]
)

min_date = date_bounds["MinDate"]
max_date = date_bounds["MaxDate"]

date_df = spark.sql(
    f"""
    SELECT explode(
        sequence(
            to_date('{min_date}'),
            to_date('{max_date}'),
            interval 1 day
        )
    ) AS FullDate
    """
)

dim_date = (
    date_df
    .withColumn("DateKey", F.date_format("FullDate", "yyyyMMdd").cast("int"))
    .withColumn("Year", F.year("FullDate"))
    .withColumn("Quarter", F.quarter("FullDate"))
    .withColumn("Month", F.month("FullDate"))
    .withColumn("MonthName", F.date_format("FullDate", "MMMM"))
    .withColumn("Week", F.weekofyear("FullDate"))
    .withColumn("Day", F.dayofmonth("FullDate"))
    .withColumn("DayName", F.date_format("FullDate", "EEEE"))
    .select(
        "DateKey",
        "FullDate",
        "Year",
        "Quarter",
        "Month",
        "MonthName",
        "Week",
        "Day",
        "DayName"
    )
)

(
    dim_date.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", f"{GOLD_PATH}/dim_date")
    .saveAsTable("sales_catalog.gold.dim_date")
)


# ============================================================
# 5. FACT_SALES
# Grain: one order-line/product row.
# ============================================================

orders = orders_silver.withColumn(
    "OrderDateOnly",
    F.to_date("OrderDate")
)

fact = (
    orders.alias("o")
    .join(
        dim_customer.alias("c"),
        (
            (F.col("o.CustomerID") == F.col("c.CustomerID")) &
            (F.col("o.OrderDate") >= F.col("c.EffectiveStart")) &
            (
                F.col("c.EffectiveEnd").isNull() |
                (F.col("o.OrderDate") < F.col("c.EffectiveEnd"))
            )
        ),
        "left"
    )
    .join(
        dim_product.alias("p"),
        F.col("o.ProductID") == F.col("p.ProductID"),
        "left"
    )
    .join(
        dim_store.alias("s"),
        F.col("o.StoreID") == F.col("s.StoreID"),
        "left"
    )
    .join(
        dim_date.alias("d"),
        F.col("o.OrderDateOnly") == F.col("d.FullDate"),
        "left"
    )
    .withColumn(
        "SalesKey",
        F.sha2(
            F.concat_ws(
                "||",
                F.col("o.OrderID").cast("string"),
                F.col("o.ProductID").cast("string")
            ),
            256
        )
    )
    .withColumn(
        "SalesAmount",
        F.col("o.Quantity") * F.col("o.UnitPrice")
    )
    .select(
        "SalesKey",
        F.col("o.OrderID").alias("OrderID"),
        F.col("c.CustomerKey").alias("CustomerKey"),
        F.col("p.ProductKey").alias("ProductKey"),
        F.col("s.StoreKey").alias("StoreKey"),
        F.col("d.DateKey").alias("DateKey"),
        F.col("o.Quantity").alias("Quantity"),
        F.col("o.UnitPrice").alias("UnitPrice"),
        F.col("SalesAmount").alias("SalesAmount"),
        F.col("o.OrderStatus").alias("OrderStatus")
    )
)

(
    fact.write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .option("path", f"{GOLD_PATH}/fact_sales")
    .saveAsTable("sales_catalog.gold.fact_sales")
)

print("GOLD STAR SCHEMA CREATED")

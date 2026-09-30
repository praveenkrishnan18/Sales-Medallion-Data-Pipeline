from pathlib import Path
from datetime import datetime, timedelta
import csv
import json
import random
from faker import Faker

fake = Faker()
random.seed(42)

OUTPUT_DIR = Path("sales-data-source")
DIRS = {
    "customers": OUTPUT_DIR / "customers",
    "products": OUTPUT_DIR / "products",
    "stores": OUTPUT_DIR / "stores",
    "orders": OUTPUT_DIR / "orders",
}

for p in DIRS.values():
    p.mkdir(parents=True, exist_ok=True)

CITIES = ["Chennai","Bengaluru","Hyderabad","Mumbai","Pune","Delhi","Kochi","Coimbatore","Madurai","Trichy"]
STATES = ["Tamil Nadu","Karnataka","Telangana","Maharashtra","Delhi","Kerala"]
REGIONS = ["South","West","North","Central"]
CATEGORIES = ["Electronics","Home","Clothing","Sports","Books","Grocery"]
SUBCATEGORIES = ["Mobile","Laptop","Audio","Kitchen","Furniture","Men","Women","Fitness","Books","Food"]
ORDER_STATUSES = ["Pending","Confirmed","Shipped","Delivered","Cancelled"]
BASE_DATE = datetime(2026, 1, 1)

def dt(dt_value):
    return dt_value.strftime("%Y-%m-%d %H:%M:%S")

def random_date(start, days):
    return start + timedelta(days=random.randint(0, days), seconds=random.randint(0, 86399))

def write_csv(path, headers, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    print(f"Created {path} -> {len(rows):,} rows")

# ---------------- CUSTOMERS ----------------
customer_headers = ["CustomerID","CustomerName","Email","City","State","SignupDate","UpdatedDate"]
customers = []
customer_lookup = {}

for cid in range(1, 5001):
    signup = random_date(BASE_DATE - timedelta(days=700), 500)
    row = [cid, fake.name(), f"customer{cid}@example.com",
           random.choice(CITIES), random.choice(STATES),
           dt(signup), dt(signup)]
    customers.append(row)
    customer_lookup[cid] = row

write_csv(DIRS["customers"] / "customers_001.csv", customer_headers, customers)

customer_changes = []
change_time = datetime(2026, 9, 1, 10, 0, 0)
update_ids = random.sample(range(1, 5001), 300)

for i, cid in enumerate(update_ids):
    old = customer_lookup[cid]
    customer_changes.append([
        cid, old[1], old[2], random.choice(CITIES), random.choice(STATES),
        old[5], dt(change_time + timedelta(minutes=i))
    ])

for cid in range(5001, 5201):
    signup = change_time + timedelta(minutes=random.randint(0, 2000))
    customer_changes.append([
        cid, fake.name(), f"customer{cid}@example.com",
        random.choice(CITIES), random.choice(STATES),
        dt(signup), dt(signup)
    ])

write_csv(DIRS["customers"] / "customers_002.csv", customer_headers, customer_changes)

# ---------------- PRODUCTS JSON ----------------
products = []
for pid in range(1, 1001):
    updated = BASE_DATE + timedelta(days=random.randint(0, 240))
    products.append({
        "ProductID": pid,
        "ProductName": f"{fake.word().title()} {random.choice(['Phone','Laptop','Chair','Shoes','Book','Speaker'])}",
        "Category": random.choice(CATEGORIES),
        "SubCategory": random.choice(SUBCATEGORIES),
        "Price": round(random.uniform(100, 50000), 2),
        "SupplierID": random.randint(100, 250),
        "UpdatedDate": dt(updated)
    })

with open(DIRS["products"] / "products.json", "w", encoding="utf-8") as f:
    json.dump(products, f, indent=2)
print(f"Created {DIRS['products'] / 'products.json'} -> {len(products):,} records")

# ---------------- STORES ----------------
store_headers = ["StoreID","StoreName","City","State","Region"]
stores = []
for sid in range(1, 101):
    stores.append([
        sid,
        f"{fake.company()} Store",
        random.choice(CITIES),
        random.choice(STATES),
        random.choice(REGIONS)
    ])
write_csv(DIRS["stores"] / "stores.csv", store_headers, stores)

# ---------------- ORDERS ----------------
order_headers = ["OrderID","CustomerID","ProductID","StoreID","OrderDate","Quantity","UnitPrice","OrderStatus","UpdatedDate"]
orders = []
order_lookup = {}

for oid in range(1, 20001):
    order_date = random_date(BASE_DATE, 240)
    pid = random.randint(1, 1000)
    qty = random.randint(1, 5)
    price = products[pid - 1]["Price"]
    row = [
        oid,
        random.randint(1, 5000),
        pid,
        random.randint(1, 100),
        dt(order_date),
        qty,
        price,
        random.choice(ORDER_STATUSES),
        dt(order_date)
    ]
    orders.append(row)
    order_lookup[oid] = row

write_csv(DIRS["orders"] / "orders_001.csv", order_headers, orders)

order_changes = []
order_change_time = datetime(2026, 9, 5, 9, 0, 0)
order_update_ids = random.sample(range(1, 20001), 1000)

for i, oid in enumerate(order_update_ids):
    old = order_lookup[oid]
    order_changes.append([
        oid, old[1], old[2], old[3], old[4],
        random.randint(1, 5), old[6],
        random.choice(ORDER_STATUSES),
        dt(order_change_time + timedelta(minutes=i))
    ])

for oid in range(20001, 21001):
    order_date = order_change_time + timedelta(minutes=random.randint(0, 3000))
    pid = random.randint(1, 1000)
    qty = random.randint(1, 5)
    price = products[pid - 1]["Price"]
    order_changes.append([
        oid,
        random.randint(1, 5200),
        pid,
        random.randint(1, 100),
        dt(order_date),
        qty,
        price,
        random.choice(ORDER_STATUSES),
        dt(order_date)
    ])

write_csv(DIRS["orders"] / "orders_002.csv", order_headers, order_changes)

print("\nDATA GENERATION COMPLETE")
print(f"Output folder: {OUTPUT_DIR.resolve()}")

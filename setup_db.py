"""
Creates and populates the business SQLite database with realistic sample data.
Run this once before running analysis.py.
"""
import sqlite3
import random
from datetime import datetime, timedelta

random.seed(42)

conn = sqlite3.connect("business.db")
cur = conn.cursor()

# ── Schema ─────────────────────────────────────────────────────────────────
cur.executescript("""
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS order_items;

CREATE TABLE customers (
    customer_id   INTEGER PRIMARY KEY,
    name          TEXT,
    email         TEXT,
    region        TEXT,
    segment       TEXT,
    joined_date   TEXT
);

CREATE TABLE products (
    product_id    INTEGER PRIMARY KEY,
    name          TEXT,
    category      TEXT,
    unit_price    REAL,
    unit_cost     REAL
);

CREATE TABLE orders (
    order_id      INTEGER PRIMARY KEY,
    customer_id   INTEGER REFERENCES customers(customer_id),
    order_date    TEXT,
    status        TEXT
);

CREATE TABLE order_items (
    item_id       INTEGER PRIMARY KEY,
    order_id      INTEGER REFERENCES orders(order_id),
    product_id    INTEGER REFERENCES products(product_id),
    quantity      INTEGER,
    discount      REAL
);
""")

# ── Customers ──────────────────────────────────────────────────────────────
first = ["James","Sarah","Michael","Emily","David","Jessica","Daniel","Ashley",
         "Chris","Amanda","Matthew","Stephanie","Andrew","Jennifer","Joshua","Megan",
         "Ryan","Lauren","Kevin","Rachel","Brandon","Hannah","Tyler","Brittany","Justin"]
last  = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis",
         "Wilson","Taylor","Anderson","Thomas","Jackson","White","Harris","Martin",
         "Thompson","Robinson","Clark","Lewis","Lee","Walker","Hall","Allen","Young"]
regions   = ["Ontario","British Columbia","Quebec","Alberta","Manitoba"]
segments  = ["Consumer","Corporate","Small Business"]

customers = []
for i in range(1, 301):
    name = f"{random.choice(first)} {random.choice(last)}"
    email = name.lower().replace(" ", ".") + f"{i}@email.com"
    joined = (datetime(2020,1,1) + timedelta(days=random.randint(0,1000))).strftime("%Y-%m-%d")
    customers.append((i, name, email,
                      random.choices(regions, weights=[40,20,20,12,8])[0],
                      random.choices(segments, weights=[55,30,15])[0],
                      joined))
cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?)", customers)

# ── Products ───────────────────────────────────────────────────────────────
product_data = [
    ("Laptop Pro 15",       "Technology",      1299.99, 820.00),
    ("Wireless Mouse",      "Technology",        29.99,  12.00),
    ("USB-C Hub",           "Technology",        49.99,  22.00),
    ("4K Monitor",          "Technology",       449.99, 280.00),
    ("Mechanical Keyboard", "Technology",        89.99,  45.00),
    ("Webcam HD",           "Technology",        79.99,  38.00),
    ("Office Chair",        "Furniture",        349.99, 190.00),
    ("Standing Desk",       "Furniture",        599.99, 340.00),
    ("Bookcase",            "Furniture",        229.99, 130.00),
    ("Filing Cabinet",      "Furniture",        189.99, 100.00),
    ("A4 Paper (500pk)",    "Office Supplies",   12.99,   5.00),
    ("Sticky Notes",        "Office Supplies",    8.99,   2.50),
    ("Ballpoint Pens 12pk", "Office Supplies",    9.99,   3.00),
    ("Binder A4",           "Office Supplies",   14.99,   5.50),
    ("Whiteboard Markers",  "Office Supplies",   11.99,   4.00),
]
cur.executemany("INSERT INTO products VALUES (?,?,?,?,?)",
                [(i+1,)+p for i, p in enumerate(product_data)])

# ── Orders + Items ─────────────────────────────────────────────────────────
order_id = 1
item_id  = 1
orders, items = [], []
start = datetime(2022, 1, 1)

for _ in range(2200):
    cust_id    = random.randint(1, 300)
    order_date = (start + timedelta(days=random.randint(0, 1094))).strftime("%Y-%m-%d")
    status     = random.choices(["Completed","Completed","Completed","Returned","Pending"],
                                 weights=[75,10,5,7,3])[0]
    orders.append((order_id, cust_id, order_date, status))

    num_items = random.choices([1,2,3,4], weights=[50,30,15,5])[0]
    for _ in range(num_items):
        prod_id  = random.randint(1, 15)
        qty      = random.choices([1,2,3,5,10], weights=[50,25,12,8,5])[0]
        discount = random.choices([0,0.05,0.10,0.20], weights=[55,20,15,10])[0]
        items.append((item_id, order_id, prod_id, qty, discount))
        item_id += 1
    order_id += 1

cur.executemany("INSERT INTO orders VALUES (?,?,?,?)", orders)
cur.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", items)

conn.commit()
conn.close()
print(f"Database created: {order_id-1} orders, {item_id-1} items, 300 customers, 15 products")

"""
Business SQL Analysis — runs all queries and prints formatted results.
"""
import sqlite3
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.width", 120)
pd.set_option("display.float_format", "${:,.2f}".format)

conn = sqlite3.connect("business.db")

def run(title, sql):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))

# ── 1. Total Revenue, Profit, Orders ──────────────────────────────────────
run("1. Overall Business Performance", """
SELECT
    COUNT(DISTINCT o.order_id)                                AS total_orders,
    ROUND(SUM(oi.quantity * p.unit_price * (1 - oi.discount)), 2) AS total_revenue,
    ROUND(SUM(oi.quantity * (p.unit_price - p.unit_cost) * (1 - oi.discount)), 2) AS total_profit,
    ROUND(SUM(oi.quantity * (p.unit_price - p.unit_cost) * (1 - oi.discount)) /
          SUM(oi.quantity * p.unit_price * (1 - oi.discount)) * 100, 1) AS profit_margin_pct
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p     ON oi.product_id = p.product_id
WHERE o.status = 'Completed'
""")

# ── 2. Revenue by Category ─────────────────────────────────────────────────
run("2. Revenue & Profit by Product Category", """
SELECT
    p.category,
    COUNT(DISTINCT o.order_id)                                    AS orders,
    ROUND(SUM(oi.quantity * p.unit_price * (1 - oi.discount)), 2) AS revenue,
    ROUND(SUM(oi.quantity * (p.unit_price - p.unit_cost) * (1 - oi.discount)), 2) AS profit,
    ROUND(SUM(oi.quantity * (p.unit_price - p.unit_cost) * (1 - oi.discount)) /
          SUM(oi.quantity * p.unit_price * (1 - oi.discount)) * 100, 1) AS margin_pct
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p     ON oi.product_id = p.product_id
WHERE o.status = 'Completed'
GROUP BY p.category
ORDER BY revenue DESC
""")

# ── 3. Top 10 Customers by Revenue ────────────────────────────────────────
run("3. Top 10 Customers by Revenue", """
SELECT
    c.name,
    c.region,
    c.segment,
    COUNT(DISTINCT o.order_id)                                    AS orders,
    ROUND(SUM(oi.quantity * p.unit_price * (1 - oi.discount)), 2) AS total_spent
FROM customers c
JOIN orders o       ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p     ON oi.product_id = p.product_id
WHERE o.status = 'Completed'
GROUP BY c.customer_id
ORDER BY total_spent DESC
LIMIT 10
""")

# ── 4. Monthly Revenue Trend ───────────────────────────────────────────────
run("4. Monthly Revenue Trend (2022–2024)", """
SELECT
    STRFTIME('%Y-%m', o.order_date)                               AS month,
    COUNT(DISTINCT o.order_id)                                    AS orders,
    ROUND(SUM(oi.quantity * p.unit_price * (1 - oi.discount)), 2) AS revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p     ON oi.product_id = p.product_id
WHERE o.status = 'Completed'
GROUP BY month
ORDER BY month
""")

# ── 5. Revenue by Region & Segment ────────────────────────────────────────
run("5. Revenue by Region & Customer Segment", """
SELECT
    c.region,
    c.segment,
    COUNT(DISTINCT o.order_id)                                    AS orders,
    ROUND(SUM(oi.quantity * p.unit_price * (1 - oi.discount)), 2) AS revenue
FROM customers c
JOIN orders o       ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p     ON oi.product_id = p.product_id
WHERE o.status = 'Completed'
GROUP BY c.region, c.segment
ORDER BY c.region, revenue DESC
""")

# ── 6. Top Products ────────────────────────────────────────────────────────
run("6. Top 10 Products by Revenue", """
SELECT
    p.name,
    p.category,
    SUM(oi.quantity)                                              AS units_sold,
    ROUND(SUM(oi.quantity * p.unit_price * (1 - oi.discount)), 2) AS revenue,
    ROUND(SUM(oi.quantity * (p.unit_price - p.unit_cost) * (1 - oi.discount)), 2) AS profit
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o   ON oi.order_id = o.order_id
WHERE o.status = 'Completed'
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 10
""")

# ── 7. Customer Segmentation by Purchase Frequency ────────────────────────
run("7. Customer Segmentation by Purchase Frequency", """
SELECT
    CASE
        WHEN order_count >= 10 THEN 'High Value (10+ orders)'
        WHEN order_count >= 5  THEN 'Mid Tier (5-9 orders)'
        ELSE                        'Low Frequency (1-4 orders)'
    END AS segment,
    COUNT(*) AS customers,
    ROUND(AVG(total_spent), 2) AS avg_spend
FROM (
    SELECT
        c.customer_id,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(oi.quantity * p.unit_price * (1 - oi.discount)) AS total_spent
    FROM customers c
    JOIN orders o       ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p     ON oi.product_id = p.product_id
    WHERE o.status = 'Completed'
    GROUP BY c.customer_id
)
GROUP BY segment
ORDER BY customers DESC
""")

# ── 8. Return Rate by Category ─────────────────────────────────────────────
run("8. Return Rate by Product Category", """
SELECT
    p.category,
    COUNT(CASE WHEN o.status = 'Completed' THEN 1 END) AS completed,
    COUNT(CASE WHEN o.status = 'Returned'  THEN 1 END) AS returned,
    ROUND(COUNT(CASE WHEN o.status = 'Returned' THEN 1 END) * 100.0 /
          COUNT(*), 1) AS return_rate_pct
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p     ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY return_rate_pct DESC
""")

conn.close()
print("\nAnalysis complete.")

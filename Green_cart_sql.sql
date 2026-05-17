-- ============================================================================
-- PROJECT: Green Cart Ltd. — End-to-End Business Intelligence Project
-- SCRIPT: Data Quality Audit, Integrity Testing, & Advanced Analytical Queries
-- PLATFORM: MySQL
-- AUTHOR: Data Analyst Portfolio Piece
-- ============================================================================

-- STAGE 0: Environment Setup & Data Ingestion Adjustments
SET GLOBAL max_allowed_packet = 67108864;

-- Remove UTF-8 BOM hidden characters from primary key column
-- ALTER TABLE sales_data CHANGE `ï»¿order_id` `order_id` VARCHAR(255);

-- Quick sanity check on ingestion
SELECT * FROM sales_data LIMIT 5;


-- ============================================================================
-- STAGE 1: Volume & Row Count Validation (Auditing Truncation Risks)
-- ============================================================================
SELECT 'customer' AS table_name, COUNT(*) AS total_rows FROM customer_info 
UNION SELECT 'product', COUNT(*) FROM product_info 
UNION SELECT 'sales', COUNT(*) FROM sales_data;

DESCRIBE sales_data;


-- ============================================================================
-- STAGE 2: Completeness Testing (Identifying Nulls & Missing Attributes)
-- ============================================================================

-- 2.1 Customer Profile Integrity Audit
SELECT 
    'customer_info' AS table_audit,
    SUM(CASE WHEN customer_id IS NULL OR customer_id = '' THEN 1 ELSE 0 END) AS missing_id,
    SUM(CASE WHEN email IS NULL OR TRIM(email) = '' THEN 1 ELSE 0 END) AS missing_email,
    SUM(CASE WHEN signup_date IS NULL THEN 1 ELSE 0 END) AS missing_date,
    SUM(CASE WHEN gender IS NULL OR gender = '' THEN 1 ELSE 0 END) AS missing_gender,
    SUM(CASE WHEN region IS NULL OR region = '' THEN 1 ELSE 0 END) AS missing_region,
    SUM(CASE WHEN loyalty_tier IS NULL OR loyalty_tier = '' THEN 1 ELSE 0 END) AS missing_loyalty_tier
FROM customer_info;

-- 2.2 Product Catalog Integrity Audit
SELECT 
    'product_info' AS table_audit,
    SUM(CASE WHEN product_id IS NULL OR product_id = '' THEN 1 ELSE 0 END) AS missing_product_id,
    SUM(CASE WHEN product_name IS NULL OR product_name = '' THEN 1 ELSE 0 END) AS missing_product_name,
    SUM(CASE WHEN category IS NULL OR category = '' THEN 1 ELSE 0 END) AS missing_category,
    SUM(CASE WHEN launch_date IS NULL OR launch_date = '' THEN 1 ELSE 0 END) AS missing_launch_date,
    SUM(CASE WHEN base_price IS NULL OR base_price = '' THEN 1 ELSE 0 END) AS missing_base_price,
    0 AS padding_column
FROM product_info;

-- 2.3 Transactional Sales Integrity Audit
SELECT 
    'sales_data' AS table_audit,
    SUM(CASE WHEN order_id IS NULL OR order_id = '' THEN 1 ELSE 0 END) AS missing_order_id,
    SUM(CASE WHEN customer_id IS NULL OR customer_id = '' THEN 1 ELSE 0 END) AS missing_customer_id,
    SUM(CASE WHEN product_id IS NULL OR product_id = '' THEN 1 ELSE 0 END) AS missing_product_id,
    SUM(CASE WHEN quantity IS NULL OR quantity = '' THEN 1 ELSE 0 END) AS missing_quantity,
    SUM(CASE WHEN unit_price IS NULL OR unit_price = '' THEN 1 ELSE 0 END) AS missing_unit_price,
    SUM(CASE WHEN delivery_status IS NULL OR delivery_status = '' THEN 1 ELSE 0 END) AS missing_delivery,
    SUM(CASE WHEN order_date IS NULL OR order_date = '' THEN 1 ELSE 0 END) AS missing_order_date,
    SUM(CASE WHEN payment_method IS NULL OR payment_method = '' THEN 1 ELSE 0 END) AS missing_payment_method,
    SUM(CASE WHEN region IS NULL OR region = '' THEN 1 ELSE 0 END) AS missing_region,
    SUM(CASE WHEN discount_applied IS NULL OR TRIM(discount_applied) = '' THEN 1 ELSE 0 END) AS missing_discount
FROM sales_data;

-- Deep-dive sanity check on order dates
SELECT 
    COUNT(order_date) AS total_populated_dates, 
    SUM(CASE WHEN order_date IS NULL THEN 1 ELSE 0 END) AS null_dates
FROM sales_data;


-- ============================================================================
-- STAGE 3: Uniqueness Verification (Primary Key & Constraint Violations)
-- ============================================================================
SELECT order_id, COUNT(*) AS cnt FROM sales_data GROUP BY order_id HAVING cnt > 1;
SELECT customer_id, COUNT(*) AS cnt FROM customer_info GROUP BY customer_id HAVING cnt > 1;
SELECT product_id, COUNT(*) AS cnt FROM product_info GROUP BY product_id HAVING cnt > 1;


-- ============================================================================
-- STAGE 4: Categorical Consistency (Identifying Typos, Case Variance & Anomalies)
-- ============================================================================
SELECT 'sales_data' AS src_tbl, 'payment_method' AS col, payment_method AS val, COUNT(*) AS cnt FROM sales_data GROUP BY payment_method
UNION ALL
SELECT 'sales_data', 'delivery_status', delivery_status, COUNT(*) AS cnt FROM sales_data GROUP BY delivery_status
UNION ALL
SELECT 'sales_data', 'region', region, COUNT(*) AS cnt FROM sales_data GROUP BY region
UNION ALL
SELECT 'product_info', 'category', category, COUNT(*) AS cnt FROM product_info GROUP BY category
UNION ALL
SELECT 'customer_info', 'gender', gender, COUNT(*) AS cnt FROM customer_info GROUP BY gender
UNION ALL
SELECT 'customer_info', 'region', region, COUNT(*) AS cnt FROM customer_info GROUP BY region
UNION ALL
SELECT 'customer_info', 'loyalty_tier', loyalty_tier, COUNT(*) AS cnt FROM customer_info GROUP BY loyalty_tier;


-- ============================================================================
-- STAGE 5: Business Rule & Boundary Validation (Negative/Impossible Metric Audits)
-- ============================================================================
SELECT COUNT(*) AS total_invalid_records 
FROM sales_data
WHERE quantity <= 0 OR unit_price <= 0 OR discount_applied < 0;


-- ============================================================================
-- STAGE 6: Advanced Analytical Foundations (Window Functions & Aggregations)
-- ============================================================================

-- 6.1 Regional Pricing Baselines
SELECT region, unit_price, 
       AVG(unit_price) OVER(PARTITION BY region) AS regional_avg_price
FROM sales_data;

-- 6.2 Intracategory Product Competitive Pricing Rank
SELECT product_name, category, base_price,
       RANK() OVER(PARTITION BY category ORDER BY base_price DESC) AS price_rank,
       ROW_NUMBER() OVER(PARTITION BY category ORDER BY base_price DESC) AS unique_item_index
FROM product_info;

-- 6.3 Volumetric Customer Distribution Checks
SELECT order_id, customer_id,
       COUNT(order_id) OVER(PARTITION BY customer_id) AS total_customer_historic_orders
FROM sales_data;

-- 6.4 Strategic Financial Running Totals (Cumulative Velocity per Region)
SELECT region, order_date, (quantity * unit_price) AS row_revenue,
       SUM(quantity * unit_price) OVER(PARTITION BY region ORDER BY order_date) AS running_total_revenue
FROM sales_data;

-- 6.5 Operational Moving Averages (Smooth 3-Day Revenue Variance Model)
SELECT order_date,
       (quantity * unit_price) AS daily_revenue,
       AVG(quantity * unit_price) OVER(
           ORDER BY order_date
           ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
       ) AS 3_day_moving_avg
FROM sales_data;

-- 6.6 Subquery & CTE Operations (Strategic Client Spending Profiles)
WITH top_customers AS (
    SELECT customer_id, SUM(quantity * unit_price) AS total_spend
    FROM sales_data
    GROUP BY customer_id
)
SELECT * FROM top_customers WHERE total_spend > 100;

-- 6.7 Identification of Outliers (Transactions Beating Average Order Revenue)
SELECT customer_id, (quantity * unit_price) AS transaction_revenue
FROM sales_data
WHERE (quantity * unit_price) > (SELECT AVG(quantity * unit_price) FROM sales_data);

-- Final check against chronological timeline bounds
SELECT * FROM sales_data ORDER BY order_date LIMIT 10;

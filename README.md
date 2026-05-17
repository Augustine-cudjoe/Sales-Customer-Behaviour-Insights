# Sales & Customer Behaviour Insights

> End-to-end data analytics project covering data cleaning, feature engineering, exploratory analysis, visualisation, and business intelligence reporting across two real-world style datasets.

---

## Project overview

This project investigates sales performance and customer behaviour for Green Cart Ltd. (a UK-based eco-friendly e-commerce company). The work was completed as part of a structured data analytics internship programme and covers the full analytics pipeline — from raw, messy CSV files through to polished PDF reports and business recommendations.

The analysis addresses questions that a real Data & Insights team would face ahead of a quarterly business review:

- Which customer segments are most engaged and most valuable?
- Do discounts actually drive more sales?
- Which regions have data quality or delivery problems?
- Does the timing of a customer's sign-up affect how they behave?

---


## Datasets

### Week 2 — Sales & Customer Behaviour (Green Cart Ltd.)

| File | Description |
|---|---|
| `sales_data.csv` | Order-level transactions: quantity, price, discount, delivery status, payment method |
| `product_info.csv` | Product catalogue: category, launch date, base price, supplier |
| `customer_info.csv` | Customer profiles: signup date, region, gender, loyalty tier |

---


## 🛠️ Technology Stack
* **Database & Ingestion:** MySQL Workbench (SQL Audit, Joins, Window Functions)
* **ETL & Analytics:** Python 3.9 (Pandas, NumPy, Scikit-learn)
* **Visualization Engine:** Microsoft Power BI Desktop (Power Query, DAX Data Modeling)
* **Executive Presentation:** Microsoft Word (Corporate Styling, Visual Typography)


---
## 🚀 Project Architecture & Workflow

```text
 ┌──────────────┐      ┌──────────────────────┐      ┌─────────────┐      ┌────────────────────────┐
 │   RAW DATA   │ ───> │  SQL PRE-CLEAN AUDIT │ ───> │  PYTHON ETL │ ───> │ POWER BI DASHBOARD     │
 │ 3 CSV Tables │      │ Integrity & Ingestion│      │ Engineering │      │ 4-Page Executive UI    │
 └──────────────┘      └──────────────────────┘      └─────────────┘      └────────────────────────┘
                                                                                      │
                                                                                      ▼
                                                                          ┌────────────────────────┐
                                                                          │ 11-PAGE CORPORATE BRIEF│
                                                                          │ Strategy & Next Steps  │
                                                                          └────────────────────────┘
```

---

## 🗄️ Phase 1: Pre-Cleaning Database Audit (SQL)
Before building the cleaning pipelines, a robust diagnostic audit script (`green_cart_data_audit.sql`) was developed in MySQL to protect data lineage and identify structural faults at ingestion.

Ingestion Guarding: Handled big data payload constraints (`max_allowed_packet`) and stripped hidden encoding characters (**Byte Order Mark `ï»¿`**) from primary keys.

Integrity Error Interception: Caught a critical database truncation error causing a 17.4% row loss (521 missing transaction records). Restoring this data saved the project from an initial **56% understatement of total revenue.
Advanced Analytical Foundations: Implemented window functions (`PARTITION BY`), 3-Day Rolling Moving Averages, and Common Table Expressions (CTEs) to establish localized pricing benchmarks and detect out-of-boundary transactional outliers.

---


 What I did

## 🐍 Phase 2: Automated ETL & Feature Engineering (Python)
Using `pandas` and `scikit-learn`, an automated pipeline was constructed to ingest, clean, and enrich the core data models.

Each dataset was cleaned individually before merging. Issues found and resolved:

**Text standardisation** — multiple spellings of the same category value were mapped using explicit whitelists:

python
# delivery_status: 'DELAYED', 'delyd', 'Delayed' → 'Delayed'
sales_data['delivery_status'] = sales_data['delivery_status'].str.strip().replace({
    'delivered': 'Delivered', 'DELAYED': 'Delayed',
    'delrd': 'Delivered',     'delyd': 'Delayed',
    'cancelled': 'Cancelled'
})

# loyalty_tier: 'GOLD', 'gld', 'gold' → 'Gold'
customer_data['loyalty_tier'] = customer_data['loyalty_tier'].str.strip().replace({
    'GOLD': 'Gold', 'gold': 'Gold', 'gld': 'Gold',
    'SILVER': 'Silver', 'silver': 'Silver', 'sllver': 'Silver',
    'BRONZE': 'Bronze', 'bronze': 'Bronze', 'brnze': 'Bronze',
})


**Missing values** — handled column by column with justified decisions:

| Column | Action |
|---|---|
| `delivery_status` / `region` / `payment_method` | Filled with `'Unknown'` |
| `quantity` / `unit_price` | Filled with column median |
| `discount_applied` | Filled with `0` (no discount assumed) |
| `loyalty_tier` / `gender` | Filled with `'Unknown'` |
| `order_id` / `customer_id` / `product_id` | Rows dropped — no key = no analysis |

**Date conversion:**

python
sales_data['order_date']     = pd.to_datetime(sales_data['order_date'],     errors='coerce')
customer_data['signup_date'] = pd.to_datetime(customer_data['signup_date'],  errors='coerce')

# Week 1: explicit format to prevent silent mis-parsing
df['signup_date'] = pd.to_datetime(df['signup_date'], format='%d-%m-%y', errors='coerce')

**Duplicates and validation:**


sales_data.drop_duplicates(subset=['order_id'], keep='first', inplace=True)
sales_data = sales_data[(sales_data['quantity'] > 0) & (sales_data['unit_price'] > 0)]


---

### 2. Feature engineering

Six new columns created after merging:


# Revenue after discount
merged_df['revenue'] = merged_df['quantity'] * merged_df['unit_price'] * (1 - merged_df['discount_applied'])

# ISO week number for trend analysis
merged_df['order_week'] = merged_df['order_date'].dt.isocalendar().week

# Price tier segmentation
merged_df['price_band'] = pd.cut(merged_df['unit_price'],
                                  bins=[0, 14, 30, np.inf],
                                  labels=['Low', 'Medium', 'High'])

# Days between product launch and order
merged_df['days_to_order'] = (merged_df['order_date'] - merged_df['launch_date']).dt.days.abs()

# Email provider extraction
merged_df['email_domain'] = merged_df['email'].str.split('@').str[1]

# Late delivery boolean flag
merged_df['is_late'] = merged_df['delivery_status'] == 'Delayed'


---

### 3. Summary tables

Built using `groupby()`, `agg()`, and `pivot_table()`:


# Weekly revenue by region
weekly_revenue = merged_df_time.pivot_table(
    index='week', columns='region_y', values='revenue', aggfunc='sum'
).fillna(0)

# Category performance
merged_df.groupby('category')[['revenue', 'quantity', 'discount_applied']].sum().round(2)

# Customer behaviour by loyalty tier
merged_df.groupby('loyalty_tier').agg(
    customers=('customer_id', 'nunique'),
    total_revenue=('revenue', 'sum'),
    avg_order=('revenue', 'mean'),
    total_orders=('order_id', 'count')
)

# Delivery delay rate by region and price band
merged_df.groupby(['region_y', 'price_band'])['is_late'].agg(['mean', 'count'])
### 4. Visualisations

Six charts produced with Matplotlib and Seaborn:

| # | Chart type | What it shows |
|---|---|---|
| 1 | Line plot | Weekly revenue trends by region (3-week rolling average) |
| 2 | Horizontal bar chart | Top 5 categories by total revenue |
| 3 | Boxplot | Quantity distribution by category and price band |
| 4 | Heatmap | Correlation between revenue, quantity, and discount |
| 5 | Countplot | Orders by loyalty tier with region as hue |
| 6 | Stacked bar | Delivery status breakdown by price band |

## 📊 Phase 3: Interactive Visualizations & Data Modeling (Power BI)
Developed a cohesive, 7-page interactive dashboard aligned strictly with Green Cart’s eco-friendly brand identity, utilizing a strict typographic hierarchy and accessibility guidelines.

* **Page 1: Executive Revenue Summary:** High-level revenue trajectories mapped against an static **48K baseline marker**, monitoring seasonal growth velocities.
* **Page 2: Regional Performance Matrix:** Geographic breakdown of order distribution volumes paired with regional operational performance.
* **Page 3: Customer Intelligence & Loyalty Tiers:** Deep-dive demographic tracking examining spending habits and preferred transaction methods.
* **Page 4: Operations & Supply Chain Risk:** Supply chain grid monitoring delivery health and mapping shipping bottlenecks.




### 5. Business questions answered

#### Q1 — Which product categories drive the most revenue, and in which regions?

most_rev=merged_df.groupby(['region','category'])[ 'revenue'].sum().unstack().fillna(0).astype('Int64')
most_rev['total_revenue']=most_rev.sum(axis=1)
most_rev.sort_values(by='total_revenue', ascending=False)

Finding: Cleaning is the top category in every region, with East generating the highest cleaning revenue (£13,641). West leads overall with £32432 total revenue. Personal Care performs disproportionately poorly in the South, suggesting low demand in that region. North is the weakest across all categories.

#### Q2 — Do discounts lead to more items sold?

 correlation = merged_df['discount_applied'].corr(merged_df['quantity'])
 
Finding: No. Our correlation analysis yielded a coefficient of -0.02 , indicating a near-total lack of relationship between discount depth and a 0.20 discount applied, which has the least quantity ordered.


#### Q3 — Which loyalty tier generates the most value?

loyalty_revenue=merged_df.groupby(['loyalty_tier']).agg(
    total_revenue=('revenue','sum'),
    avg_revenue=('revenue','mean'),
    quantity_order=('order_id','count')

).sort_values(by='total_revenue', ascending=False)
loyalty_revenue.astype('Int64')

Finding: Gold generates the highest total revenue, followed by  Silver and Bronze. 

#### Q4 — Are certain regions struggling with delivery delays?

struggling_regions = merged_df.groupby('region').agg(
    total_orders=('order_id', 'count'),
   
    delayed_orders=('delivery_status', lambda x: (x == 'Delayed').sum())
)

struggling_regions['delay_rate'] = ((struggling_regions['delayed_orders'] / struggling_regions['total_orders']) * 100).round(2)
struggling_regions.sort_values(by='delay_rate',ascending=False)

Finding: Logistics performance is critical in all areas, with the South region recording the greatest criticality, reaching a delay rate of 41.4%, followed by East with 40.5%.

#### Q5 — Do customer signup patterns influence purchasing activity?

signup_pattern =merged_df_time.groupby('purchase_speed').agg(
    average_quantity=('quantity', 'mean'),
    average_revenue=('revenue','mean'),
    purchase_count = ('order_id','count')

)

Finding: Yes . Early customers (≤14 days) show a higher strategic value, with an average spend (84.0) and quantity per order (3.2) consistently higher than late customers.



### 6. Stretch tasks

#### `.query()` segmentation

customer_query=merged_df.query( 'month_quarter=="Q2" & days_signup_order <= 14 & discount_applied= =0.20 ')
customer_query

#### MinMaxScaler — revenue normalisation

from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
merged_df['revenue_scaled'] = scaler.fit_transform(merged_df[['revenue']])
merged_df['revenue_scaled'].mean()

#### Underperforming product flag

underperforming_table = underperforming[
    ['product_name', 'quantity', 'discount_applied', 'delivery_status', 'region']
]
underperforming_table.head(5)

## Key recommendations

1.    Focus marketing investment on Gold in East and West

2.    Audit and reduce the platform-wide delivery delay rate.

## Data issues identified

Data issues identified

Problem: loyalty_tier contained 15+ raw variants for 4 intended values (Bronze, Silver, Gold, Platinum) — including brnze, GOLD, sllver, gld — caused by free-text data entry with no input validation.

Impact: Without correction, tier-based segmentation silently mislabels customers, understating tier sizes and distorting revenue comparisons.

Fix at source:

* Replace the free-text field with a dropdown restricted to the four approved values.
* Add server-side validation, rejecting any value outside the approved list.
* Run a scheduled automated check that flags unrecognised tier values for manual review.

## How to run

bash
# Clone the repository
git clone https://github.com/Augustine-cudjoe/Sales-Customer-Behaviour-Insights/tree/master
cd your-repo-name

# Install dependencies
pip install pandas numpy matplotlib seaborn scikit-learn reportlab


# Run Week 2 notebook
jupyter notebook week2/sales_product_dataset.ipynb




## Deliverables

| File | Description |
|---|---|
| `Project_Report_Augustine_Cudjoe.pdf` | 11-pages business report  |


---

## Skills demonstrated


Data cleaning        →  missing value handling, type coercion, duplicate removal,
                        whitelist standardisation, regex validation, outlier capping

Feature engineering  →  revenue formula, date extraction, pd.cut() banding,
                        boolean flags, string parsing

Aggregation          →  groupby, pivot_table, agg, unstack, merge, query,
                        rolling averages, cohort comparison

Visualisation        →  line plots, bar charts, boxplots, heatmaps,
                        countplots, stacked bars (matplotlib + seaborn)

Statistical          →  Pearson correlation, median imputation, MinMaxScaler,
                        quantile-based flagging

Reporting            →  structured PDF reports, Word documents,
                        executive summaries, data risk sections


---

## Acknowledgements

Completed as part of the Uptrail Data Analytics Internship Programme.  
Datasets are synthetic/anonymised and used for educational purposes only.

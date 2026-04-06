# %% [markdown]
# Loading dataset

# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler


# %%
sales_data = pd.read_csv('sales_data.csv')
sales_data




# %%

customer_data = pd.read_csv('customer_info.csv')
customer_data

# %%
product_data = pd.read_csv('product_info.csv')
product_data

# %% [markdown]
# Data cleaning 

# %% [markdown]
# Standardise text formatting

# %%
sales_data['delivery_status']=sales_data['delivery_status'].str.strip().replace({'delivered':'Delivered','DELAYED':'Delayed','cancelled':'Cancelled','delrd':'Delivered','delyd':'Delayed'})

sales_data['payment_method']=sales_data['payment_method'].str.strip().replace({'credit card':'Credit Card','paypal':'PayPal','bank transfr':'Bank Transfer','cash':'Cash'})
sales_data['region']=sales_data['region'].str.strip().replace({'nrth':'North','south':'South','east':'East','west':'West'})
customer_data['gender']=customer_data['gender'].str.strip().replace({'MALE':'Male','FEMALE':'Female','male':'Male','female':'Female','femle':'Female'})
customer_data['loyalty_tier']=customer_data['loyalty_tier'].str.strip().replace({'BRONZE':'Bronze','bronze':'Bronze','SILVER':'Silver','silver':'Silver','sllver':'Silver','brnze':'Bronze','GOLD':'Gold','gold':'Gold','gld':'Gold','PLATINUM':'Platinum','platinum':'Platinum'})
customer_data['loyalty_tier'].value_counts()


# %% [markdown]
#  Convert date columns 

# %%
sales_data['order_date']=pd.to_datetime(sales_data['order_date'], errors='coerce')
sales_data['quantity']=pd.to_numeric(sales_data['quantity'], errors='coerce').astype('Int64')
customer_data['signup_date']=pd.to_datetime(customer_data['signup_date'], errors='coerce')
product_data['launch_date']=pd.to_datetime(product_data['launch_date'], errors='coerce')
product_data.info()

# %% [markdown]
#  Handle missing values:

# %% [markdown]
# Sales data

# %%
sales_data.isnull().sum()
sales_data['delivery_status'] = sales_data['delivery_status'].fillna('Unknown')
sales_data['payment_method'] = sales_data['payment_method'].fillna('Unknown')
sales_data['region'] = sales_data['region'].fillna('Unknown')
sales_data['quantity'] = sales_data['quantity'].fillna(sales_data['quantity'].median())
sales_data['unit_price'] = sales_data['unit_price'].fillna(sales_data['unit_price'].median())
sales_data['discount_applied'] = sales_data['discount_applied'].fillna(0)


# %% [markdown]
# Customer data

# %%
customer_data.isnull().sum()
cols_to_fix = ['gender', 'region', 'loyalty_tier']
customer_data[cols_to_fix] = customer_data[cols_to_fix].fillna('Unknown')

# %% [markdown]
# Product data

# %%
product_data.isnull().sum()

# %% [markdown]
# Dropping NaN Values

# %% [markdown]
#  Sales Data

# %% [markdown]
# 
# A sales record without order_id or product_id is statistical noise . keeping incomplete data slows down filtering operations and makes graphs less precise.
# 
# The order_date column was retained despite a high proportion of missing values (60.6%). Imputation was not performed due to the risk of introducing inaccurate time-based information. Instead, rows with valid dates were used selectively for analyses requiring temporal insights.

# %%

sales_data.dropna(subset=['order_id', 'customer_id', 'product_id'], inplace=True)
sales_data.isnull().sum()


# %% [markdown]
# Customer

# %% [markdown]
# The dataset contains minimal missing values across key variables, with less than 1% missing in customer_id, email, and signup_date. Rows with missing customer_id were removed due to their importance as unique identifiers, while other missing values were handled using appropriate imputation or left unchanged where they did not affect the analysis

# %%
customer_data['signup_date'] = customer_data['signup_date'].fillna(customer_data['signup_date'].median())
customer_data['email'] = customer_data['email'].fillna('Unknown')
customer_data = customer_data.dropna(subset=['customer_id'])



# %% [markdown]
#  Remove duplicates:

# %% [markdown]
# Sales Dataset

# %%
sales_data.drop_duplicates(subset=['order_id'],keep='first', inplace=True)
sales_data

# %% [markdown]
# Product

# %%
product_data.duplicated().sum()


# %% [markdown]
# Customer

# %%
customer_data.duplicated().sum()

# %% [markdown]
#  Validate numeric columns:

# %%
sales_data=sales_data[(sales_data['quantity'] >0) &(sales_data['unit_price'] >0)& (sales_data['discount_applied']>0)]
sales_data

# %%
product_data[product_data['base_price'] >= 0 ]

# %% [markdown]
# 3. Merge the Data

# %%
merged_data = pd.merge(sales_data, product_data, on='product_id', how='left')
merged_data


# %%
merged_df.head(10)

# %% [markdown]
# The dataset includes 1995  transactions made by 497 customers on a catalog of 30 products . A geographical discrepancy was detected in 80% of cases between the customer's residence and the order destination; the analysis was conducted based on the Destination Region to ensure the accuracy of the logistics and revenue data.

# %%
merged_df= pd.merge(merged_data, customer_data.drop(columns=['region']), on=['customer_id' ], how='left')
merged_df

# %% [markdown]
# 4. Feature Engineering

# %% [markdown]
# 4.1 revenue = quantity × unit_price × (1 - discount_applied)

# %%
merged_df['revenue'] = merged_df['quantity'] * merged_df['unit_price'] * (1 - merged_df['discount_applied'])
merged_df.head(10)

# %% [markdown]
# 4.2 order_week = ISO week from order_date

# %%
merged_df['order_week'] = merged_df['order_date'].dt.isocalendar().week
merged_df

# %% [markdown]
# 4.3 price_band = Categorise unit price as Low (<£15), Medium (£15–30), High (>£30)

# %%
merged_df['price_band']=pd.cut(merged_df['unit_price'], bins=[0, 14, 30, np.inf], labels=['Low', 'Medium', 'High'])
merged_df

# %% [markdown]
# 4.4 days_to_order = Days between launch_date and order_date
# 

# %%
merged_df['days_to_order'] = (merged_df['order_date'] - merged_df['launch_date']).dt.days.abs()
merged_df

# %% [markdown]
# 4.5 email_domain = Extract domain from email (e.g., gmail.com)
# 

# %%
merged_df['email_domain'] = merged_df['email'].str.split('@').str[1]
merged_df.head(10)

# %% [markdown]
# 4.6 is_late = True if delivery_status is "Delayed"

# %%
merged_df['is_late_delivery'] = merged_df['delivery_status'].apply(lambda x: True if x == 'Delayed' else False)
merged_df.head(10)

# %% [markdown]
# 5. Create Summary Tables

# %% [markdown]
# Weekly revenue trends by region

# %%

merged_df["weekly"] = merged_df['order_date'].dt.to_period('W')
weekly_trend = merged_df.pivot_table(
    index='weekly', 
    columns='region', 
    values='revenue', 
    aggfunc='sum'
).fillna(0)
weekly_trend['total']=weekly_trend.sum(axis=1)
weekly_trend.astype('Int64')

# %% [markdown]
# Product category performance (revenue, quantity, discount)

# %%

measures=['revenue','quantity','discount_applied']

Product_category_performance=merged_df.groupby(['category'])[measures].sum().round(0).sort_values(by='revenue', ascending=False)
Product_category_performance

# %% [markdown]
# Customer behaviour by loyalty_tier and signup_month

# %% [markdown]
# Extract the month name from the sign up date

# %%
merged_df['month_name'] = merged_df['signup_date'].dt.month_name()
merged_df

# %% [markdown]
# Customer behaviour by loyalty_tier and signup_month

# %%

customer_behaviour=merged_df.groupby(['month_name','loyalty_tier'])['revenue'].agg(['sum','mean']).unstack().fillna(0).astype('Int64')
customer_behaviour



# %% [markdown]
# Delivery performance by region and price_band

# %%
cat=['price_band', 'region']
delivery_performance_pb_region=merged_df.groupby(['delivery_status'])[cat].value_counts().unstack(fill_value=0)
delivery_performance_pb_region

# %%
merged_df.pivot_table( index=['region','price_band' ], columns='delivery_status', aggfunc='size').unstack().fillna(0)

# %% [markdown]
# 6. Are certain regions struggling with delivery delays?

# %%

delivery_analysis = merged_df.groupby(['region', 'price_band'])['is_late_delivery'].agg(['mean', 'count'])  


delivery_analysis['delay_rate_%'] = (delivery_analysis['mean'] * 100).round(2)
delivery_analysis.rename(columns={'count': 'total_orders'}, inplace=True)
delivery_analysis.drop(columns=['mean'], inplace=True)


delivery_analysis.unstack(fill_value=0)


# %% [markdown]
# Preferred payment methods by loyalty_tier

# %%
preferred_payment_methods = merged_df.groupby('loyalty_tier')['payment_method'].value_counts().unstack(fill_value=0)
preferred_payment_methods

# %% [markdown]
# 6. Visual Exploration

# %%
merged_df

# %% [markdown]
# 1. Line plot - weekly revenue trends by region

# %% [markdown]
# Create Weekly Groups

# %% [markdown]
# Due to a high proportion of missing values (approximately 60.6%) in the order_date column, rows without valid dates were excluded only for time-based analysis. While this reduced the dataset size, it ensured the accuracy and reliability of temporal insights. All other analyses were conducted using the full dataset.

# %%
merged_df_time=merged_df.copy()
merged_df_time.dropna(subset=['order_date'], inplace=True)
merged_df_time

# %% [markdown]
# create the week column

# %%
merged_df_time['week']=merged_df_time['order_date'].dt.to_period('W').dt.start_time
merged_df_time

# %% [markdown]
# Aggregate

# %%
weekly_revenue=merged_df_time.pivot_table(index='week', columns='region', values='revenue', aggfunc='sum').fillna(0)

weekly_revenue['wk_total'] = weekly_revenue.sum(axis=1).astype('Int64')

weekly_revenue

# %% [markdown]
# Plot the Line Chart

# %%

weekly_revenue.plot()
plt.title('Weekly Revenue Trends by Region')
plt.xlabel('Week')
plt.ylabel('Revenue')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %% [markdown]
# Bar chart - top 5 categories by revenue

# %%

top_categories = merged_df.groupby('category')['revenue'].sum().nlargest(5)
top_categories.plot(kind='bar', fontsize=12, color='red')
plt.xlabel('Category')
plt.ylabel('Revenue')
plt.title('Revenue by Product Category')
plt.xticks(rotation=45)
plt.tight_layout()
plt.legend()
plt.show() 
 

# %% [markdown]
# Boxplot - quantity vs discount across categories

# %%
sns.boxplot(x='category', y='quantity', hue='discount_applied', data=merged_df)
plt.title('Quantity vs Discount across Categories')
plt.xlabel('Category')
plt.ylabel('Quantity vs Discount')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %% [markdown]
# 4. Heatmap - correlation between revenue, discount, and quantity

# %% [markdown]
# Compute Correlation

# %%
corr=merged_df[['revenue','discount_applied','quantity']].corr()
corr

# %% [markdown]
# Compute Correlation

# %%
sns.heatmap(corr,annot=True)

# %% [markdown]
# 5. Countplot - orders by loyalty tier (with hue = region)

# %%
sns.countplot(x='loyalty_tier', hue='region', data=merged_df)
plt.title('Orders by Loyalty Tier and Region')
plt.xlabel('Region')
plt.ylabel('Loyalty Tier ')

# %% [markdown]
# 6. Stacked bar or pie - delivery status by price band

# %%
delivery_analysis=merged_df.groupby(['price_band', 'delivery_status']).size().unstack(0)
delivery_analysis.plot(kind='bar', stacked=True)

plt.title('Delivery Status by Price Band')
plt.xlabel('Delivery Status')
plt.ylabel('Number of Orders')
plt.legend(title='Price Band')
plt.tight_layout()
plt.show()  

# %% [markdown]
# 7. Business Questions to Answer 

# %% [markdown]
# 1. Which product categories drive the most revenue, and in which regions?

# %%
most_rev=merged_df.groupby(['region','category'])[ 'revenue'].sum().unstack().fillna(0).astype('Int64')
most_rev['total_revenue']=most_rev.sum(axis=1)
most_rev.sort_values(by='total_revenue', ascending=False)

# %% [markdown]
# 4. Do discounts lead to more items sold?

# %%
merged_df.groupby(['discount_applied'])['quantity'].sum().sort_values(ascending=False).astype('Int64')

# %% [markdown]
# 5. Which loyalty tier generates the most value?

# %%
merged_df.groupby(['loyalty_tier'])['revenue'].sum().sort_values(ascending=False).astype('Int64')


# %%
pd.pivot_table(merged_df,index='loyalty_tier', values='revenue', aggfunc='sum').sort_values(by='revenue', ascending=False).astype('Int64')

# %% [markdown]
# 6. Are certain regions struggling with delivery delays?

# %%
 struggling_regions=merged_df.groupby('region')['delivery_status'].value_counts().unstack().fillna(0)
 struggling_regions['Delayed'].sort_values(ascending=False).astype("int64")

# %% [markdown]
# 7. Do customer signup patterns influence purchasing activity?

# %% [markdown]
# Calculate the delay between signup and purchase

# %%
merged_df_time['days_perchase'] = (merged_df_time['order_date'] - merged_df_time['signup_date']).dt.days.abs()
merged_df_time['days_perchase'].astype("Int64")

# %% [markdown]
# Group by the delay to see if 'quick signups' spend more

# %%
merged_df_time.groupby(['days_perchase'])['revenue'].count().sort_values(ascending=False).astype('Int64')

# %% [markdown]
# 

# %% [markdown]
# 8. Optional Stretch Tasks

# %% [markdown]
# Use .query() to extract:
# - Customers who signed up in Q2
# - Placed an order within 14 days
# - Received a discount > 20%

# %%
merged_df['month_quarter'] = 'Q'+ merged_df['order_date'].dt.quarter.astype('Int64').astype('str')
merged_df

# %% [markdown]
# Days between signup and order

# %%
merged_df['days_signup_order']=(merged_df['order_date']-merged_df['signup_date']).dt.days.abs()
merged_df['days_signup_order'].astype('Int64')

# %%
merged_df.query( 'month_quarter=="Q2" & days_signup_order <= 14 & discount_applied= =0.20 ')

# %% [markdown]
# Use MinMaxScaler to normalise revenue or price

# %%
scaler = MinMaxScaler()
merged_df['revenue_scaled'] = scaler.fit_transform(merged_df[['revenue']])
merged_df

# %% [markdown]
# Flag underperforming products (low quantity, high discount, delayed deliveries)

# %%
underperforming = merged_df[
    (merged_df['quantity'] < merged_df['quantity'].median()) &
    (merged_df['discount_applied'] >= 0.20) &
    (merged_df['delivery_status'] == 'Delayed')
]
underperforming

# %%
underperforming_table = underperforming[
    ['product_name', 'quantity', 'discount_applied', 'delivery_status', 'region']
]
underperforming_table.head(15)



import os

import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "ecommerce_db")
DB_USER = os.getenv("DB_USER", "airflow")
DB_PASSWORD = os.getenv("DB_PASSWORD", "airflow")

connection = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(connection)

# Dashboard title
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    layout="wide"
)

st.title("🛒 E-Commerce Analytics Dashboard")
st.markdown("---")

#Load data from the database
query = """
SELECT
    f.order_id,
    f.customer_id,
    f.product_id,
    f.sales,
    f.order_date,
    c.region,
    c.segment,
    p.category,
    p.product_name
FROM fact_sales f
JOIN dim_customer c
ON f.customer_id = c.customer_id
JOIN dim_product p
ON f.product_id = p.product_id
"""

df = pd.read_sql(query, engine)

st.write("Number of rows:", len(df))
st.write(df.head())
st.write(df.columns.tolist())

df["order_date"] = pd.to_datetime(df["order_date"])

#KPI cards
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Sales",
    f"${df['sales'].sum():,.2f}"
)

col2.metric(
    "Orders",
    len(df)
)

col3.metric(
    "Customers",
    df["customer_id"].nunique()
)

col4.metric(
    "Average Order",
    f"${df['sales'].mean():,.2f}"
)

#Sales charts - monthly
monthly = (
    df.groupby(df["order_date"].dt.to_period("M"))["sales"]
    .sum()
    .reset_index()
)

monthly["order_date"] = monthly["order_date"].astype(str)

fig_monthly = px.line(
    monthly,
    x="order_date",
    y="sales",
    title="Monthly Sales"
)

st.plotly_chart(fig_monthly, use_container_width=True, key="monthly_sales")

#Sales by region
region = (
    df.groupby("region")["sales"]
    .sum()
    .reset_index()
)

fig_region = px.bar(
    region,
    x="region",
    y="sales",
    title="Sales by Region"
)

st.plotly_chart(fig_region, use_container_width=True, key="region_sales")

#Sales by category
category = (
    df.groupby("category")["sales"]
    .sum()
    .reset_index()
)

fig_category = px.bar(
    category,
    x="category",
    y="sales",
    title="Sales by Category"
)

st.plotly_chart(fig_category, use_container_width=True, key="category_sales")

#Top products
products = (
    df.groupby("product_name")["sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig_products = px.bar(
    products,
    x="sales",
    y="product_name",
    orientation="h",
    title="Top Products"
)

st.plotly_chart(fig_products, use_container_width=True, key="top_products")

import os

import pandas as pd
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from sqlalchemy import create_engine

# ----------------------------------
# Load environment variables
# ----------------------------------
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

# ----------------------------------
# Streamlit Page Config
# ----------------------------------
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    layout="wide"
)

st.title("📊 E-Commerce Analytics Dashboard")
st.markdown("---")

# ----------------------------------
# Load Data
# ----------------------------------
query = """
SELECT
    f.order_id,
    f.order_date,
    f.sales,

    c.customer_name,
    c.segment,
    c.region,

    p.category,
    p.sub_category,
    p.product_name,

    d.year,
    d.quarter,
    d.month

FROM fact_sales f

LEFT JOIN dim_customer c
ON f.customer_id = c.customer_id

LEFT JOIN dim_product p
ON f.product_id = p.product_id

LEFT JOIN dim_date d
ON f.order_date = d.date_id

ORDER BY f.order_date;
"""

df = pd.read_sql(query, engine)

df["order_date"] = pd.to_datetime(df["order_date"])

# ----------------------------------
# Sidebar Filters
# ----------------------------------
st.sidebar.header("Filters")

regions = st.sidebar.multiselect(
    "Region",
    sorted(df["region"].dropna().unique())
)

categories = st.sidebar.multiselect(
    "Category",
    sorted(df["category"].dropna().unique())
)

segments = st.sidebar.multiselect(
    "Customer Segment",
    sorted(df["segment"].dropna().unique())
)

years = st.sidebar.multiselect(
    "Year",
    sorted(df["year"].dropna().unique())
)

filtered_df = df.copy()

if regions:
    filtered_df = filtered_df[
        filtered_df["region"].isin(regions)
    ]

if categories:
    filtered_df = filtered_df[
        filtered_df["category"].isin(categories)
    ]

if segments:
    filtered_df = filtered_df[
        filtered_df["segment"].isin(segments)
    ]

if years:
    filtered_df = filtered_df[
        filtered_df["year"].isin(years)
    ]

# ----------------------------------
# No data after filtering
# ----------------------------------
if filtered_df.empty:
    st.warning("No data found for the selected filters.")
    st.stop()

# ----------------------------------
# KPI Cards
# ----------------------------------
col1, col2, col3 = st.columns(3)

col1.metric(
    "Total Sales",
    f"${filtered_df['sales'].sum():,.2f}"
)

col2.metric(
    "Orders",
    f"{filtered_df['order_id'].nunique():,}"
)

col3.metric(
    "Customers",
    f"{filtered_df['customer_name'].nunique():,}"
)

st.markdown("---")

# ----------------------------------
# Monthly Sales
# ----------------------------------
monthly = (
    filtered_df
    .groupby(filtered_df["order_date"].dt.to_period("M"))["sales"]
    .sum()
    .reset_index()
)

monthly["order_date"] = monthly["order_date"].astype(str)

fig_monthly = px.line(
    monthly,
    x="order_date",
    y="sales",
    markers=True,
    title="Monthly Sales"
)

st.plotly_chart(fig_monthly, use_container_width=True)

# ----------------------------------
# Two Charts Side-by-Side
# ----------------------------------
left, right = st.columns(2)

with left:

    region_sales = (
        filtered_df
        .groupby("region")["sales"]
        .sum()
        .reset_index()
    )

    fig_region = px.bar(
        region_sales,
        x="region",
        y="sales",
        color="region",
        title="Sales by Region"
    )

    st.plotly_chart(fig_region, use_container_width=True)

with right:

    category_sales = (
        filtered_df
        .groupby("category")["sales"]
        .sum()
        .reset_index()
    )

    fig_category = px.pie(
        category_sales,
        names="category",
        values="sales",
        title="Sales by Category"
    )

    st.plotly_chart(fig_category, use_container_width=True)

# ----------------------------------
# Top 10 Products
# ----------------------------------
top_products = (
    filtered_df
    .groupby("product_name")["sales"]
    .sum()
    .nlargest(10)
    .reset_index()
)

fig_products = px.bar(
    top_products,
    x="sales",
    y="product_name",
    orientation="h",
    color="sales",
    title="Top 10 Products"
)

fig_products.update_layout(
    yaxis={"categoryorder": "total ascending"}
)

st.plotly_chart(fig_products, use_container_width=True)

# ----------------------------------
# Dataset
# ----------------------------------
st.subheader("Filtered Dataset")

st.dataframe(
    filtered_df,
    use_container_width=True
)
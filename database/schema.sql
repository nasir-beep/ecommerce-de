DROP TABLE IF EXISTS fact_sales CASCADE;
DROP TABLE IF EXISTS dim_customer CASCADE;
DROP TABLE IF EXISTS dim_product CASCADE;
DROP TABLE IF EXISTS dim_date CASCADE;

-- Customer Dimension

CREATE TABLE dim_customer (

    customer_id VARCHAR(20) PRIMARY KEY,

    customer_name TEXT,

    segment VARCHAR(50),

    country VARCHAR(100),

    city VARCHAR(100),

    state VARCHAR(100),

    postal_code VARCHAR(20),

    region VARCHAR(50)

);


-- Product Dimension

CREATE TABLE dim_product (

    product_id VARCHAR(30) PRIMARY KEY,

    category VARCHAR(100),

    sub_category VARCHAR(100),

    product_name TEXT

);


-- Date Dimension

CREATE TABLE dim_date (

    date_id DATE PRIMARY KEY,

    year INTEGER,

    quarter INTEGER,

    month INTEGER,

    day INTEGER

);


-- Sales Fact Table

CREATE TABLE fact_sales (

    sales_id SERIAL PRIMARY KEY,

    order_id VARCHAR(30),

    customer_id VARCHAR(20),

    product_id VARCHAR(30),

    order_date DATE,

    ship_date DATE,

    shipping_days INTEGER,

    sales NUMERIC(12,2),

    sales_category VARCHAR(20),

    FOREIGN KEY(customer_id)
        REFERENCES dim_customer(customer_id),

    FOREIGN KEY(product_id)
        REFERENCES dim_product(product_id),

    FOREIGN KEY(order_date)
        REFERENCES dim_date(date_id)

);
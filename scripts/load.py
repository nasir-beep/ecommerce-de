from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values

# -------------------------------------------------------
# Load Environment Variables
# -------------------------------------------------------

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

DATA_PATH = Path("data/processed/clean_sales.csv")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ecommerce_db")
DB_USER = os.getenv("DB_USER", "airflow")
DB_PASSWORD = os.getenv("DB_PASSWORD", "airflow")


# -------------------------------------------------------
# Database Connection
# -------------------------------------------------------

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


# -------------------------------------------------------
# ETL Load
# -------------------------------------------------------

def load_data():

    print("=" * 60)
    print("Loading Data Warehouse")
    print("=" * 60)

    print("\nReading cleaned dataset...")

    df = pd.read_csv(DATA_PATH)

    print(f"Rows Found: {len(df)}")

    # Convert dates
    df["order_date"] = pd.to_datetime(df["order_date"]).dt.date
    df["ship_date"] = pd.to_datetime(df["ship_date"]).dt.date

    print("\nConnecting to PostgreSQL...")

    conn = get_connection()
    cur = conn.cursor()

    print("Connected Successfully!\n")

    try:

        # ------------------------------------------
        # Clear Existing Data
        # ------------------------------------------

        print("Clearing warehouse tables...")

        cur.execute("""
            TRUNCATE TABLE
                fact_sales,
                dim_customer,
                dim_product,
                dim_date
            RESTART IDENTITY CASCADE;
        """)

        # ------------------------------------------
        # Customer Dimension
        # ------------------------------------------

        print("Loading Customer Dimension...")

        customers = (
            df[
                [
                    "customer_id",
                    "customer_name",
                    "segment",
                    "country",
                    "city",
                    "state",
                    "postal_code",
                    "region",
                ]
            ]
            .drop_duplicates()
            .values.tolist()
        )

        execute_values(
            cur,
            """
            INSERT INTO dim_customer(
                customer_id,
                customer_name,
                segment,
                country,
                city,
                state,
                postal_code,
                region
            )
            VALUES %s
            """,
            customers,
        )

        print(f"Loaded {len(customers)} Customers")

        # ------------------------------------------
        # Product Dimension
        # ------------------------------------------

        print("Loading Product Dimension...")

        products = (
            df[
                [
                    "product_id",
                    "category",
                    "sub_category",
                    "product_name",
                ]
            ]
            .drop_duplicates()
            .values.tolist()
        )

        execute_values(
            cur,
            """
            INSERT INTO dim_product(
                product_id,
                category,
                sub_category,
                product_name
            )
            VALUES %s
            """,
            products,
        )

        print(f"Loaded {len(products)} Products")

        # ------------------------------------------
        # Date Dimension
        # ------------------------------------------

        print("Loading Date Dimension...")

        dates = (
            df[
                [
                    "order_date",
                    "order_year",
                    "order_quarter",
                    "order_month",
                    "order_day",
                ]
            ]
            .drop_duplicates()
            .rename(
                columns={
                    "order_date": "date_id",
                    "order_year": "year",
                    "order_quarter": "quarter",
                    "order_month": "month",
                    "order_day": "day",
                }
            )
            .values.tolist()
        )

        execute_values(
            cur,
            """
            INSERT INTO dim_date(
                date_id,
                year,
                quarter,
                month,
                day
            )
            VALUES %s
            """,
            dates,
        )

        print(f"Loaded {len(dates)} Dates")

        # ------------------------------------------
        # Fact Table
        # ------------------------------------------

        print("Loading Fact Table...")

        facts = (
            df[
                [
                    "order_id",
                    "customer_id",
                    "product_id",
                    "order_date",
                    "ship_date",
                    "shipping_days",
                    "sales",
                    "sales_category",
                ]
            ]
            .values.tolist()
        )

        execute_values(
            cur,
            """
            INSERT INTO fact_sales(
                order_id,
                customer_id,
                product_id,
                order_date,
                ship_date,
                shipping_days,
                sales,
                sales_category
            )
            VALUES %s
            """,
            facts,
        )

        print(f"Loaded {len(facts)} Sales Records")

        # ------------------------------------------
        # Commit Transaction
        # ------------------------------------------

        conn.commit()

        print("\n" + "=" * 60)
        print("ETL LOAD COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:

        conn.rollback()

        print("\nERROR OCCURRED")
        print("-" * 60)
        print(e)
        print("-" * 60)

    finally:

        cur.close()
        conn.close()

        print("\nDatabase Connection Closed")


# -------------------------------------------------------
# Main
# -------------------------------------------------------

if __name__ == "__main__":
    load_data()
from pathlib import Path
import pandas as pd

RAW_DATA = Path("data/raw/train.csv")
PROCESSED_DATA = Path("data/processed/clean_sales.csv")


def transform_data():
    """Clean and transform the e-commerce sales dataset."""

    print("=" * 50)
    print("Loading raw dataset...")
    print("=" * 50)

    df = pd.read_csv(RAW_DATA)

    print(f"Original Shape: {df.shape}")

    #Standardize column names
    
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    #Convert dates
    
    df["order_date"] = pd.to_datetime(
        df["order_date"],
        dayfirst=True,
        errors="coerce"
    )

    df["ship_date"] = pd.to_datetime(
        df["ship_date"],
        dayfirst=True,
        errors="coerce"
    )

    print("\nInvalid Order Dates:", df["order_date"].isna().sum())
    print("Invalid Ship Dates:", df["ship_date"].isna().sum())
    
    df = df.dropna(subset=["order_date", "ship_date"])
    
    #Remove duplicates
    
    duplicates = df.duplicated().sum()

    if duplicates > 0:
        print(f"Removing {duplicates} duplicate rows...")
        df = df.drop_duplicates()

    #Handle missing values

    print("\nMissing Values Before Cleaning")
    print(df.isnull().sum())

    df = df.fillna("Unknown")

    print("\nMissing Values After Cleaning")
    print(df.isnull().sum())

    #Feature Engineering
    
    df["shipping_days"] = (
        df["ship_date"] - df["order_date"]
    ).dt.days

    df["order_year"] = df["order_date"].dt.year

    df["order_month"] = df["order_date"].dt.month

    df["order_day"] = df["order_date"].dt.day

    df["order_quarter"] = df["order_date"].dt.quarter

    df["sales_category"] = pd.cut(
        df["sales"],
        bins=[0, 100, 500, 1000, float("inf")],
        labels=["Low", "Medium", "High", "Very High"]
    )

  
    #Save cleaned data

    PROCESSED_DATA.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(PROCESSED_DATA, index=False)

    print("\nTransformation Complete!")

    print(f"Final Shape: {df.shape}")

    print(f"\nSaved cleaned data to:\n{PROCESSED_DATA}")

    return df


if __name__ == "__main__":
    cleaned_df = transform_data()

    print("\nFirst Five Rows")

    print(cleaned_df.head())
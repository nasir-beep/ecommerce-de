from pathlib import Path
import pandas as pd

DATA_PATH = Path("data/raw/train.csv")


def extract_data():
    """Read the raw CSV dataset."""

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    print("=" * 50)
    print("Dataset Loaded Successfully")
    print("=" * 50)
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    return df


if __name__ == "__main__":
    dataframe = extract_data()

    print("\nColumns")
    print(dataframe.columns.tolist())

    print("\nFirst Five Rows")
    print(dataframe.head())

    print("\nData Types")
    print(dataframe.dtypes)

    print("\nMissing Values")
    print(dataframe.isnull().sum())
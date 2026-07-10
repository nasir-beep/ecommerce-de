import pandas as pd

from etl.transform import clean_sales


def test_clean_sales():

    df = pd.DataFrame({
        "sales":[100,None,300]
    })

    cleaned = clean_sales(df)

    assert cleaned["sales"].isnull().sum()==0
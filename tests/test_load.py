from sqlalchemy import create_engine

def test_database_connection():

    engine = create_engine(
        "postgresql://airflow:airflow@localhost:5433/ecommerce_db"
    )

    conn = engine.connect()

    assert conn.closed == False

    conn.close()
import os
import pandas as pd
from sqlalchemy import create_engine
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password@127.0.0.1:5433/retail_db")

def load_data_to_postgres():
    print(f"Connecting to database: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    
    # 1. Execute schema.sql to create tables
    with engine.connect() as conn:
        with open('storage/schema.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
            for statement in sql.split(';'):
                if statement.strip():
                    from sqlalchemy import text
                    conn.execute(text(statement))
            conn.commit()
        print("Schema loaded successfully.")

    # 2. Load Customers
    try:
        print("Loading Customers...")
        df_customers = pd.read_parquet('data/processed/clean_customers.parquet')
        df_customers.to_sql('customers', engine, if_exists='append', index=False)
        print(f"Loaded {len(df_customers)} customers.")
    except Exception as e:
        print(f"Error loading customers: {e}")

    # 3. Load Product Metrics
    try:
        print("Loading Product Metrics...")
        df_products = pd.read_parquet('data/processed/product_metrics.parquet')
        df_products.to_sql('product_metrics', engine, if_exists='append', index=False)
        print(f"Loaded {len(df_products)} products.")
    except Exception as e:
        print(f"Error loading products: {e}")

    # 4. Load Orders
    try:
        print("Loading Orders...")
        df_orders = pd.read_parquet('data/processed/clean_orders.parquet')
        # Cast dates and arrays if necessary
        df_orders['order_date'] = pd.to_datetime(df_orders['order_date'])
        df_orders['delivery_date'] = pd.to_datetime(df_orders['delivery_date'])
        df_orders.to_sql('orders', engine, if_exists='append', index=False)
        print(f"Loaded {len(df_orders)} orders.")
    except Exception as e:
        print(f"Error loading orders: {e}")

if __name__ == "__main__":
    load_data_to_postgres()

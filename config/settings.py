from pathlib import Path

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Data folders
DATA_DIR = BASE_DIR / "data"

RAW_DATA_DIR = DATA_DIR / "raw" / "ecommerce"
SAMPLE_DATA_DIR = DATA_DIR / "sample"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Dataset files
CUSTOMERS_DATA = RAW_DATA_DIR / "customers.csv"
ORDERS_DATA = RAW_DATA_DIR / "orders.csv"
PRODUCT_SUMMARY_DATA = RAW_DATA_DIR / "product_summary.csv"
MONTHLY_REVENUE_DATA = RAW_DATA_DIR / "monthly_revenue.csv"

# Sample
SAMPLE_ORDERS_DATA = SAMPLE_DATA_DIR / "sample_orders.csv"

# Processed
CLEAN_ORDERS_DATA = PROCESSED_DATA_DIR / "clean_orders.parquet"
CLEAN_CUSTOMERS_DATA = PROCESSED_DATA_DIR / "clean_customers.parquet"

print("Project root:", BASE_DIR)
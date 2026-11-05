from pathlib import Path
import pandas as pd
import sys

# =========================================================
# 1. CẤU HÌNH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(BASE_DIR))
from config.settings import (
    SAMPLE_ORDERS_DATA, 
    CUSTOMERS_DATA, 
    CLEAN_ORDERS_DATA,
    CLEAN_CUSTOMERS_DATA
)

PROCESSED_DIR = CLEAN_ORDERS_DATA.parent
REPORT_DIR = BASE_DIR / "docs" / "preprocessing"
REPORT_TXT = REPORT_DIR / "cleaning_summary.txt"


# =========================================================
# 2. TẠO THƯ MỤC
# =========================================================

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# 3. KIỂM TRA INPUT
# =========================================================

if not SAMPLE_ORDERS_DATA.exists() or not CUSTOMERS_DATA.exists():
    raise FileNotFoundError(
        f"Không tìm thấy file input. Hãy đảm bảo đã chạy create_sample.py và tải đủ raw data."
    )

print("=" * 70)
print("CLEAN E-COMMERCE DATA (2020-2026)")
print("=" * 70)


# =========================================================
# 4. ĐỌC DATA
# =========================================================

orders = pd.read_csv(SAMPLE_ORDERS_DATA)
customers = pd.read_csv(CUSTOMERS_DATA)

orders_before = len(orders)
customers_before = len(customers)

print(f"\nSố dòng orders ban đầu: {orders_before:,}")
print(f"Số dòng customers ban đầu: {customers_before:,}")


# =========================================================
# 5. CHUẨN HÓA ORDERS
# =========================================================

# 5.1. Convert datetime
orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce", utc=True)
orders["delivery_date"] = pd.to_datetime(orders["delivery_date"], errors="coerce", utc=True)

# 5.2. Fill missing ratings
orders["customer_rating"] = pd.to_numeric(orders["customer_rating"], errors="coerce")
# Fill missing rating with the median or 0, we'll just fill with 0 for now
orders["customer_rating"] = orders["customer_rating"].fillna(0)

# 5.3. Handle duplicates
orders = orders.drop_duplicates(subset=["order_id"])

# 5.4 Sort by date
orders = orders.sort_values(by="order_date").reset_index(drop=True)

# =========================================================
# 6. CHUẨN HÓA CUSTOMERS
# =========================================================

customers["registration_date"] = pd.to_datetime(customers["registration_date"], errors="coerce", utc=True)
customers = customers.drop_duplicates(subset=["customer_id"])


# =========================================================
# 7. MERGE DATA TÙY CHỌN
# =========================================================

# Đôi khi ta cần phân tích tập order có chứa luôn thông tin customer (VD: quốc gia, tuổi)
merged_orders = orders.merge(
    customers[["customer_id", "country", "age", "gender", "membership_tier", "churned"]], 
    on="customer_id", 
    how="left"
)

# =========================================================
# 8. THỐNG KÊ SAU CLEAN
# =========================================================

orders_after = len(merged_orders)
customers_after = len(customers)

# =========================================================
# 9. LƯU PARQUET
# =========================================================

merged_orders.to_parquet(
    CLEAN_ORDERS_DATA,
    index=False,
    engine="pyarrow"
)

customers.to_parquet(
    CLEAN_CUSTOMERS_DATA,
    index=False,
    engine="pyarrow"
)


# =========================================================
# 10. LƯU REPORT TXT
# =========================================================

with open(REPORT_TXT, "w", encoding="utf-8") as f:
    f.write("DATA CLEANING SUMMARY\n")
    f.write("=" * 50 + "\n")
    f.write(f"Orders before: {orders_before:,}\n")
    f.write(f"Orders after: {orders_after:,}\n")
    f.write(f"Customers before: {customers_before:,}\n")
    f.write(f"Customers after: {customers_after:,}\n")
    f.write(f"Missing ratings in orders: {merged_orders['customer_rating'].isna().sum()}\n")


print("\n" + "=" * 70)
print("CLEAN DATA THÀNH CÔNG")
print("=" * 70)
print(f"Đã lưu: {CLEAN_ORDERS_DATA}")
print(f"Đã lưu: {CLEAN_CUSTOMERS_DATA}")
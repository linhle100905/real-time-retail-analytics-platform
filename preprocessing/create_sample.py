from pathlib import Path
import pandas as pd
import sys

# =========================================================
# 1. CẤU HÌNH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Thêm BASE_DIR vào sys.path để import từ config
sys.path.append(str(BASE_DIR))

from config.settings import ORDERS_DATA, SAMPLE_ORDERS_DATA

INPUT_FILE = ORDERS_DATA
OUTPUT_FILE = SAMPLE_ORDERS_DATA
OUTPUT_DIR = OUTPUT_FILE.parent

# Số dòng sử dụng cho bản demo (orders.csv có 25k dòng nên ta load hết)
SAMPLE_SIZE = 100_000


# =========================================================
# 2. TẠO THƯ MỤC OUTPUT
# =========================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================================
# 3. KIỂM TRA FILE INPUT
# =========================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Không tìm thấy dataset:\n{INPUT_FILE}"
    )


print("=" * 70)
print("CREATE SAMPLE DATA (ORDERS)")
print("=" * 70)

print("\nInput:")
print(INPUT_FILE)

print(
    f"\nĐang đọc tối đa {SAMPLE_SIZE:,} dòng..."
)


# =========================================================
# 4. ĐỌC SAMPLE
# =========================================================

df = pd.read_csv(
    INPUT_FILE,
    nrows=SAMPLE_SIZE
)


# =========================================================
# 5. KIỂM TRA
# =========================================================

print("\nKích thước sample:")
print(df.shape)

print("\nCác cột:")
print(df.columns.tolist())


# =========================================================
# 6. LƯU SAMPLE
# =========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)


print("\n" + "=" * 70)
print("TẠO SAMPLE THÀNH CÔNG")
print("=" * 70)

print("\nOutput:")
print(OUTPUT_FILE)

print(
    f"\nSố dòng đã lưu: {len(df):,}"
)
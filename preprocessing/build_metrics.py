from pathlib import Path

import pandas as pd


# =========================================================
# 1. CẤU HÌNH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "clean_events.parquet"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "processed"
    / "product_metrics.parquet"
)

REPORT_DIR = (
    BASE_DIR
    / "docs"
    / "analytics"
)

REPORT_FILE = (
    REPORT_DIR
    / "analytics_summary.txt"
)


# =========================================================
# 2. KIỂM TRA INPUT
# =========================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Không tìm thấy:\n{INPUT_FILE}\n"
        "Hãy chạy clean_data.py trước."
    )


REPORT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


print("=" * 70)
print("BUILD RETAIL ANALYTICS METRICS")
print("=" * 70)


# =========================================================
# 3. ĐỌC DỮ LIỆU
# =========================================================

df = pd.read_parquet(
    INPUT_FILE
)

print(
    f"\nSố event: {len(df):,}"
)


# =========================================================
# 4. KPI CƠ BẢN
# =========================================================

views = (
    df["event_type"] == "view"
).sum()

carts = (
    df["event_type"] == "cart"
).sum()

remove_from_cart = (
    df["event_type"] == "remove_from_cart"
).sum()

purchases = (
    df["event_type"] == "purchase"
).sum()

unique_users = (
    df["user_id"]
    .nunique()
)

unique_products = (
    df["product_id"]
    .nunique()
)

unique_sessions = (
    df["user_session"]
    .dropna()
    .nunique()
)


# =========================================================
# 5. PURCHASE VALUE
# =========================================================

purchase_df = df[
    df["event_type"] == "purchase"
].copy()

purchase_value = (
    purchase_df["price"]
    .sum()
)


# =========================================================
# 6. EVENT-LEVEL CONVERSION
# =========================================================

event_conversion = (
    purchases / views * 100
    if views > 0
    else 0
)


# =========================================================
# 7. SESSION-LEVEL CONVERSION
# =========================================================

valid_sessions = df.dropna(
    subset=["user_session"]
)

view_sessions = (
    valid_sessions.loc[
        valid_sessions["event_type"] == "view",
        "user_session"
    ]
    .nunique()
)

cart_sessions = (
    valid_sessions.loc[
        valid_sessions["event_type"] == "cart",
        "user_session"
    ]
    .nunique()
)

purchase_sessions = (
    valid_sessions.loc[
        valid_sessions["event_type"] == "purchase",
        "user_session"
    ]
    .nunique()
)

session_conversion = (
    purchase_sessions
    / view_sessions
    * 100
    if view_sessions > 0
    else 0
)


# =========================================================
# 8. TẠO PRODUCT METRICS
# =========================================================

# Tạo các cột đánh dấu event
df["is_view"] = (
    df["event_type"] == "view"
).astype(int)

df["is_cart"] = (
    df["event_type"] == "cart"
).astype(int)

df["is_remove"] = (
    df["event_type"]
    == "remove_from_cart"
).astype(int)

df["is_purchase"] = (
    df["event_type"] == "purchase"
).astype(int)

df["purchase_value"] = 0.0

df.loc[
    df["event_type"] == "purchase",
    "purchase_value"
] = df.loc[
    df["event_type"] == "purchase",
    "price"
]


# =========================================================
# 9. GROUP THEO PRODUCT
# =========================================================

product_metrics = (
    df.groupby(
        "product_id",
        as_index=False
    )
    .agg(
        views=("is_view", "sum"),
        carts=("is_cart", "sum"),
        removes=("is_remove", "sum"),
        purchases=("is_purchase", "sum"),
        purchase_value=(
            "purchase_value",
            "sum"
        ),
        unique_users=(
            "user_id",
            "nunique"
        ),
        latest_price=(
            "price",
            "last"
        )
    )
)


# =========================================================
# 10. CONVERSION THEO PRODUCT
# =========================================================

product_metrics[
    "conversion_rate"
] = 0.0

mask = (
    product_metrics["views"] > 0
)

product_metrics.loc[
    mask,
    "conversion_rate"
] = (
    product_metrics.loc[
        mask,
        "purchases"
    ]
    /
    product_metrics.loc[
        mask,
        "views"
    ]
    * 100
)


# =========================================================
# 11. THÊM BRAND + CATEGORY
# =========================================================

product_info = (
    df[
        [
            "product_id",
            "brand",
            "category_code"
        ]
    ]
    .drop_duplicates(
        subset=["product_id"],
        keep="last"
    )
)

product_metrics = (
    product_metrics.merge(
        product_info,
        on="product_id",
        how="left"
    )
)


# =========================================================
# 12. LƯU PRODUCT METRICS
# =========================================================

product_metrics.to_parquet(
    OUTPUT_FILE,
    index=False
)


# =========================================================
# 13. TOP PRODUCTS
# =========================================================

top_viewed = (
    product_metrics
    .sort_values(
        "views",
        ascending=False
    )
    .head(10)
)

top_purchased = (
    product_metrics
    .sort_values(
        "purchases",
        ascending=False
    )
    .head(10)
)


# =========================================================
# 14. PRINT KPI
# =========================================================

print("\n" + "=" * 70)
print("RETAIL KPI")
print("=" * 70)

print(
    f"Views               : {views:,}"
)

print(
    f"Carts               : {carts:,}"
)

print(
    f"Remove from cart    : {remove_from_cart:,}"
)

print(
    f"Purchases           : {purchases:,}"
)

print(
    f"Unique users        : {unique_users:,}"
)

print(
    f"Unique products     : {unique_products:,}"
)

print(
    f"Unique sessions     : {unique_sessions:,}"
)

print(
    f"Purchase value      : {purchase_value:,.2f}"
)

print(
    f"Event conversion    : {event_conversion:.2f}%"
)

print(
    f"Session conversion  : {session_conversion:.2f}%"
)


# =========================================================
# 15. LƯU REPORT
# =========================================================

with open(
    REPORT_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "RETAIL ANALYTICS SUMMARY\n"
    )

    f.write(
        "=" * 50 + "\n"
    )

    f.write(
        f"Total events: {len(df):,}\n"
    )

    f.write(
        f"Views: {views:,}\n"
    )

    f.write(
        f"Carts: {carts:,}\n"
    )

    f.write(
        f"Remove from cart: "
        f"{remove_from_cart:,}\n"
    )

    f.write(
        f"Purchases: {purchases:,}\n"
    )

    f.write(
        f"Unique users: "
        f"{unique_users:,}\n"
    )

    f.write(
        f"Unique products: "
        f"{unique_products:,}\n"
    )

    f.write(
        f"Unique sessions: "
        f"{unique_sessions:,}\n"
    )

    f.write(
        f"Purchase value proxy: "
        f"{purchase_value:,.2f}\n"
    )

    f.write(
        f"Event conversion: "
        f"{event_conversion:.2f}%\n"
    )

    f.write(
        f"Session conversion: "
        f"{session_conversion:.2f}%\n"
    )


print("\n" + "=" * 70)
print("TOP 10 SẢN PHẨM ĐƯỢC XEM")
print("=" * 70)

print(
    top_viewed[
        [
            "product_id",
            "views",
            "carts",
            "purchases"
        ]
    ]
)


print("\n" + "=" * 70)
print("TOP 10 SẢN PHẨM ĐƯỢC MUA")
print("=" * 70)

print(
    top_purchased[
        [
            "product_id",
            "views",
            "carts",
            "purchases"
        ]
    ]
)


print("\n" + "=" * 70)
print("BUILD METRICS THÀNH CÔNG")
print("=" * 70)

print("\nProduct metrics:")
print(OUTPUT_FILE)

print("\nReport:")
print(REPORT_FILE)
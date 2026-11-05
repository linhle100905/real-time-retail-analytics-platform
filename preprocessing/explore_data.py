from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import sys

# =========================================================
# 1. CẤU HÌNH
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from config.settings import ORDERS_DATA, CUSTOMERS_DATA

OUTPUT_DIR = BASE_DIR / "docs" / "eda"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =========================================================
# 2. ĐỌC DỮ LIỆU
# =========================================================

print("=" * 70)
print("EDA - E-COMMERCE ORDERS & CUSTOMERS")
print("=" * 70)

orders = pd.read_csv(ORDERS_DATA)
customers = pd.read_csv(CUSTOMERS_DATA)

print("\nĐọc dữ liệu thành công!")


# =========================================================
# 3. THÔNG TIN CƠ BẢN
# =========================================================

print("\n" + "=" * 70)
print("1. TỔNG QUAN")
print("=" * 70)

print(f"Tổng số đơn hàng: {len(orders):,}")
print(f"Tổng số khách hàng: {len(customers):,}")

total_revenue = orders["total_amount_usd"].sum()
print(f"Tổng doanh thu: ${total_revenue:,.2f}")


# =========================================================
# 4. KHOẢNG THỜI GIAN
# =========================================================

orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")

print("\n" + "=" * 70)
print("2. THỜI GIAN GIAO DỊCH")
print("=" * 70)
print(f"Bắt đầu: {orders['order_date'].min()}")
print(f"Kết thúc: {orders['order_date'].max()}")


# =========================================================
# 5. TOP CATEGORY
# =========================================================

top_categories = orders["category"].value_counts().head(10)
print("\n" + "=" * 70)
print("3. TOP 10 DANH MỤC")
print("=" * 70)
print(top_categories)

top_categories.to_csv(OUTPUT_DIR / "top_categories.csv", header=["orders"], encoding="utf-8-sig")

plt.figure(figsize=(10, 6))
top_categories.sort_values().plot(kind="barh")
plt.title("Top 10 Categories by Number of Orders")
plt.xlabel("Orders")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "top_categories.png", dpi=200)
plt.close()


# =========================================================
# 6. THỐNG KÊ DOANH THU THEO THÁNG
# =========================================================

revenue_by_month = orders.groupby(orders["order_date"].dt.to_period("M"))["total_amount_usd"].sum()

plt.figure(figsize=(12, 6))
revenue_by_month.plot(kind="line", marker="o")
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue (USD)")
plt.grid(True)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "monthly_revenue_trend.png", dpi=200)
plt.close()


# =========================================================
# 7. PHÂN TÍCH CHURN TỪ BẢNG CUSTOMERS
# =========================================================

churn_counts = customers["churned"].value_counts()
print("\n" + "=" * 70)
print("4. TỶ LỆ RỜI BỎ (CHURN)")
print("=" * 70)
print(churn_counts)

plt.figure(figsize=(6, 6))
churn_counts.plot(kind="pie", autopct="%1.1f%%", colors=["#66b3ff", "#ff9999"])
plt.title("Customer Churn Status")
plt.ylabel("")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "churn_status.png", dpi=200)
plt.close()


# =========================================================
# 8. LƯU SUMMARY
# =========================================================

summary_path = OUTPUT_DIR / "eda_summary.txt"

with open(summary_path, "w", encoding="utf-8") as f:
    f.write("EDA SUMMARY\n")
    f.write("=" * 50 + "\n")
    f.write(f"Total Orders: {len(orders):,}\n")
    f.write(f"Total Customers: {len(customers):,}\n")
    f.write(f"Total Revenue: ${total_revenue:,.2f}\n")
    f.write(f"Churn Rate: {(churn_counts.get(1, 0) / len(customers) * 100):.2f}%\n")


print("\n" + "=" * 70)
print("EDA HOÀN THÀNH")
print("=" * 70)
print(f"Kết quả được lưu tại: {OUTPUT_DIR}")
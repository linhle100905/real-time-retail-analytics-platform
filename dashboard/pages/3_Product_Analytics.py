from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# STYLE
# =========================================================

DASHBOARD_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(DASHBOARD_DIR))

from style import apply_style

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Product Analytics",
    page_icon="📊",
    layout="wide"
)

apply_style()

# =========================================================
# PATH
# =========================================================

BASE_DIR = Path(__file__).resolve().parents[2]
ORDERS_FILE = BASE_DIR / "data" / "processed" / "clean_orders.parquet"

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():
    return pd.read_parquet(ORDERS_FILE)

if not ORDERS_FILE.exists():
    st.error("Không tìm thấy clean_orders.parquet. Hãy chạy clean_data.py trước.")
    st.stop()

df = load_data()

@st.cache_data
def get_product_metrics(orders_df):
    metrics = orders_df.groupby(["product_name", "category"]).agg(
        total_quantity=("quantity", "sum"),
        total_revenue=("subtotal_usd", "sum"),
        avg_rating=("customer_rating", lambda x: x[x > 0].mean()),
        total_orders=("order_id", "nunique")
    ).reset_index()
    metrics["avg_rating"] = metrics["avg_rating"].fillna(0).round(2)
    return metrics

product_metrics = get_product_metrics(df)

# =========================================================
# TITLE
# =========================================================

st.title("🛒 Phân tích Sản phẩm & Ngành hàng")
st.caption("Thống kê chi tiết doanh thu, số lượng bán ra theo từng sản phẩm và danh mục.")

# =========================================================
# TOP PRODUCTS (FETCH FROM FASTAPI)
# =========================================================
import requests

st.markdown("## 🏆 Top Sản phẩm")

metric_mapping = {
    "Doanh thu (Revenue)": "total_revenue",
    "Số lượng bán (Quantity)": "total_quantity",
    "Số lượng đơn (Orders)": "total_orders"
}

selected_metric = st.selectbox(
    "Xếp hạng sản phẩm theo:",
    options=list(metric_mapping.keys())
)

sort_col = metric_mapping[selected_metric]

try:
    response = requests.get(f"http://127.0.0.1:8000/api/analytics/top-products?limit=10&sort_by={sort_col}", timeout=3)
    if response.status_code == 200:
        top_products = pd.DataFrame(response.json())
    else:
        raise Exception(f"API trả về status {response.status_code}")
except Exception as e:
    # Dự phòng thông minh: Nếu chưa bật FastAPI, lấy dữ liệu trực tiếp từ dataframe đã tính toán
    top_products = product_metrics.sort_values(sort_col, ascending=False).head(10)

fig_product = px.bar(
    top_products,
    x="product_name",
    y=sort_col,
    color="category",
    hover_data=["total_revenue", "total_quantity", "avg_rating"],
    title=f"Top 10 Sản phẩm theo {selected_metric}"
)

st.plotly_chart(fig_product, use_container_width=True)

st.divider()

# =========================================================
# CATEGORY & RATING ANALYTICS
# =========================================================

col1, col2 = st.columns(2)

with col1:
    st.markdown("## 🏷️ Top Ngành hàng (Category)")
    category_rev = df.groupby("category")["subtotal_usd"].sum().reset_index()
    category_rev = category_rev.sort_values("subtotal_usd", ascending=False).head(10)
    
    fig_category = px.bar(
        category_rev,
        x="subtotal_usd",
        y="category",
        orientation="h",
        title="Top 10 Ngành hàng mang lại doanh thu cao nhất",
        labels={"subtotal_usd": "Doanh thu (USD)", "category": "Ngành hàng"}
    )
    fig_category.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_category, use_container_width=True)

with col2:
    st.markdown("## ⭐ Phân bổ Đánh giá (Rating)")
    valid_ratings = df[df["customer_rating"] > 0]["customer_rating"]
    
    fig_rating = px.histogram(
        valid_ratings, 
        x="customer_rating",
        nbins=5,
        title="Số lượng đánh giá theo số sao (1-5)",
        labels={"customer_rating": "Điểm đánh giá (Sao)"}
    )
    st.plotly_chart(fig_rating, use_container_width=True)

st.divider()

# =========================================================
# PRODUCT TABLE
# =========================================================

st.markdown("## 📋 Bảng Chi tiết Sản phẩm")

# Format data for display
display_df = product_metrics.sort_values("total_revenue", ascending=False).copy()
display_df = display_df.rename(columns={
    "product_name": "Tên sản phẩm",
    "category": "Ngành hàng",
    "total_quantity": "SL đã bán",
    "total_revenue": "Doanh thu ($)",
    "avg_rating": "Đánh giá TB (Sao)",
    "total_orders": "Tổng số đơn"
})

st.dataframe(
    display_df,
    use_container_width=True,
    height=400
)
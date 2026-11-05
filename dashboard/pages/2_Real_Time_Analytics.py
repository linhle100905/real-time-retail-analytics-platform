import streamlit as st
import pandas as pd
import json
import time
from kafka import KafkaConsumer
from collections import deque
import plotly.express as px

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Real-Time Analytics",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Real-Time Analytics")
st.caption("Trang này tự động cập nhật dữ liệu luồng Đơn hàng (Orders) đang được bắn từ Kafka.")
st.info("⏱️ Tốc độ luồng dữ liệu hiện tại: 1 đơn hàng mới mỗi 20 giây (20 giây / 1 đơn).")

# =========================================================
# INIT KAFKA CONSUMER
# =========================================================
KAFKA_TOPIC = "ecommerce_orders"
KAFKA_SERVER = "127.0.0.1:9092"

# Dùng st.cache_resource để KafkaConsumer duy trì kết nối
@st.cache_resource
def get_kafka_consumer():
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=KAFKA_SERVER,
            auto_offset_reset='earliest',  # Đọc từ đầu để hiện ngay các đơn hàng đã có trong topic
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=1000,
            request_timeout_ms=10000,
            api_version=(2, 0, 2)
        )
        return consumer
    except Exception as e:
        return None

consumer = get_kafka_consumer()
if consumer is None:
    st.error("❌ Không thể kết nối tới Kafka tại 127.0.0.1:9092. Hãy đảm bảo Docker Kafka đang chạy và refresh lại trang.")
    st.cache_resource.clear()
    st.stop()

# =========================================================
# STATE MANAGER (Lưu data tạm thời vào bộ nhớ)
# =========================================================
# Chúng ta giữ lại tối đa 50 đơn hàng gần nhất để vẽ biểu đồ cho nhẹ
if "live_orders" not in st.session_state:
    st.session_state.live_orders = deque(maxlen=50)

if "total_live_revenue" not in st.session_state:
    st.session_state.total_live_revenue = 0.0

if "total_live_count" not in st.session_state:
    st.session_state.total_live_count = 0


# =========================================================
# PLACEHOLDERS (Khu vực chứa biểu đồ sẽ được tự động refresh)
# =========================================================
kpi_placeholder = st.empty()
chart_placeholder = st.empty()
table_placeholder = st.empty()

# Nút bật/tắt luồng
run_stream = st.sidebar.checkbox("Bật theo dõi Real-time", value=True)

if not run_stream:
    st.warning("Đã tạm dừng theo dõi luồng dữ liệu.")
else:
    if consumer is None:
        st.stop()
        
    st.sidebar.success("✅ Đang kết nối luồng Kafka...")
    
    # Vòng lặp cập nhật Real-time
    while run_stream:
        # Lấy các messages có sẵn trong hàng đợi (đợi tối đa 1 giây)
        messages = consumer.poll(timeout_ms=1000)
        
        new_events = False
        for tp, msgs in messages.items():
            for msg in msgs:
                event = msg.value
                # Thêm vào danh sách bộ nhớ
                st.session_state.live_orders.append(event)
                st.session_state.total_live_revenue += float(event.get("subtotal_usd", 0))
                st.session_state.total_live_count += 1
                new_events = True
        
        # Chỉ vẽ lại biểu đồ khi có dữ liệu mới để chống nháy màn hình
        if new_events or not st.session_state.get('drawn', False):
            st.session_state.drawn = True
            df_live = pd.DataFrame(list(st.session_state.live_orders))
            
            # 1. Cập nhật KPI
            with kpi_placeholder.container():
                col1, col2, col3 = st.columns(3)
                col1.metric("🔴 Đơn hàng đã nhận", f"{st.session_state.total_live_count}")
                col2.metric("💰 Doanh thu Real-time", f"${st.session_state.total_live_revenue:,.2f}")
                
                # Tính giá trị trung bình đơn
                avg_val = st.session_state.total_live_revenue / st.session_state.total_live_count if st.session_state.total_live_count > 0 else 0
                col3.metric("💳 Giá trị TB/Đơn", f"${avg_val:,.2f}")
            
            # 2. Cập nhật Biểu đồ
            with chart_placeholder.container():
                if not df_live.empty:
                    # Gom nhóm doanh thu theo Category
                    cat_live = df_live.groupby("category")["subtotal_usd"].sum().reset_index()
                    fig = px.bar(
                        cat_live, 
                        x="category", 
                        y="subtotal_usd", 
                        title="Doanh thu theo Ngành hàng (50 đơn gần nhất)",
                        labels={"subtotal_usd": "Doanh thu (USD)", "category": "Ngành hàng"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # 3. Cập nhật Bảng dữ liệu thô
            with table_placeholder.container():
                st.markdown("### 🛒 Danh sách Đơn hàng mới nhất")
                if not df_live.empty:
                    # Hiển thị 10 đơn mới nhất (đảo ngược list)
                    st.dataframe(
                        df_live[["order_id", "product_name", "category", "subtotal_usd", "order_date"]].tail(10).iloc[::-1],
                        use_container_width=True
                    )
        
        # Nghỉ 1 giây rồi vòng lặp tự chạy tiếp (không dùng st.rerun để tránh nháy giật web)
        time.sleep(1)

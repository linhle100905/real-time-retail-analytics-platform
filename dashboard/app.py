import streamlit as st

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Retail Intelligence Platform",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# TITLE
# =========================================================
st.title("🛒 Retail Intelligence Platform")
st.subheader("Real-Time Retail Analytics + Machine Learning + RAG Platform")

st.info(
    """
    Hệ thống phân tích bán lẻ thông minh đa tầng phục vụ đồ án Chuyên đề Công nghệ thông tin:
    Xử lý luồng dữ liệu thời gian thực (Kafka/Spark), lưu trữ kho dữ liệu (PostgreSQL), 
    hệ thống gợi ý sản phẩm cá nhân hóa (Collaborative Filtering Recommender), 
    và trợ lý AI thông minh hỏi đáp danh mục sản phẩm & chính sách (RAG / GPT-4o-mini).
    """
)

# =========================================================
# SYSTEM ARCHITECTURE FLOW
# =========================================================
st.markdown("### 🏛️ Kiến trúc hệ thống toàn diện")

st.code(
    """
Raw Ecommerce Events (Orders / CSV / Parquet)
      ↓
Kafka Producer (Real-time Simulation)
      ↓
Apache Kafka Broker (Topic: ecommerce_orders)
      ↓
PySpark / Stream Consumer
      ↓
Data Lake (Delta/Parquet) + Serving Database (PostgreSQL)
      ↓
Machine Learning (Item-Based CF) + Vector DB (Qdrant & Local Dense) + LLM (GPT-4o-mini)
      ↓
FastAPI Backend (Port: 8000)
      ↓
Streamlit Dashboard Portal (Port: 8501)
    """,
    language=None
)

# =========================================================
# CURRENT SYSTEM STATUS
# =========================================================
st.markdown("### 🚀 Trạng thái các phân hệ hệ thống")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.success("✅ Database & Postgres")

with col2:
    st.success("✅ FastAPI Backend")

with col3:
    st.success("✅ Kafka Streaming")

with col4:
    st.success("✅ ML Recommendations")

with col5:
    st.success("✅ AI & RAG Assistant")

st.caption("🎉 Toàn bộ 5 phân hệ kiến trúc đã được hoàn thiện 100% và sẵn sàng cho buổi demo báo cáo đồ án.")

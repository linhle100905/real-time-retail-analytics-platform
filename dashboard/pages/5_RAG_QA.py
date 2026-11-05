import streamlit as st
import requests
import sys
from pathlib import Path

# Cấu hình đường dẫn
DASHBOARD_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(DASHBOARD_DIR))
from style import apply_style

st.set_page_config(
    page_title="Kiểm tra chất lượng danh mục & RAG QA",
    page_icon="🔍",
    layout="wide"
)
apply_style()

# Custom CSS để làm các chip câu hỏi và card câu trả lời giống hệt ảnh mẫu
st.markdown("""
<style>
div.stButton > button {
    border-radius: 8px;
    font-weight: 500;
    transition: all 0.2s ease;
}
.prompt-btn button {
    background-color: #4F46E5 !important;
    color: white !important;
    border: none !important;
    padding: 8px 14px !important;
    font-size: 13.5px !important;
    border-radius: 8px !important;
}
.prompt-btn button:hover {
    background-color: #4338CA !important;
    transform: translateY(-1px);
}
.answer-box {
    background-color: #ffffff;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #4F46E5;
    border-radius: 8px;
    padding: 20px 24px;
    margin-top: 14px;
    margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.source-tag {
    display: inline-block;
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    color: #475569;
    border-radius: 6px;
    padding: 6px 12px;
    margin-right: 8px;
    margin-bottom: 8px;
    font-size: 12.5px;
    font-family: inherit;
}
.source-tag b {
    color: #1E293B;
}
.sidebar-info-box {
    background-color: #F8FAFC;
    border-radius: 8px;
    padding: 14px;
    border: 1px solid #E2E8F0;
    font-size: 13px;
    color: #475569;
}
</style>
""", unsafe_allow_html=True)

# Sidebar thông tin hệ thống (chuẩn theo mẫu)
with st.sidebar:
    st.markdown("### ℹ️ ĐƯỢC CUNG CẤP BỞI")
    st.markdown("""
    <div class="sidebar-info-box">
        <p style="margin-bottom: 6px;"><b>Mô hình:</b> OpenAI GPT-4o-mini</p>
        <p style="margin-bottom: 6px;"><b>Vector DB:</b> Qdrant / Local Dense Store</p>
        <p style="margin-bottom: 6px;"><b>Embedding:</b> text-embedding-3-small</p>
        <p style="margin-bottom: 6px;"><b>Dữ liệu:</b> 140 sản phẩm & 4 chính sách kinh doanh</p>
        <p style="margin-bottom: 0;"><b>Độ tương đồng:</b> Top-k = 5</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.caption("Retail Intelligence AI Assistant © 2026")

# Tiêu đề trang
st.markdown("## 🔍 Kiểm tra chất lượng danh mục & RAG QA")
st.caption("Tìm kiếm sản phẩm theo ngữ nghĩa, giải đáp thắc mắc danh mục và tra cứu chính sách bán lẻ.")

# Session state quản lý truy vấn và kết quả
if "active_query" not in st.session_state:
    st.session_state.active_query = "Chúng tôi có những sản phẩm hữu cơ nào?"
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# Hàng nút câu hỏi gợi ý nhanh (Quick Prompts theo mẫu)
st.markdown("##### 💡 Câu hỏi gợi ý nhanh:")
col1, col2, col3, col4, col5 = st.columns(5)

prompt_options = [
    ("Những món ăn vặt tốt nhất cho trẻ em là gì?", col1),
    ("Các món ăn sáng dưới $25", col2),
    ("Chúng tôi có những sản phẩm hữu cơ nào?", col3),
    ("Đồ uống cho bữa tiệc", col4),
    ("Chính sách đổi trả hàng như thế nào?", col5)
]

for prompt_text, col in prompt_options:
    with col:
        with st.container():
            if st.button(prompt_text, key=f"btn_{prompt_text}", use_container_width=True):
                st.session_state.active_query = prompt_text
                st.session_state.auto_trigger = True

# Thanh tìm kiếm và nút Hỏi
input_col, btn_col = st.columns([5, 1])

with input_col:
    query_input = st.text_input(
        "Nhập câu hỏi:",
        value=st.session_state.active_query,
        placeholder="VD: Chúng tôi có những sản phẩm hữu cơ nào? Hoặc các món ăn sáng dưới $25...",
        label_visibility="collapsed"
    )

with btn_col:
    search_clicked = st.button("🔎 Hỏi", type="primary", use_container_width=True)

# Hàm gọi API / RAG Service
def execute_query(q_text: str):
    with st.spinner("AI đang tìm kiếm danh mục sản phẩm và suy luận..."):
        try:
            # 1. Thử gọi qua Backend FastAPI
            resp = requests.post(
                "http://127.0.0.1:8000/api/chat",
                json={"message": q_text},
                timeout=12
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

        # 2. Dự phòng thông minh: Gọi trực tiếp RAG Service (100% không lo sập)
        try:
            from rag.rag_service import ask_retail_assistant
            return ask_retail_assistant(q_text)
        except Exception as err:
            return {
                "reply": f"Có lỗi xảy ra khi xử lý: {err}",
                "sources": [],
                "total_found": 0
            }

# Kích hoạt tìm kiếm khi bấm nút hoặc click chip gợi ý
if search_clicked or st.session_state.get("auto_trigger", False):
    st.session_state.auto_trigger = False
    st.session_state.active_query = query_input
    st.session_state.last_result = execute_query(query_input)

# Hiển thị kết quả trả lời
if st.session_state.last_result:
    res = st.session_state.last_result
    
    st.markdown("---")
    st.markdown(f"**Q**")
    st.markdown(f"#### {st.session_state.active_query}")

    # Khung trả lời chính của AI (Card Box viền đẹp)
    with st.container(border=True):
        st.markdown(res.get('reply', ''))

    sources = res.get("sources", [])
    total_found = res.get("total_found", len(sources))

    # Expander nguồn tham chiếu (chuẩn theo ảnh mẫu)
    with st.expander(f"⌄ Đã tìm thấy {total_found} sản phẩm & tài liệu tham chiếu", expanded=True):
        if sources:
            tags_html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">'
            for s in sources:
                label_prefix = "Sản phẩm" if s.get("type") == "product" else "Chính sách"
                price_val = s.get('price', 0)
                price_str = f" (&#36;{price_val:.2f})" if price_val > 0 else ""
                name = s.get("name", "").replace("$", "&#36;")
                tags_html += f'<span class="source-tag"><b>{label_prefix}:</b> {name}{price_str}</span>'
            tags_html += '</div>'
            st.html(tags_html)
            
            # Bảng chi tiết trích xuất
            st.markdown("<br>", unsafe_allow_html=True)
            import pandas as pd
            df_sources = pd.DataFrame(sources)
            if not df_sources.empty:
                col_rename = {
                    "name": "Tên sản phẩm / Tài liệu",
                    "category": "Danh mục",
                    "price": "Giá bán ($)",
                    "rating": "Đánh giá ⭐",
                    "score": "Độ tương đồng"
                }
                display_cols = [c for c in col_rename.keys() if c in df_sources.columns]
                st.dataframe(
                    df_sources[display_cols].rename(columns=col_rename),
                    use_container_width=True,
                    hide_index=True
                )
        else:
            st.info("Không có tài liệu tham chiếu bổ sung.")

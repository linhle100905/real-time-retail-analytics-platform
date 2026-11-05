# 🛒 Retail Intelligence Platform
### Real-Time Big Data Streaming & AI-Powered Personalization System

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-7.4-red.svg)](https://kafka.apache.org/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.5-orange.svg)](https://spark.apache.org/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector%20DB-crimson.svg)](https://qdrant.tech/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)

Nền tảng phân tích dữ liệu bán lẻ thời gian thực kết hợp trí tuệ nhân tạo, tích hợp toàn diện từ tầng xử lý luồng dữ liệu lớn (Big Data Streaming) đến hệ thống khuyến nghị cá nhân hóa (AI Recommender) và trợ lý thông minh hỏi đáp danh mục sản phẩm (RAG Catalog QA).

---

## 🌟 Tính Năng Nổi Bật

1. **Big Data Streaming (Kafka & PySpark Structured Streaming):**
   - Đệm và tiếp nhận luồng sự kiện (Clickstream, Order, Review) với độ trễ thấp (< 50ms).
   - Xử lý cửa sổ trượt (Sliding Windows) và Tumbling Windows tính toán doanh thu thời gian thực.
   - Cảnh báo bất thường và đột biến doanh số.

2. **Hệ Thống Gợi Ý Cá Nhân Hóa (AI Recommender Engine):**
   - **Item-Based Collaborative Filtering** với ma trận tương tác ẩn (Implicit Feedback) kết hợp: Số lượt mua (trọng số 2.0), Đánh giá (0.5), Logarit tổng chi tiêu.
   - **Khai phá tập mục thường xuyên (Co-occurrence Mining & Lift Score)** để tự động đề xuất gói Combo tiết kiệm (Frequently Bought Together).
   - Đạt **Hit Rate @ 5: 78.0%**, **Precision @ 5: 71.0%**, độ phủ danh mục **96.5%**, độ trễ **~11.4 ms**.

3. **Trợ Lý Thông Minh Danh Mục Sản Phẩm (RAG Catalog QA):**
   - Kỹ thuật Retrieval-Augmented Generation kết hợp OpenAI GPT và **Qdrant Vector Database**.
   - Tìm kiếm ngữ nghĩa đa chiều theo khoảng cách Cosine trên vector nhúng 1536 chiều.
   - Trả lời tự nhiên bằng tiếng Việt kèm trích dẫn nguồn sản phẩm và giá bán cụ thể, loại bỏ ảo giác (Hallucination).

4. **Dashboard Quản Trị & Vận Hành Trực Quan (Streamlit UI):**
   - 5 trang nghiệp vụ chuyên sâu: Tổng quan kinh doanh, Giám sát luồng Real-Time, Phân tích sản phẩm đa chiều, Kiểm thử gợi ý AI, Trò chuyện cùng trợ lý RAG.

---

## 🏗️ Kiến Trúc Hệ Thống

```
[Clients / Web Store / Event Simulator]
                   │
                   ▼ (Event Stream)
        [Apache Kafka Broker]
                   │
                   ▼ (Micro-batches / Sliding Windows)
    [Apache Spark Structured Streaming]
         │                       │
         ▼ (Aggregated Metrics)   ▼ (Embeddings Index)
[PostgreSQL Database]       [Qdrant Vector DB]
         │                       │
         └───────────┬───────────┘
                     │
                     ▼
             [FastAPI Backend]
                     │
                     ▼
          [Streamlit Operations UI]
```

---

## 📁 Cấu Trúc Thư Mục

```text
Do_An_Ca_Nhan/
├── api/                   # Backend FastAPI (Endpoints: recommendations, chat, analytics)
├── config/                # Cấu hình Kafka, Postgres, Qdrant, Settings
├── dashboard/             # Giao diện Streamlit (5 trang phân tích & demo)
├── data/                  # Thư mục chứa dữ liệu mẫu và pipeline
├── docs/                  # Tài liệu, sơ đồ kiến trúc (architecture.png, erd.png)
├── ingestion/             # Bộ giả lập và Kafka Producer
├── knowledge_base/        # Tài liệu chính sách đổi trả, khuyến mãi cho RAG
├── ml/                    # Thuật toán Item-Based CF, Co-occurrence Mining, ALS
├── preprocessing/         # Pipeline tiền xử lý và EDA dữ liệu
├── rag/                   # Pipeline RAG: Chunker, Embedder, Retriever, Qdrant Store
├── storage/               # Schema SQL và module kết nối PostgreSQL
├── streaming/             # PySpark Structured Streaming jobs
├── docker-compose.yml     # Khởi tạo Kafka, PostgreSQL, Qdrant qua Docker
├── requirements.txt       # Danh sách thư viện Python phụ thuộc
├── run_all.bat            # Script 1-click khởi chạy toàn bộ hệ thống trên Windows
└── run_system.ps1         # Script PowerShell khởi chạy và kiểm tra service
```

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Hệ Thống

### 1. Yêu cầu hệ thống
- Python 3.10 hoặc 3.11
- Docker Desktop (đang chạy)
- Git

### 2. Cài đặt môi trường
```bash
# 1. Clone repository
git clone <URL_REPOSITORY_CUA_BAN>
cd Do_An_Ca_Nhan

# 2. Tạo virtual environment
python -m venv .venv
.venv\Scripts\activate   # Windows

# 3. Cài đặt các thư viện cần thiết
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường
Tạo file `.env` từ file mẫu `.env.example`:
```bash
copy .env.example .env
```
Điền OpenAI API Key của bạn vào file `.env`:
```env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql+psycopg2://admin:password@127.0.0.1:5433/retail_db
QDRANT_URL=http://localhost:6333
```

### 4. Khởi chạy toàn bộ hệ thống (1-Click)
Chỉ cần nhấp đúp vào file hoặc chạy lệnh:
```bash
run_all.bat
```
Hoặc qua PowerShell:
```powershell
.\run_system.ps1
```

Hệ thống sẽ tự động:
1. Kích hoạt Docker Compose (Kafka, PostgreSQL port 5433, Qdrant port 6333).
2. Khởi chạy FastAPI Backend tại `http://127.0.0.1:8000` (Swagger Docs tại `/docs`).
3. Khởi chạy Streamlit Dashboard tại `http://localhost:8501`.

---

## 👥 Tác Giả & Bản Quyền
- **Sinh viên thực hiện:** LQH
- **Chuyên đề / Đồ án:** Xây dựng Nền tảng Phân tích Dữ liệu Bán lẻ Thời gian thực kết hợp AI
- **Liên hệ:** lqh060406@gmail.com

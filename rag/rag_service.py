import os
import sys
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console UTF-8 encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

BASE_DIR = Path(__file__).resolve().parent.parent
CACHE_FILE = BASE_DIR / "data" / "processed" / "catalog_embeddings.pkl"
ORDERS_FILE = BASE_DIR / "data" / "processed" / "clean_orders.parquet"

_catalog_data = None
_openai_client = None

def get_openai_client():
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return _openai_client

def get_catalog_data():
    global _catalog_data
    if _catalog_data is None:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "rb") as f:
                _catalog_data = pickle.load(f)
        else:
            from rag.catalog_indexer import index_all
            index_all()
            with open(CACHE_FILE, "rb") as f:
                _catalog_data = pickle.load(f)
    return _catalog_data

def search_knowledge_base(query: str, top_k: int = 5):
    """Tìm kiếm kết hợp ngữ nghĩa (Dense OpenAI Embedding) và từ khóa (Lexical Boost)"""
    client = get_openai_client()
    
    # 1. Tạo embedding câu truy vấn
    resp = client.embeddings.create(input=[query], model="text-embedding-3-small")
    q_vec = np.array(resp.data[0].embedding, dtype=np.float32)

    # 2. Thử truy vấn Qdrant nếu online
    try:
        from qdrant_client import QdrantClient
        q_client = QdrantClient(url=QDRANT_URL, timeout=1.0)
        hits = q_client.search(
            collection_name="retail_catalog",
            query_vector=q_vec.tolist(),
            limit=top_k
        )
        if hits:
            results = []
            for hit in hits:
                doc = hit.payload
                doc["score"] = float(hit.score)
                results.append(doc)
            return results
    except Exception:
        pass

    # 3. Sử dụng Local Vector Cache (Đảm bảo 100% không phụ thuộc Docker)
    catalog = get_catalog_data()
    docs = catalog["docs"]
    embeddings = catalog["embeddings"]

    # Tính Cosine Similarity
    norm_q = np.linalg.norm(q_vec)
    norm_emb = np.linalg.norm(embeddings, axis=1)
    sims = np.dot(embeddings, q_vec) / (norm_emb * norm_q + 1e-9)

    # Lexical keyword boost để tăng độ chính xác tuyệt đối cho các từ khóa chuyên biệt
    query_lower = query.lower()
    keywords_bonus = {
        "hữu cơ": ["organic", "hữu cơ", "honey", "tea", "quinoa"],
        "organic": ["organic", "hữu cơ", "honey", "tea", "quinoa"],
        "ăn vặt": ["snack", "nuts", "chocolate", "bars", "ăn vặt", "trẻ em"],
        "trẻ em": ["kids", "children", "trẻ em", "lego", "toy", "action figure", "tablet", "bear", "nuts"],
        "ăn sáng": ["breakfast", "ăn sáng", "coffee", "tea", "energy bars", "quinoa"],
        "bữa tiệc": ["party", "bữa tiệc", "card game", "blender", "speaker", "tea", "coffee"],
        "đồ uống": ["drink", "beverage", "tea", "coffee", "matcha", "blender", "đồ uống"],
        "đổi trả": ["return", "đổi trả", "hoàn trả"],
        "hoàn trả": ["return", "đổi trả", "hoàn trả"],
        "vận chuyển": ["shipping", "vận chuyển", "giao hàng"],
        "khuyến mãi": ["promotion", "khuyến mãi", "giảm giá", "voucher"]
    }

    scores = sims.copy()
    for kw, bonus_words in keywords_bonus.items():
        if kw in query_lower:
            for idx, doc in enumerate(docs):
                doc_text = (doc["name"] + " " + doc.get("tags", "") + " " + doc.get("category_vi", "")).lower()
                for bw in bonus_words:
                    if bw in doc_text:
                        scores[idx] += 0.15

    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []
    for idx in top_indices:
        doc = dict(docs[idx])
        doc["score"] = float(scores[idx])
        results.append(doc)
    return results

def get_sales_stats_context():
    """Lấy số liệu kinh doanh tóm tắt để phục vụ câu hỏi về doanh thu/đơn hàng"""
    try:
        if ORDERS_FILE.exists():
            df = pd.read_parquet(ORDERS_FILE)
            total_rev = df["subtotal_usd"].sum()
            total_orders = df["order_id"].nunique()
            total_cust = df["customer_id"].nunique()
            top_cats = df.groupby("category")["subtotal_usd"].sum().sort_values(ascending=False).head(3).to_dict()
            return f"Số liệu thực tế cửa hàng: Tổng doanh thu: ${total_rev:,.2f}. Tổng đơn hàng: {total_orders:,}. Tổng khách hàng: {total_cust:,}. Top ngành hàng doanh thu cao: {top_cats}."
    except Exception:
        pass
    return ""

def ask_retail_assistant(query: str, top_k: int = 5) -> dict:
    """Xử lý câu hỏi RAG & Catalog QA, trả về câu trả lời định dạng đẹp và danh sách nguồn trích xuất"""
    retrieved_docs = search_knowledge_base(query, top_k=top_k)
    sales_context = get_sales_stats_context() if any(w in query.lower() for w in ["doanh thu", "tổng", "bán chạy", "thống kê", "order", "khách hàng"]) else ""

    context_chunks = []
    for i, doc in enumerate(retrieved_docs, 1):
        context_chunks.append(f"[{i}] {doc['content']}")
    context_str = "\n".join(context_chunks)

    system_prompt = """Bạn là Trợ lý AI Thông minh của Hệ thống Bán lẻ Retail Intelligence (Retail AI Catalog Assistant).
Nhiệm vụ của bạn là trả lời các câu hỏi về:
1. Danh mục sản phẩm (sản phẩm hữu cơ, đồ ăn vặt cho bé, đồ uống, công nghệ, thời trang, đồ gia dụng...)
2. Chính sách công ty (đổi trả, bảo hành, vận chuyển, khuyến mãi)
3. Doanh thu và phân tích bán hàng.

QUY TẮC TRÌNH BÀY (HÃY LÀM ĐÚNG THEO ĐỊNH DẠNG MẪU):
- Nếu hỏi về danh mục / sản phẩm:
  + Mở đầu bằng một câu khẳng định lịch sự, ví dụ: "Các sản phẩm hữu cơ sau đây hiện có sẵn:" hoặc "Dưới đây là các món ăn vặt tốt nhất cho trẻ em hiện có trong cửa hàng:"
  + Liệt kê rõ ràng từng sản phẩm theo định dạng số:
    1. **Tên sản phẩm đầy đủ**
       - **Danh mục**: Tên danh mục tiếng Việt
       - **Giá bán**: $XX.XX
       - **Đánh giá**: ⭐ X.X / 5.0
       - **Đặc điểm nổi bật**: 1 câu giải thích tại sao sản phẩm này phù hợp.
- Nếu hỏi về chính sách: Trình bày các điều khoản, thời hạn (ví dụ 30 ngày đổi trả, miễn phí vận chuyển > $50) bằng các gạch đầu dòng rõ ràng.
- Nếu hỏi về số liệu kinh doanh: Sử dụng dữ liệu tổng quan được cung cấp để trả lời chính xác.
- Luôn trả lời bằng Tiếng Việt chuẩn mực, tôn trọng dữ liệu đã cung cấp."""

    user_prompt = f"""Câu hỏi: "{query}"

Dữ liệu tham khảo từ hệ thống:
{context_str}

{sales_context}

Hãy trả lời theo định dạng chuẩn:"""

    try:
        client = get_openai_client()
        chat_completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        reply = chat_completion.choices[0].message.content
    except Exception as e:
        reply = f"Lỗi khi xử lý qua OpenAI LLM: {str(e)}"

    sources = []
    for doc in retrieved_docs:
        sources.append({
            "name": doc.get("name"),
            "type": doc.get("type", "product"),
            "category": doc.get("category_vi", doc.get("category_en", "")),
            "price": doc.get("price", 0.0),
            "rating": doc.get("rating", 0.0),
            "score": round(doc.get("score", 0.0), 3)
        })

    return {
        "query": query,
        "reply": reply,
        "sources": sources,
        "total_found": len(sources),
        "engine": "OpenAI GPT-4o-mini + Vietnamese-SBERT & Hybrid Dense Search"
    }

class BotAgentCompat:
    def invoke(self, inputs: dict):
        query = inputs.get("input", "")
        res = ask_retail_assistant(query)
        return {"output": res["reply"], "sources": res["sources"]}

bot_agent = BotAgentCompat()

if __name__ == "__main__":
    test_q = "Chúng tôi có những sản phẩm hữu cơ nào?"
    print(f"Test Query: {test_q}")
    result = ask_retail_assistant(test_q)
    print("\n--- AI Reply ---")
    print(result["reply"])
    print("\n--- Sources ---")
    for s in result["sources"]:
        print(s)

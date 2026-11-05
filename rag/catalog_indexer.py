import os
import sys
import json
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
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

BASE_DIR = Path(__file__).resolve().parent.parent
PRODUCT_FILE = BASE_DIR / "data" / "raw" / "ecommerce" / "product_summary.csv"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
CACHE_FILE = BASE_DIR / "data" / "processed" / "catalog_embeddings.pkl"

CATEGORY_VIETNAMESE = {
    "Automotive": "Phụ kiện ô tô & Xe hơi",
    "Beauty & Personal Care": "Sắc đẹp & Chăm sóc cá nhân",
    "Books": "Sách & Tri thức",
    "Clothing & Apparel": "Thời trang & May mặc",
    "Electronics": "Thiết bị điện tử & Công nghệ",
    "Food & Grocery": "Thực phẩm, Đồ ăn vặt & Tạp hóa hữu cơ",
    "Health & Wellness": "Sức khỏe & Thực phẩm bổ sung",
    "Home & Kitchen": "Đồ gia dụng & Nhà bếp",
    "Jewelry & Accessories": "Trang sức & Phụ kiện",
    "Office Supplies": "Văn phòng phẩm & Bàn làm việc",
    "Pet Supplies": "Đồ dùng & Thức ăn thú cưng",
    "Sports & Outdoors": "Thể thao & Dã ngoại",
    "Toys & Games": "Đồ chơi, Trò chơi trẻ em & Bữa tiệc",
    "Travel & Luggage": "Du lịch & Hành lý"
}

PRODUCT_SEMANTIC_TAGS = {
    "Honey Raw Organic": "sản phẩm hữu cơ organic mật ong tự nhiên nguyên chất ăn sáng ngọt dinh dưỡng kháng khuẩn",
    "Organic Green Tea": "sản phẩm hữu cơ organic trà xanh tự nhiên đồ uống giải khát tiệc thanh lọc chống oxy hóa",
    "Dark Chocolate 85%": "đồ ăn vặt snack cho trẻ em sô cô la đen nguyên chất ít ngọt năng lượng món ăn nhẹ",
    "Energy Bars 12-Pack": "món ăn sáng nhanh tiện lợi đồ ăn vặt dinh dưỡng cho trẻ em thanh ngũ cốc dưới 25 đô",
    "Mixed Nuts 500g": "đồ ăn vặt tốt nhất cho trẻ em hạt dinh dưỡng óc chó hạnh nhân hạt điều ăn sáng lành mạnh tiệc",
    "Quinoa 2kg": "sản phẩm hữu cơ organic hạt diêm mạch ngũ cốc ăn sáng lành mạnh giàu đạm dưới 25 đô",
    "Matcha Powder": "bột trà xanh matcha đồ uống cho bữa tiệc giải khát pha chế sinh tố bánh ngọt",
    "Coffee Beans 1kg": "hạt cà phê nguyên chất đồ uống cho buổi sáng tỉnh táo tiếp khách bữa tiệc giải khát",
    "Olive Oil Extra Virgin": "sản phẩm hữu cơ organic dầu ô liu siêu nguyên chất gia vị nấu ăn cao cấp gia đình",
    "Card Game Party": "trò chơi cho bữa tiệc party game vui nhộn cùng bạn bè giải trí nhóm đông người",
    "Board Game Strategy": "trò chơi bàn cờ chiến thuật giải trí gia đình tư duy cho trẻ em và người lớn",
    "LEGO City Set": "bộ xếp hình đồ chơi sáng tạo cho trẻ em rèn luyện kiên nhẫn quà tặng bé",
    "Action Figure Set": "đồ chơi mô hình nhân vật hành động cho trẻ em quà tặng bé trai bé gái",
    "Stuffed Animal Bear": "gấu bông nhồi bông dễ thương cho trẻ nhỏ đồ chơi mềm mại an toàn bé yêu thích",
    "Educational Tablet": "máy tính bảng giáo dục học tập cho trẻ em đồ chơi thông minh mầm non",
    "Air Fryer 5L": "nồi chiên không dầu nhà bếp nấu ăn ít dầu mỡ tốt cho sức khỏe gia đình",
    "Blender Pro": "máy xay sinh tố công suất cao làm đồ uống giải khát và sinh tố cho bữa tiệc"
}

def build_catalog_documents():
    df = pd.read_csv(PRODUCT_FILE)
    documents = []

    for idx, row in df.iterrows():
        p_name = row["product_name"]
        cat_en = row["category"]
        cat_vi = CATEGORY_VIETNAMESE.get(cat_en, cat_en)
        price = float(row["avg_price"])
        rating = float(row["avg_rating"])
        orders = int(row["total_orders"])
        rev = float(row["total_revenue_usd"])
        tags = PRODUCT_SEMANTIC_TAGS.get(p_name, "")

        text_content = (
            f"Sản phẩm: {p_name}. "
            f"Danh mục: {cat_vi} ({cat_en}). "
            f"Giá bán: ${price:.2f}. "
            f"Đánh giá: {rating:.1f}/5.0 sao ({orders} lượt mua). "
            f"Từ khóa & đặc điểm: {tags if tags else p_name.lower()}."
        )

        doc = {
            "id": f"prod_{idx}",
            "type": "product",
            "name": p_name,
            "category_en": cat_en,
            "category_vi": cat_vi,
            "price": price,
            "rating": rating,
            "total_orders": orders,
            "revenue": rev,
            "tags": tags,
            "content": text_content
        }
        documents.append(doc)

    if KNOWLEDGE_BASE_DIR.exists():
        for file in KNOWLEDGE_BASE_DIR.glob("*.md"):
            with open(file, "r", encoding="utf-8") as f:
                p_text = f.read()
            doc_name = file.stem.replace("_", " ").title()
            doc = {
                "id": f"policy_{file.stem}",
                "type": "policy",
                "name": f"Chính sách: {doc_name}",
                "category_en": "Company Policies",
                "category_vi": "Chính sách & Quy định công ty",
                "price": 0.0,
                "rating": 5.0,
                "total_orders": 0,
                "revenue": 0.0,
                "tags": "chính sách công ty quy định hoàn trả đổi trả vận chuyển bảo hành khuyến mãi",
                "content": f"Chính sách {doc_name}:\n{p_text}"
            }
            documents.append(doc)

    return documents

def index_all():
    print("=" * 60)
    print("📦 BẮT ĐẦU EMBEDDING DANH MỤC & CHÍNH SÁCH BẰNG OPENAI")
    print("=" * 60)

    docs = build_catalog_documents()
    print(f"Tổng số mục: {len(docs)} (140 sản phẩm + chính sách)")

    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)

    contents = [d["content"] for d in docs]
    print("⏳ Đang tạo vector embedding qua OpenAI text-embedding-3-small...")
    resp = client.embeddings.create(input=contents, model="text-embedding-3-small")
    embeddings = np.array([item.embedding for item in resp.data], dtype=np.float32)

    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "wb") as f:
        pickle.dump({"docs": docs, "embeddings": embeddings}, f)
    print(f"✅ Đã lưu cache hoàn chỉnh tại: {CACHE_FILE}")

    # Đồng bộ Qdrant nếu khả dụng
    try:
        from qdrant_client import QdrantClient
        from qdrant_client.http.models import Distance, VectorParams, PointStruct
        q_client = QdrantClient(url=QDRANT_URL, timeout=1.5)
        collection_name = "retail_catalog"
        q_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=embeddings.shape[1], distance=Distance.COSINE)
        )
        points = [
            PointStruct(id=i, vector=embeddings[i].tolist(), payload=docs[i])
            for i in range(len(docs))
        ]
        q_client.upsert(collection_name=collection_name, points=points)
        print(f"✅ Đã đồng bộ thành công vào Qdrant: {collection_name}")
    except Exception as e:
        print(f"ℹ️ Qdrant server chưa online. Sử dụng local vector store sẵn sàng 100%.")

    print("🎉 HOÀN THÀNH!")

if __name__ == "__main__":
    index_all()

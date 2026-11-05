import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

# 1. Cấu hình
KNOWLEDGE_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base")
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "retail_policies"

def load_and_embed_data():
    print("1. Đang đọc tài liệu từ thư mục knowledge_base...")
    # Load toàn bộ file .md
    loader = DirectoryLoader(KNOWLEDGE_BASE_DIR, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={'encoding': 'utf-8'})
    documents = loader.load()
    print(f"Đã load {len(documents)} file tài liệu.")

    print("2. Đang cắt nhỏ văn bản (Chunking)...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)
    print(f"Đã cắt thành {len(chunks)} đoạn nhỏ.")

    print("3. Đang khởi tạo Embedding Model (SentenceTransformer)...")
    # Tải mô hình Embedding mã nguồn mở đa ngôn ngữ (Hỗ trợ tiếng Việt tốt)
    embeddings = HuggingFaceEmbeddings(model_name="keepitreal/vietnamese-sbert")

    print("4. Đang lưu vào Qdrant Database...")

    # Đưa dữ liệu vào Qdrant (Tự động xóa cũ và tạo mới)
    QdrantVectorStore.from_documents(
        chunks,
        embeddings,
        url=QDRANT_URL,
        prefer_grpc=False,
        collection_name=COLLECTION_NAME,
        force_recreate=True
    )
    print("✅ HOÀN TẤT! Toàn bộ kiến thức đã được nạp vào Vector Database.")

if __name__ == "__main__":
    load_and_embed_data()

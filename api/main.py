from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import analytics, chat, recommendations

app = FastAPI(
    title="Retail Intelligence API",
    description="Backend API cho hệ thống phân tích bán lẻ",
    version="1.0.0"
)

# Cấu hình CORS (Cho phép Streamlit hoặc ứng dụng khác gọi API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong thực tế nên giới hạn domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký các router
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
# app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])

@app.get("/")
def read_root():
    return {"message": "Chào mừng đến với Retail Intelligence API"}

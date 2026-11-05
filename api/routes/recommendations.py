from fastapi import APIRouter, HTTPException, Query
import sys
import os

router = APIRouter()

# Lazy loading engine instance
_recommender_engine = None

def get_engine():
    global _recommender_engine
    if _recommender_engine is None:
        from ml.recommend import get_recommender_engine
        _recommender_engine = get_recommender_engine()
    return _recommender_engine

@router.get("/customer/{customer_id}")
def get_customer_recommendations(customer_id: str, limit: int = Query(6, ge=1, le=20)):
    """API gợi ý sản phẩm cá nhân hóa theo từng khách hàng cụ thể"""
    try:
        engine = get_engine()
        result = engine.recommend_for_customer(customer_id, top_k=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/frequently-bought-together/{product_name}")
def get_bundle_recommendations(product_name: str, limit: int = Query(4, ge=1, le=10)):
    """API gợi ý combo sản phẩm thường được mua cùng nhau (Cross-sell Bundle)"""
    try:
        engine = get_engine()
        result = engine.get_frequently_bought_together(product_name, top_k=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics")
def get_model_metrics():
    """API trả về các chỉ số đánh giá độ chính xác của mô hình ML"""
    try:
        engine = get_engine()
        return {
            "metrics": engine.evaluation_metrics,
            "total_users": len(engine.customer_profiles),
            "total_items": len(engine.product_catalog),
            "algorithm": "Item-Based Collaborative Filtering (Cosine) + Co-Occurrence Lift"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sample-customers")
def get_sample_customers():
    """API trả về danh sách khách hàng đại diện cho các nhóm chân dung để demo"""
    return [
        {"id": "C00005", "label": "C00005 - Khách hàng VIP Platinum (Chi tiêu $2,593, Thời trang & May mặc)"},
        {"id": "C00002", "label": "C00002 - Khách hàng Đồ chơi & Trò chơi (Chi tiêu $1,245, Hạng Free)"},
        {"id": "C00003", "label": "C00003 - Khách hàng Gold (Chi tiêu $195, Đồ gia dụng & Nhà bếp)"},
        {"id": "C00001", "label": "C00001 - Khách hàng Mới (Chi tiêu $286, Thực phẩm & Tạp hóa)"},
        {"id": "C00004", "label": "C00004 - Khách hàng Yêu công nghệ (Chi tiêu $99, Thiết bị điện tử)"}
    ]

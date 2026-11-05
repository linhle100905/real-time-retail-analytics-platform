from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import sys
import os

# Thêm đường dẫn gốc để import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config.postgres_config import get_db

router = APIRouter()

@router.get("/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    """API lấy tổng quan các chỉ số (Tổng doanh thu, Tổng đơn hàng,...)"""
    try:
        query = text("""
            SELECT 
                COUNT(*) as total_orders,
                SUM(total_amount_usd) as total_revenue,
                AVG(total_amount_usd) as avg_order_value,
                COUNT(DISTINCT customer_id) as total_customers
            FROM orders
        """)
        result = db.execute(query).fetchone()
        
        return {
            "total_orders": result[0],
            "total_revenue": round(result[1], 2) if result[1] else 0,
            "avg_order_value": round(result[2], 2) if result[2] else 0,
            "total_customers": result[3]
        }
    except Exception as e:
        # Dự phòng tự động bằng Parquet nếu Docker/Postgres chưa khởi động
        try:
            import pandas as pd
            from pathlib import Path
            p_file = Path(__file__).resolve().parent.parent.parent / "data" / "processed" / "clean_orders.parquet"
            if not p_file.exists():
                p_file = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "ecommerce" / "orders.csv"
            df = pd.read_parquet(p_file) if p_file.suffix == ".parquet" else pd.read_csv(p_file)
            return {
                "total_orders": int(len(df)),
                "total_revenue": round(float(df["total_amount_usd"].sum()), 2),
                "avg_order_value": round(float(df["total_amount_usd"].mean()), 2),
                "total_customers": int(df["customer_id"].nunique())
            }
        except Exception:
            raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-products")
def get_top_products(limit: int = 10, sort_by: str = "total_revenue", db: Session = Depends(get_db)):
    """API lấy danh sách top sản phẩm bán chạy nhất"""
    
    # Ràng buộc chống SQL Injection
    valid_sort_columns = ["total_quantity", "total_revenue", "total_orders"]
    if sort_by not in valid_sort_columns:
        sort_by = "total_revenue"
        
    try:
        # F-string ở đây an toàn vì sort_by đã được check qua danh sách valid_sort_columns
        query = text(f"""
            SELECT 
                product_name,
                category,
                SUM(quantity) as total_quantity,
                SUM(subtotal_usd) as total_revenue,
                COUNT(DISTINCT order_id) as total_orders,
                AVG(customer_rating) as avg_rating
            FROM orders
            GROUP BY product_name, category
            ORDER BY {sort_by} DESC
            LIMIT :limit
        """)
        result = db.execute(query, {"limit": limit}).fetchall()
        
        top_products = []
        for row in result:
            top_products.append({
                "product_name": row[0],
                "category": row[1],
                "total_quantity": row[2],
                "total_revenue": round(row[3], 2),
                "total_orders": row[4],
                "avg_rating": round(row[5], 2) if row[5] else 0
            })
        return top_products
    except Exception as e:
        # Dự phòng tự động bằng Parquet nếu Docker/Postgres chưa khởi động
        try:
            import pandas as pd
            from pathlib import Path
            p_file = Path(__file__).resolve().parent.parent.parent / "data" / "processed" / "clean_orders.parquet"
            if not p_file.exists():
                p_file = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "ecommerce" / "orders.csv"
            df = pd.read_parquet(p_file) if p_file.suffix == ".parquet" else pd.read_csv(p_file)
            
            agg = df.groupby(["product_name", "category"]).agg(
                total_quantity=("quantity", "sum"),
                total_revenue=("subtotal_usd", "sum"),
                total_orders=("order_id", "nunique"),
                avg_rating=("customer_rating", "mean")
            ).reset_index()
            
            agg = agg.sort_values(by=sort_by, ascending=False).head(limit)
            agg["total_revenue"] = agg["total_revenue"].round(2)
            agg["avg_rating"] = agg["avg_rating"].fillna(0).round(2)
            return agg.to_dict(orient="records")
        except Exception:
            raise HTTPException(status_code=500, detail=str(e))

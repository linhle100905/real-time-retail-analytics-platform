import json
import time
import pandas as pd
from kafka import KafkaProducer
from pathlib import Path
import sys

# =========================================================
# CONFIG
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
ORDERS_FILE = BASE_DIR / "data" / "processed" / "clean_orders.parquet"
KAFKA_TOPIC = "ecommerce_orders"
KAFKA_SERVER = "127.0.0.1:9092"

print("=" * 70)
print("🚀 BẮT ĐẦU KAFKA PRODUCER (Mô phỏng sự kiện Mua hàng Real-time)")
print("=" * 70)

# =========================================================
# INIT KAFKA PRODUCER
# =========================================================
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        api_version=(2, 0, 2),
        request_timeout_ms=10000
    )
    print(f"✅ Kết nối thành công tới Kafka tại {KAFKA_SERVER}")
except Exception as e:
    print(f"❌ Lỗi kết nối Kafka: {e}")
    print("Vui lòng đảm bảo bạn đã chạy 'docker-compose up -d'")
    sys.exit(1)

# =========================================================
# READ DATA & STREAM
# =========================================================
if not ORDERS_FILE.exists():
    print(f"❌ Không tìm thấy file: {ORDERS_FILE}")
    sys.exit(1)

df = pd.read_parquet(ORDERS_FILE)
print(f"📦 Đã load {len(df):,} đơn hàng. Chuẩn bị bắn dữ liệu lên Kafka...")

# Giả lập bắn từng đơn hàng lên Kafka
for index, row in df.iterrows():
    # Convert datetime to string for JSON serialization
    event = row.to_dict()
    event["order_date"] = str(event["order_date"])
    event["delivery_date"] = str(event.get("delivery_date", ""))
    
    # Bắn lên Kafka
    producer.send(KAFKA_TOPIC, event)
    
    print(f"[{index}] 🛒 Order {event['order_id']} | "
          f"Sản phẩm: {event['product_name'][:20]}... | "
          f"Giá: ${event['subtotal_usd']}")
    
    # Nghỉ 20 giây để giả lập real-time (20 giây / 1 đơn hàng demo)
    time.sleep(20)

print("🎉 Đã hoàn thành gửi toàn bộ dữ liệu!")
producer.close()

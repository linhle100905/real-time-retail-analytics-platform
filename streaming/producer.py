import json
import time
import socket
import pandas as pd
from kafka import KafkaProducer
from pathlib import Path
import sys

# Đảm bảo in tiếng Việt và Emoji trên Windows PowerShell không bị lỗi charmap
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# =========================================================
# CONFIG
# =========================================================
BASE_DIR = Path(__file__).resolve().parent.parent
ORDERS_FILE = BASE_DIR / "data" / "processed" / "clean_orders.parquet"
if not ORDERS_FILE.exists():
    ORDERS_FILE = BASE_DIR / "data" / "raw" / "ecommerce" / "orders.csv"

KAFKA_TOPIC = "ecommerce_orders"
KAFKA_HOST = "127.0.0.1"
KAFKA_PORT = 9092
KAFKA_SERVER = f"{KAFKA_HOST}:{KAFKA_PORT}"

print("=" * 70)
print("🚀 BẮT ĐẦU KAFKA PRODUCER (Mô phỏng sự kiện Mua hàng Real-time)")
print("=" * 70)

# =========================================================
# KIỂM TRA SẴN SÀNG CỦA KAFKA BROKER (PRE-FLIGHT CHECK)
# =========================================================
def is_kafka_running(host=KAFKA_HOST, port=KAFKA_PORT, timeout=2.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False

if not is_kafka_running():
    print(f"\n❌ LỖI: Không thể kết nối tới Kafka Broker tại {KAFKA_SERVER}!")
    print("----------------------------------------------------------------------")
    print("👉 NGUYÊN NHÂN:")
    print("   1. Docker Desktop chưa được bật trên máy tính của bạn.")
    print("   2. Hoặc các container hạ tầng (Kafka, Zookeeper) chưa được khởi động.")
    print("\n👉 CÁCH KHẮC PHỤC:")
    print("   Bước 1: Mở ứng dụng Docker Desktop trên Windows.")
    print("   Bước 2: Chờ Docker chuyển sang trạng thái 'Engine running' (xanh lá).")
    print("   Bước 3: Chạy lệnh sau để khởi động Kafka & Zookeeper:")
    print("           docker compose up -d")
    print("   Bước 4: Chạy lại lệnh producer này:")
    print("           python streaming/producer.py")
    print("----------------------------------------------------------------------\n")
    sys.exit(1)

# =========================================================
# INIT KAFKA PRODUCER
# =========================================================
try:
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_SERVER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        api_version=(2, 0, 2),
        request_timeout_ms=5000,
        max_block_ms=5000
    )
    print(f"✅ Kết nối thành công tới Kafka tại {KAFKA_SERVER}")
except Exception as e:
    print(f"❌ Lỗi khởi tạo Kafka Producer: {e}")
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

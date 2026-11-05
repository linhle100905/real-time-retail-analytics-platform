from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, sum as _sum
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType

# =========================================================
# CONFIG
# =========================================================
KAFKA_TOPIC = "ecommerce_orders"
KAFKA_SERVER = "localhost:9092"

print("=" * 70)
print("🚀 BẮT ĐẦU PYSPARK STRUCTURED STREAMING")
print("=" * 70)

# Khởi tạo Spark Session với Kafka package
# Lưu ý: Yêu cầu kết nối internet lần đầu để tải thư viện org.apache.spark:spark-sql-kafka-0-10
spark = SparkSession.builder \
    .appName("RetailStreamProcessing") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .config("spark.sql.shuffle.partitions", "2") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# =========================================================
# SCHEMA
# =========================================================
# Định nghĩa schema khớp với dữ liệu JSON gửi từ producer
schema = StructType([
    StructField("order_id", StringType(), True),
    StructField("order_date", StringType(), True),
    StructField("product_name", StringType(), True),
    StructField("category", StringType(), True),
    StructField("subtotal_usd", DoubleType(), True)
])

# =========================================================
# ĐỌC KAFKA
# =========================================================
try:
    df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_SERVER) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "latest") \
        .load()
except Exception as e:
    print(f"❌ Lỗi kết nối Spark-Kafka: {e}")
    exit(1)

# Chuyển đổi dữ liệu nhị phân (value) từ Kafka thành JSON
parsed_df = df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

# Chuyển string order_date thành kiểu timestamp để tính toán cửa sổ thời gian
parsed_df = parsed_df.withColumn("order_date", col("order_date").cast("timestamp"))

# =========================================================
# XỬ LÝ (PROCESSING)
# =========================================================
# 1. Tính tổng doanh thu theo danh mục sản phẩm (Category) theo thời gian thực
category_revenue = parsed_df \
    .groupBy("category") \
    .agg(_sum("subtotal_usd").alias("total_revenue"))

# =========================================================
# OUTPUT SINK
# =========================================================
# Trong đồ án thực tế, bạn sẽ dùng .format("jdbc") để ghi xuống PostgreSQL
# Ở bản demo này, chúng ta xuất thẳng ra console để dễ nhìn
query = category_revenue \
    .writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .start()

print("✅ Đang lắng nghe dữ liệu từ Kafka...")
query.awaitTermination()

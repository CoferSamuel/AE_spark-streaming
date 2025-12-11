from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    from_json,
    current_timestamp,
    window,
    count,
    max as max_,
    min as min_,
)
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from datetime import datetime
import pyspark

# ============================
# 1. CONFIGURACIÓN BÁSICA
# ============================

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "tweets_topic"

# Usar la versión de PySpark como versión del conector Kafka
spark_version = pyspark.__version__.split("+")[0]  # ej: "3.5.1"

spark = (
    SparkSession.builder
    .appName("TrendingTopicsStreaming")
    .config(
        "spark.jars.packages",
        f"org.apache.spark:spark-sql-kafka-0-10_2.12:{spark_version}"
    )
    .getOrCreate()
)

# Menos ruido en consola
spark.sparkContext.setLogLevel("ERROR")

# ============================
# 2. LEER STREAM DESDE KAFKA
# ============================

raw_df = (
    spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS)
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "latest")
        .load()
)

value_df = raw_df.selectExpr("CAST(value AS STRING) as json_str")

# ============================
# 3. PARSEAR EL JSON
# ============================

schema = StructType([
    StructField("usuario", StringType(), True),
    StructField("texto", StringType(), True),
    StructField("hashtag_principal", StringType(), True),
    StructField("timestamp", DoubleType(), True),
])

parsed_df = (
    value_df
    .select(from_json(col("json_str"), schema).alias("data"))
    .select("data.*")
)

df_with_ts = (
    parsed_df
    .where(col("hashtag_principal").isNotNull())
    .withColumn("ts", current_timestamp())
)

# ============================
# 4. AGREGACIÓN EN VENTANAS DE 60 s (minuto real)
# ============================

windowed_counts = (
    df_with_ts
    .withWatermark("ts", "2 minutes")
    .groupBy(
        window(col("ts"), "60 seconds"),   # ventana FIJA de 1 minuto
        col("hashtag_principal")
    )
    .agg(count("*").alias("num_ocurrencias"))
)

MAX_HASHTAGS = 10  # mostramos hasta 10 si hay suficientes

# ============================
# 5. FOREACHBATCH: LÓGICA POR BATCH
# ============================

def process_batch(batch_df, batch_id: int):
    """
    - Se queda con la ventana de minuto más reciente (REAL).
    - Ordena por num_ocurrencias (ranking del minuto).
    - Imprime la tabla directamente, sin tocar la columna 'window'.
    """
    if batch_df.isEmpty():
        return

    # Ventana de minuto más reciente (por window.end real)
    max_end_row = batch_df.agg(max_("window.end").alias("max_end")).collect()[0]
    max_end = max_end_row["max_end"]

    if max_end is None:
        return

    latest_window_df = batch_df.filter(col("window.end") == max_end)

    # Límites reales de la ventana de minuto
    bounds = latest_window_df.agg(
        min_("window.start").alias("start"),
        max_("window.end").alias("end")
    ).collect()[0]

    window_start = bounds["start"]
    window_end = bounds["end"]

    if window_start is None or window_end is None:
        return

    # Ranking por minuto (ventana real)
    top_in_minute = (
        latest_window_df
        .orderBy(col("num_ocurrencias").desc())
        .limit(MAX_HASHTAGS)
    )

    # Tiempo del snapshot (para saber cuándo se ha impreso)
    snapshot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ----------------- SALIDA POR CONSOLA -----------------
    print("\n========================================")
    print(f"Batch {batch_id} - Snapshot en {snapshot_time}")
    print(
        "Ventana del minuto "
        f"[{window_start.strftime('%H:%M:%S')} , {window_end.strftime('%H:%M:%S')}]"
    )
    print("Top hashtags en este minuto:")
    top_in_minute.show(truncate=False)
    print("========================================\n")

# ============================
# 6. ARRANCAR EL STREAM
# ============================

query = (
    windowed_counts
    .writeStream
    .outputMode("update")          # actualizamos solo cambios
    .foreachBatch(process_batch)   # usamos nuestra función para mostrar resultados
    .trigger(processingTime="10 seconds")
    .start()
)

query.awaitTermination()

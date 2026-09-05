from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
import os

app = FastAPI(title="Crypto Pipeline API")

# Izinkan React (beda port) untuk akses API ini
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # untuk development; nanti bisa dibatasi ke domain tertentu
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port="5432",
        dbname="pipeline_db",
        user="dataeng",
        password="password123",
        cursor_factory=psycopg2.extras.RealDictCursor
    )

@app.get("/")
def root():
    return {"status": "ok", "service": "crypto-pipeline-api"}

@app.get("/api/coins")
def get_coins():

    """Snapshot harga terbaru tiap koin"""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT name, symbol, price_usd AS price, price_change_24h_pct AS "change24h",
                   total_volume AS volume, market_cap AS "marketCap", loaded_at
            FROM crypto_prices
            WHERE loaded_at = (SELECT MAX(loaded_at) FROM crypto_prices)
            ORDER BY market_cap_rank ASC
        """)
        rows = cur.fetchall()
    conn.close()
    return rows

@app.get("/api/price-series")
def get_price_series():
    """Histori harga tiap koin, format wide untuk chart (t, BTC, ETH, ...)"""
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT symbol, price_usd, loaded_at
            FROM crypto_prices
            ORDER BY loaded_at ASC
        """)
        rows = cur.fetchall()
    conn.close()

    # Pivot: kelompokkan per timestamp, gabung semua symbol jadi 1 baris
    series = {}
    for r in rows:
        ts = r["loaded_at"].strftime("%Y-%m-%d %H:%M")
        if ts not in series:

            series[ts] = {"t": ts}
        series[ts][r["symbol"].upper()] = float(r["price_usd"])
    return list(series.values())

@app.get("/api/insights")
def get_insights():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT coin_name, insight_type, insight_text, is_anomaly, generated_at
            FROM ai_dialog_feed
            ORDER BY generated_at DESC
            LIMIT 30
        """)
        rows = cur.fetchall()
    conn.close()
    return rows

@app.get("/api/quality")
def get_quality():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT run_timestamp, total_records_in, total_records_out,
                   missing_values_count, duplicate_count, anomaly_count, status
            FROM data_quality_log
            ORDER BY run_timestamp DESC
            LIMIT 1
        """)
        latest = cur.fetchone()
    conn.close()
    return latest or {}


@app.get("/api/pipeline-status")
def get_pipeline_status():
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT MAX(loaded_at) AS last_extract FROM crypto_prices")
        extract = cur.fetchone()

        cur.execute("SELECT MAX(event_timestamp) AS last_stream FROM crypto_prices_streaming")
        stream = cur.fetchone()

        cur.execute("SELECT status, run_timestamp FROM data_quality_log ORDER BY run_timestamp DESC LIMIT 1")
        quality = cur.fetchone()
    conn.close()
    return {
        "last_extract": extract["last_extract"],
        "last_stream": stream["last_stream"],
        "quality_status": quality["status"] if quality else None,
    }
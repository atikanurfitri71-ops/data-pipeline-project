import pandas as pd
import psycopg2
import os
from sklearn.ensemble import IsolationForest
from datetime import datetime

import pandas as pd
import psycopg2
import os
from sklearn.ensemble import IsolationForest

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port="5432",
        dbname="pipeline_db",
        user="dataeng",
        password="password123"
    )

def create_dialog_feed_table(conn):
    create_query = """
    CREATE TABLE IF NOT EXISTS ai_dialog_feed (
        id SERIAL PRIMARY KEY,
        coin_name VARCHAR(100),
        insight_type VARCHAR(50),
        insight_text TEXT,
        is_anomaly BOOLEAN DEFAULT FALSE,
        generated_at TIMESTAMP DEFAULT NOW()
    );
    """
    with conn.cursor() as cur:
        cur.execute(create_query)
    conn.commit()

def fetch_latest_snapshot(conn):
    query = """
        SELECT id, name, symbol, price_usd, market_cap, market_cap_rank,

               total_volume, price_change_24h_pct, loaded_at
        FROM crypto_prices
        WHERE loaded_at = (SELECT MAX(loaded_at) FROM crypto_prices)
    """
    return pd.read_sql(query, conn)

def fetch_two_latest_snapshots(conn):
    """Ambil 2 timestamp run terakhir untuk perbandingan trend"""
    ts_query = "SELECT DISTINCT loaded_at FROM crypto_prices ORDER BY loaded_at DESC LIMIT 2"
    timestamps = pd.read_sql(ts_query, conn)["loaded_at"].tolist()
    
    if len(timestamps) < 2:
        return None, None
    
    latest_df = pd.read_sql(
        "SELECT * FROM crypto_prices WHERE loaded_at = %(ts)s",
        conn, params={"ts": timestamps[0]}
    )
    previous_df = pd.read_sql(
        "SELECT * FROM crypto_prices WHERE loaded_at = %(ts)s",
        conn, params={"ts": timestamps[1]}
    )
    return latest_df, previous_df

# ── Insight 1: Anomaly Detection (harga) ──
def detect_price_anomalies(df):
    features = df[["price_change_24h_pct"]].fillna(0)
    model = IsolationForest(contamination=0.15, random_state=42)
    df["anomaly_score"] = model.fit_predict(features)
    df["is_anomaly"] = df["anomaly_score"] == -1
    return df


def generate_anomaly_insights(df):
    insights = []
    for _, row in df.iterrows():
        if row["is_anomaly"]:
            direction = "naik" if row["price_change_24h_pct"] > 0 else "turun"
            text = (f"⚠️ {row['name']} menunjukkan pergerakan tidak biasa: harga {direction} "
                    f"signifikan ke ${row['price_usd']:,.2f} ({row['price_change_24h_pct']:+.2f}% dalam 24 jam).")
            insights.append((row["name"], "price_anomaly", text, True))
    return insights

# ── Insight 2: Trend Dibanding Run Sebelumnya ──
def generate_trend_insights(latest_df, previous_df):
    insights = []
    if latest_df is None:
        return insights
    
    merged = latest_df.merge(previous_df, on="id", suffixes=("_latest", "_prev"))
    for _, row in merged.iterrows():
        price_diff_pct = ((row["price_usd_latest"] - row["price_usd_prev"]) / row["price_usd_prev"]) * 100
        if abs(price_diff_pct) >= 1:  # cuma laporkan perubahan >= 1% biar tidak terlalu ramai
            direction = "naik" if price_diff_pct > 0 else "turun"
            text = (f"{row['name_latest']} {direction} {abs(price_diff_pct):.2f}% dibanding pengecekan "
                    f"sebelumnya, kini di harga ${row['price_usd_latest']:,.2f}.")
            insights.append((row["name_latest"], "trend_vs_previous", text, False))
    return insights

# ── Insight 3: Perubahan Ranking Market Cap ──
def generate_ranking_insights(latest_df, previous_df):
    insights = []
    if latest_df is None:
        return insights
    

    merged = latest_df.merge(previous_df, on="id", suffixes=("_latest", "_prev"))
    for _, row in merged.iterrows():
        rank_diff = row["market_cap_rank_prev"] - row["market_cap_rank_latest"]
        if rank_diff != 0:
            direction = "naik" if rank_diff > 0 else "turun"
            text = (f"{row['name_latest']} {direction} peringkat market cap dari #{row['market_cap_rank_prev']} "
                    f"ke #{row['market_cap_rank_latest']}.")
            insights.append((row["name_latest"], "rank_change", text, False))
    return insights

# ── Insight 4: Korelasi Volume vs Pergerakan Harga ──
def generate_volume_price_insights(df):
    insights = []
    for _, row in df.iterrows():
        if row["market_cap"] == 0:
            continue
        volume_ratio = row["total_volume"] / row["market_cap"]
        change = row["price_change_24h_pct"]
        
        if abs(change) >= 2 and volume_ratio >= 0.15:
            direction = "kenaikan" if change > 0 else "penurunan"
            text = (f"{row['name']} mengalami {direction} {abs(change):.2f}% didukung volume transaksi "
                    f"tinggi (rasio volume/market cap: {volume_ratio:.2f}) — sinyal pergerakan kuat.")
            insights.append((row["name"], "volume_price_signal", text, False))
        elif abs(change) >= 2 and volume_ratio < 0.02:
            direction = "kenaikan" if change > 0 else "penurunan"
            text = (f"{row['name']} mengalami {direction} {abs(change):.2f}% namun volume transaksi rendah "
                    f"(rasio: {volume_ratio:.3f}) — sinyal pergerakan lemah, perlu diwaspadai.")
            insights.append((row["name"], "volume_price_signal", text, False))
    return insights

# ── Insight 5: Ringkasan Sentimen Pasar ──

def generate_market_summary(df):
    total = len(df)
    positive_count = int((df["price_change_24h_pct"] > 0).sum())
    negative_count = total - positive_count
    avg_change = df["price_change_24h_pct"].mean()
    sentiment = "bullish (cenderung naik)" if positive_count > total / 2 else "bearish (cenderung turun)"
    
    text = (f"Ringkasan pasar: {positive_count} dari {total} koin bergerak positif dalam 24 jam terakhir, "
            f"{negative_count} koin negatif. Rata-rata perubahan {avg_change:+.2f}%. "
            f"Sentimen pasar saat ini {sentiment}.")
    return [("MARKET_OVERVIEW", "market_summary", text, False)]

def save_insights(conn, insights):
    with conn.cursor() as cur:
        for coin_name, insight_type, text, is_anomaly in insights:
            cur.execute("""
                INSERT INTO ai_dialog_feed (coin_name, insight_type, insight_text, is_anomaly)
                VALUES (%s, %s, %s, %s)
            """, (coin_name, insight_type, text, is_anomaly))
    conn.commit()

def run_ai_feed_pipeline():
    conn = get_connection()
    create_dialog_feed_table(conn)
    
    latest_df = fetch_latest_snapshot(conn)
    if latest_df.empty:
        print("Tidak ada data ditemukan. Jalankan pipeline ETL dulu.")
        return
    
    latest_two, previous_two = fetch_two_latest_snapshots(conn)
    

    all_insights = []
    
    # 1. Anomaly detection
    latest_df = detect_price_anomalies(latest_df)
    all_insights += generate_anomaly_insights(latest_df)
    
    # 2 & 3. Trend & ranking (butuh minimal 2 run data)
    if latest_two is not None:
        all_insights += generate_trend_insights(latest_two, previous_two)
        all_insights += generate_ranking_insights(latest_two, previous_two)
    else:
        print("Catatan: belum cukup data historis untuk trend/ranking (butuh minimal 2x run pipeline).")
    
    # 4. Volume vs price correlation
    all_insights += generate_volume_price_insights(latest_df)
    
    # 5. Market summary
    all_insights += generate_market_summary(latest_df)
    
    save_insights(conn, all_insights)
    
    print(f"\nBerhasil generate {len(all_insights)} insight untuk Dialog feed:\n")
    for coin_name, insight_type, text, is_anomaly in all_insights:
        print(f"[{insight_type}] {text}")
    
    conn.close()

if __name__ == "__main__":
    run_ai_feed_pipeline()
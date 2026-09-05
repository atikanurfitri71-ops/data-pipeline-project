import streamlit as st
import pandas as pd
import psycopg2
import os
import plotly.express as px
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Crypto Pipeline Dashboard", layout="wide")

# Auto-refresh tiap 30 detik
st_autorefresh(interval=30 * 1000, key="datarefresh")

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port="5432",
        dbname="pipeline_db",
        user="dataeng",
        password="password123"
    )

@st.cache_data(ttl=25)
def load_price_history():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT name, price_usd, market_cap_rank, price_change_24h_pct, loaded_at
        FROM crypto_prices
        ORDER BY loaded_at ASC
    """, conn)
    conn.close()
    return df


@st.cache_data(ttl=25)
def load_quality_log():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT run_timestamp, total_records_in, total_records_out, 
               missing_values_count, duplicate_count, anomaly_count, status
        FROM data_quality_log
        ORDER BY run_timestamp DESC
        LIMIT 20
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=25)
def load_ai_insights():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT coin_name, insight_type, insight_text, is_anomaly, generated_at
        FROM ai_dialog_feed
        ORDER BY generated_at DESC
        LIMIT 30
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=25)
def load_streaming_data():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT coin, price_usd, event_timestamp
        FROM crypto_prices_streaming
        ORDER BY event_timestamp ASC

    """, conn)
    conn.close()
    return df

# ── HEADER ──
st.title("📊 Crypto Data Pipeline Dashboard")
st.caption("Dashboard live yang terhubung langsung ke pipeline ETL, Airflow, Kafka, dan AI Feed. Auto-refresh tiap 30 detik.")

price_df = load_price_history()
quality_df = load_quality_log()
insight_df = load_ai_insights()
stream_df = load_streaming_data()

# ── MARKET SUMMARY (dari AI insight) ──
summary_row = insight_df[insight_df["insight_type"] == "market_summary"]
if not summary_row.empty:
    st.info(summary_row.iloc[0]["insight_text"])

# ── ROW 1: Price Trend Chart ──
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("📈 Trend Harga per Koin (Batch/Airflow)")
    if not price_df.empty:
        coin_options = price_df["name"].unique().tolist()
        selected_coins = st.multiselect(
            "Pilih koin untuk ditampilkan:", 
            coin_options, 
            default=coin_options
        )
        filtered = price_df[price_df["name"].isin(selected_coins)]
        fig = px.line(filtered, x="loaded_at", y="price_usd", color="name",
                      title="Pergerakan Harga dari Waktu ke Waktu")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Belum ada data. Jalankan pipeline ETL terlebih dahulu.")
        
with col2:
    st.subheader("✅ Status Data Quality")
    if not quality_df.empty:
        latest_status = quality_df.iloc[0]
        status_color = "🟢" if latest_status["status"] == "PASS" else "🔴"
        st.metric("Status Terakhir", f"{status_color} {latest_status['status']}")
        st.metric("Records In → Out", 
                   f"{latest_status['total_records_in']} → {latest_status['total_records_out']}")
        st.metric("Anomaly Terdeteksi", int(latest_status["anomaly_count"]))
    else:
        st.warning("Belum ada log data quality.")

# ── ROW 2: Real-time Streaming Chart ──
st.subheader("⚡ Real-time Streaming (Kafka)")
if not stream_df.empty:
    fig2 = px.line(stream_df, x="event_timestamp", y="price_usd", color="coin",
                   title="Data Real-time dari Kafka Consumer")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("Belum ada data streaming. Jalankan producer & consumer Kafka.")

# ── ROW 3: AI Dialog Feed Insights ──
st.subheader("🤖 AI Insight Feed (untuk Fitur Dialog)")
if not insight_df.empty:
    for _, row in insight_df[insight_df["insight_type"] != "market_summary"].head(15).iterrows():
        icon = "⚠️" if row["is_anomaly"] else "💬"
        st.write(f"{icon} **[{row['insight_type']}]** {row['insight_text']}")

else:
    st.warning("Belum ada insight AI. Jalankan ai_feed/detect_and_generate.py.")

# ── ROW 4: Data Quality History Table ──
st.subheader("📋 Riwayat Data Quality Log")
st.dataframe(quality_df, use_container_width=True)
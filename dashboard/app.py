import streamlit as st
import pandas as pd
import psycopg2
import os
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Crypto Data Pipeline Dashboard", layout="wide", page_icon="📊")
st_autorefresh(interval=30 * 1000, key="datarefresh")

# ─────────────────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────────────────
BG = "oklch(0.16 0.018 250)"
SURFACE = "oklch(0.2 0.02 252)"
SURFACE_2 = "oklch(0.24 0.022 254)"
BORDER = "oklch(0.3 0.022 254)"
FG = "oklch(0.96 0.005 250)"
MUTED = "oklch(0.68 0.02 254)"
PRIMARY = "oklch(0.8 0.16 165)"
DOWN = "oklch(0.68 0.19 20)"
WARN = "oklch(0.83 0.16 85)"
ACCENT = "oklch(0.72 0.15 240)"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{ font-family: 'Space Grotesk', sans-serif; }}
.stApp {{ background-color: {BG}; color: {FG}; }}
.num {{ font-family: 'JetBrains Mono', monospace; }}

.hero-wrap {{
    background-image: radial-gradient(120% 100% at 50% 0%,
        color-mix(in oklab, {PRIMARY} 16%, transparent), transparent 70%);
    padding: 24px 0 8px 0; margin: -16px -16px 8px -16px; padding-left: 16px; padding-right: 16px;
    border-bottom: 1px solid {BORDER};
}}
.hero-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    border: 1px solid {BORDER}; background: {SURFACE};
    padding: 4px 12px; border-radius: 999px;
    font-size: 12px; color: {MUTED}; margin-right: 8px;
}}
.live-dot {{
    width: 8px; height: 8px; border-radius: 50%;
    background: {PRIMARY}; display: inline-block;
    animation: pulse 1.8s infinite;
}}
@keyframes pulse {{
    0% {{ box-shadow: 0 0 0 0 color-mix(in oklab, {PRIMARY} 60%, transparent); }}
    100% {{ box-shadow: 0 0 0 8px transparent; }}
}}

.panel {{
    background-color: {SURFACE}; border: 1px solid {BORDER};
    border-radius: 16px; padding: 20px 24px; margin-bottom: 16px;
}}
.stat-card {{
    background: linear-gradient(180deg, {SURFACE_2}, {SURFACE});
    border: 1px solid {BORDER}; border-radius: 14px; padding: 18px 20px;
}}
.stat-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.05em; color: {MUTED}; }}
.stat-value {{ font-size: 26px; font-weight: 700; margin-top: 6px; font-family: 'JetBrains Mono', monospace; }}
.stat-hint {{ font-size: 12px; color: {MUTED}; margin-top: 4px; }}

.section-title {{ display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }}
.section-title .icon {{
    width: 34px; height: 34px; border-radius: 10px;
    background: {SURFACE_2}; color: {PRIMARY};
    display: flex; align-items: center; justify-content: center; font-size: 15px;
}}
.section-title h3 {{ margin: 0; font-size: 17px; font-weight: 600; }}
.section-title p {{ margin: 0; font-size: 12px; color: {MUTED}; }}

.badge-up {{
    color: {PRIMARY}; background: color-mix(in oklab, {PRIMARY} 14%, transparent);
    padding: 3px 9px; border-radius: 999px; font-size: 12px; font-weight: 500;
    font-family: 'JetBrains Mono', monospace; white-space: nowrap;
}}
.badge-down {{
    color: {DOWN}; background: color-mix(in oklab, {DOWN} 14%, transparent);
    padding: 3px 9px; border-radius: 999px; font-size: 12px; font-weight: 500;
    font-family: 'JetBrains Mono', monospace; white-space: nowrap;
}}

.pipeline-card {{
    background: linear-gradient(160deg, {SURFACE}, {SURFACE_2});
    border: 1px solid {BORDER}; border-radius: 14px; padding: 16px 18px; height: 100%;
    border-left: 3px solid {PRIMARY};
}}
.pipeline-card .title {{ font-size: 13px; font-weight: 600; margin-bottom: 2px; }}
.pipeline-card .detail {{ font-size: 12px; color: {MUTED}; }}
.pipeline-card .meta {{ font-size: 12px; color: {PRIMARY}; margin-top: 8px; font-family: 'JetBrains Mono', monospace; }}

.insight-card {{
    background: linear-gradient(135deg, {SURFACE_2}, {SURFACE});
    border-radius: 12px; padding: 14px 16px; margin-bottom: 10px;
    border: 1px solid {BORDER};
}}
.insight-card .title {{ font-size: 13px; font-weight: 600; color: {PRIMARY}; margin-bottom: 4px; }}
.insight-card p {{ font-size: 13px; color: {MUTED}; margin: 0; line-height: 1.5; }}

.anomaly-card {{
    background: linear-gradient(135deg, {SURFACE_2}, {SURFACE});
    border-left: 3px solid {DOWN}; border-radius: 10px;
    padding: 12px 16px; margin-bottom: 10px;
}}
.anomaly-card .title {{ font-size: 13px; font-weight: 600; }}
.anomaly-card .kind {{ font-size: 12px; color: {DOWN}; font-weight: 500; margin: 2px 0; }}
.anomaly-card p {{ font-size: 12px; color: {MUTED}; margin: 0; }}

.quality-status {{
    display: flex; align-items: center; gap: 14px;
    background: linear-gradient(135deg, {SURFACE_2}, {SURFACE});
    border-radius: 12px; padding: 16px; margin-bottom: 16px;
}}
.quality-status .circle {{
    width: 48px; height: 48px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center; font-size: 20px; flex-shrink: 0;
}}
.quality-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 0; border-bottom: 1px solid {BORDER};
}}
.quality-row:last-child {{ border-bottom: none; }}

table.price-table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
table.price-table th {{
    text-align: left; font-size: 11px; text-transform: uppercase; color: {MUTED};
    padding: 8px 10px; border-bottom: 1px solid {BORDER}; font-weight: 500;
}}
table.price-table td {{
    padding: 10px; border-bottom: 1px solid color-mix(in oklab, {BORDER} 60%, transparent);
}}
table.price-table tr:hover td {{ background: color-mix(in oklab, {PRIMARY} 4%, transparent); }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port="5432", dbname="pipeline_db",
        user="dataeng", password="password123"
    )

@st.cache_data(ttl=25)
def load_price_history():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT name, symbol, price_usd, market_cap, market_cap_rank,
               total_volume, price_change_24h_pct, loaded_at
        FROM crypto_prices ORDER BY loaded_at ASC
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=25)
def load_quality_log():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT run_timestamp, total_records_in, total_records_out,
               missing_values_count, duplicate_count, anomaly_count, status
        FROM data_quality_log ORDER BY run_timestamp DESC LIMIT 20
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=25)
def load_ai_insights():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT coin_name, insight_type, insight_text, is_anomaly, generated_at
        FROM ai_dialog_feed ORDER BY generated_at DESC LIMIT 30
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=25)
def load_streaming_data():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT coin, price_usd, event_timestamp
        FROM crypto_prices_streaming ORDER BY event_timestamp ASC
    """, conn)
    conn.close()
    return df

price_df = load_price_history()
quality_df = load_quality_log()
insight_df = load_ai_insights()
stream_df = load_streaming_data()

def badge(value):
    cls = "badge-up" if value >= 0 else "badge-down"
    arrow = "↑" if value >= 0 else "↓"
    return f'<span class="{cls}">{arrow} {value:+.2f}%</span>'

def section_title(icon, title, subtitle=""):
    st.markdown(
        f'<div class="section-title"><div class="icon">{icon}</div>'
        f'<div><h3>{title}</h3><p>{subtitle}</p></div></div>',
        unsafe_allow_html=True
    )

# ─────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────
latest_snapshot = price_df[price_df["loaded_at"] == price_df["loaded_at"].max()] if not price_df.empty else pd.DataFrame()
positives = int((latest_snapshot["price_change_24h_pct"] > 0).sum()) if not latest_snapshot.empty else 0
total_coins = len(latest_snapshot)
avg_change = latest_snapshot["price_change_24h_pct"].mean() if not latest_snapshot.empty else 0
total_volume = latest_snapshot["total_volume"].sum() if not latest_snapshot.empty else 0
last_update = price_df["loaded_at"].max().strftime("%H:%M:%S") if not price_df.empty else "—"

st.markdown('<div class="hero-wrap">', unsafe_allow_html=True)
st.markdown(
    '<span class="hero-badge"><span class="live-dot"></span> Live · auto-refresh 30 detik</span>'
    '<span class="hero-badge">Portofolio Data Engineering</span>',
    unsafe_allow_html=True
)
st.markdown(f"""
<h1 style="font-size:40px; font-weight:700; margin-top:16px; margin-bottom:8px;">
Crypto Data Pipeline <span style="color:{PRIMARY};">Dashboard</span>
</h1>
<p style="color:{MUTED}; font-size:15px; max-width:700px;">
Pemantauan harga kripto secara real-time dari pipeline ETL end-to-end: ingest API,
streaming Kafka, transformasi Python, dan orkestrasi Airflow — dilengkapi insight AI,
kontrol kualitas data, serta deteksi anomali nilai ekstrem.
</p>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
stats = [
    (c1, "Koin dipantau", f"{total_coins}", "refresh tiap 30 menit"),
    (c2, "Rata-rata 24 jam", f"{avg_change:+.2f}%", f"{positives} naik · {total_coins - positives} turun"),
    (c3, "Volume 24 jam", f"${total_volume/1e9:.2f}B" if total_volume else "—", "agregat pasar"),
    (c4, "Update terakhir", last_update, "waktu snapshot Airflow"),
]
for col, label, value, hint in stats:
    with col:
        st.markdown(
            f'<div class="stat-card"><div class="stat-label">{label}</div>'
            f'<div class="stat-value">{value}</div><div class="stat-hint">{hint}</div></div>',
            unsafe_allow_html=True
        )
st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# PIPELINE HEALTH
# ─────────────────────────────────────────────────────────
last_quality = quality_df.iloc[0] if not quality_df.empty else None
last_stream = stream_df["event_timestamp"].max() if not stream_df.empty else None

pipeline_cards = [
    ("Extract", "Ingest dari CoinGecko API", f"Snapshot terakhir: {last_update}"),
    ("Kafka Streaming", "Producer & consumer real-time",
     f"Event terakhir: {last_stream.strftime('%H:%M:%S') if last_stream is not None else '—'}"),
    ("Transform & QC", "Cleaning, dedup, anomaly check",
     f"Status: {last_quality['status'] if last_quality is not None else '—'}"),
    ("Airflow", "Orkestrasi batch pipeline", "Jadwal: tiap 30 menit"),
]
cols = st.columns(4)
for col, (title, detail, meta) in zip(cols, pipeline_cards):
    with col:
        st.markdown(
            f'<div class="pipeline-card"><div class="title">{title}</div>'
            f'<div class="detail">{detail}</div><div class="meta">{meta}</div></div>',
            unsafe_allow_html=True
        )
st.markdown("<br>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# CHART + AI INSIGHT
# ─────────────────────────────────────────────────────────
col_chart, col_insight = st.columns([2, 1])

with col_chart:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    section_title("📈", "Trend harga per koin", "Batch Airflow")
    if not price_df.empty:
        coin_options = price_df["name"].unique().tolist()
        selected = st.multiselect("Pilih koin:", coin_options, default=coin_options, label_visibility="collapsed")
        mode = st.radio("Mode:", ["Skala Log (Harga Absolut)", "Perubahan Relatif (%)"],
                         horizontal=True, label_visibility="collapsed")

        filtered = price_df[price_df["name"].isin(selected)].copy().sort_values("loaded_at")
        palette = [PRIMARY, ACCENT, WARN, DOWN, "oklch(0.75 0.14 190)"]
        fig = go.Figure()

        if mode == "Perubahan Relatif (%)":
            filtered["pct_change"] = filtered.groupby("name")["price_usd"].transform(
                lambda x: (x / x.iloc[0] - 1) * 100
            )
            for i, name in enumerate(selected):
                d = filtered[filtered["name"] == name]
                fig.add_trace(go.Scatter(
                    x=d["loaded_at"], y=d["pct_change"], name=name, mode="lines",
                    line=dict(width=2, color=palette[i % len(palette)])
                ))
            fig.update_yaxes(title="Perubahan (%)")
        else:
            for i, name in enumerate(selected):
                d = filtered[filtered["name"] == name]
                fig.add_trace(go.Scatter(
                    x=d["loaded_at"], y=d["price_usd"], name=name, mode="lines",
                    line=dict(width=2, color=palette[i % len(palette)])
                ))
            fig.update_yaxes(type="log")

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=340, margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", y=1.15),
            font=dict(family="JetBrains Mono", size=11)
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Belum ada data. Jalankan pipeline ETL terlebih dahulu.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_insight:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    section_title("🤖", "Insight AI", "Ringkasan otomatis")
    if not insight_df.empty:
        cards = "".join(
            f'<div class="insight-card"><div class="title">{row["insight_type"].replace("_", " ").title()}</div>'
            f'<p>{row["insight_text"]}</p></div>'
            for _, row in insight_df.head(6).iterrows()
        )
        st.markdown(cards, unsafe_allow_html=True)
    else:
        st.info("Belum ada insight AI.")
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# PRICE TABLE
# ─────────────────────────────────────────────────────────
st.markdown('<div class="panel">', unsafe_allow_html=True)
section_title("🗄", "Tabel data harga", "Snapshot terakhir dari crypto_prices")

if not latest_snapshot.empty:
    anomaly_coins = insight_df[insight_df["is_anomaly"] == True]["coin_name"].tolist() if not insight_df.empty else []

    def price_row(r):
        flagged = r["name"] in anomaly_coins
        status = f'<span style="color:{WARN};">⚠ Anomali</span>' if flagged else f'<span style="color:{MUTED};">✓ Normal</span>'
        return (
            f'<tr><td>{r["name"]} <span class="num" style="color:{MUTED};">{r["symbol"].upper()}</span></td>'
            f'<td class="num">${r["price_usd"]:,.2f}</td>'
            f'<td>{badge(r["price_change_24h_pct"])}</td>'
            f'<td class="num" style="color:{MUTED};">${r["total_volume"]/1e6:,.1f}M</td>'
            f'<td class="num" style="color:{MUTED};">${r["market_cap"]/1e9:,.2f}B</td>'
            f'<td>{status}</td></tr>'
        )

    rows_html = "".join(price_row(r) for _, r in latest_snapshot.iterrows())
    table_html = (
        '<table class="price-table"><thead><tr>'
        '<th>Koin</th><th>Harga</th><th>Perubahan 24 jam</th>'
        '<th>Volume 24 jam</th><th>Kapitalisasi Pasar</th><th>Status</th>'
        f'</tr></thead><tbody>{rows_html}</tbody></table>'
    )
    st.markdown(table_html, unsafe_allow_html=True)
else:
    st.info("Belum ada data.")
st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# QUALITY CONTROL + ANOMALY DETECTION
# ─────────────────────────────────────────────────────────
col_q, col_a = st.columns(2)

with col_q:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    section_title("✓", "Data quality control", "Hasil check run terakhir")
    if last_quality is not None:
        is_pass = last_quality["status"] == "PASS"
        color = PRIMARY if is_pass else DOWN
        st.markdown(
            f'<div class="quality-status"><div class="circle" '
            f'style="background:color-mix(in oklab, {color} 15%, transparent); color:{color};">'
            f'{"✓" if is_pass else "✗"}</div><div>'
            f'<div class="num" style="font-size:22px; font-weight:700; color:{color};">{last_quality["status"]}</div>'
            f'<div style="font-size:12px; color:{MUTED};">Records: {last_quality["total_records_in"]} → {last_quality["total_records_out"]}</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )
        checks = [
            ("Missing values", f'{last_quality["missing_values_count"]} nilai kosong ditemukan'),
            ("Duplikat", f'{last_quality["duplicate_count"]} baris duplikat'),
            ("Anomaly (harga ≤ 0)", f'{last_quality["anomaly_count"]} baris terdeteksi'),
        ]
        rows = "".join(
            f'<div class="quality-row"><div><div style="font-size:13px; font-weight:500;">{n}</div>'
            f'<div style="font-size:12px; color:{MUTED};">{d}</div></div></div>'
            for n, d in checks
        )
        st.markdown(rows, unsafe_allow_html=True)
    else:
        st.info("Belum ada log data quality.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_a:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    section_title("⚠", "Deteksi anomali", "Berdasarkan Isolation Forest")
    anomaly_insights = insight_df[insight_df["is_anomaly"] == True] if not insight_df.empty else pd.DataFrame()
    if not anomaly_insights.empty:
        cards = "".join(
            f'<div class="anomaly-card"><div class="title">{a["coin_name"]}</div>'
            f'<div class="kind">{a["insight_type"].replace("_", " ").title()}</div>'
            f'<p>{a["insight_text"]}</p></div>'
            for _, a in anomaly_insights.head(6).iterrows()
        )
        st.markdown(cards, unsafe_allow_html=True)
    else:
        st.markdown(f'<p style="color:{MUTED}; font-size:13px;">Tidak ada anomali terdeteksi saat ini.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────
st.markdown(
    f'<hr style="border-color:{BORDER}; margin-top:32px;">'
    f'<div style="padding:16px 0; color:{MUTED}; font-size:12px;">'
    f'<strong style="color:{FG};">Atika Nurfitri · Data Engineering Portfolio</strong><br>'
    'Data pada dashboard ini berasal dari pipeline ETL nyata (CoinGecko API → PostgreSQL).</div>',
    unsafe_allow_html=True
)
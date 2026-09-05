import json
import pandas as pd
import glob
import os
import psycopg2
from datetime import datetime

def get_latest_raw_file():
    """Ambil file JSON terbaru dari folder extract/output"""
    files = glob.glob("extract/output/raw_data_*.json")
    if not files:
        raise FileNotFoundError("Tidak ada file raw data ditemukan")
    latest_file = max(files, key=os.path.getctime)
    return latest_file
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port="5432",
        dbname="pipeline_db",
        user="dataeng",
        password="password123"
    )

def create_quality_log_table(conn):
    create_query = """
    CREATE TABLE IF NOT EXISTS data_quality_log (
        id SERIAL PRIMARY KEY,
        run_timestamp TIMESTAMP DEFAULT NOW(),
        pipeline_name VARCHAR(100),
        total_records_in INTEGER,
        total_records_out INTEGER,
        missing_values_count INTEGER,
        duplicate_count INTEGER,
        anomaly_count INTEGER,
        status VARCHAR(20)
    );
    """
    with conn.cursor() as cur:
        cur.execute(create_query)
    conn.commit()

def log_quality_metrics(metrics):
    conn = get_connection()
    create_quality_log_table(conn)
    
    insert_query = """

        INSERT INTO data_quality_log 
        (pipeline_name, total_records_in, total_records_out, 
         missing_values_count, duplicate_count, anomaly_count, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    with conn.cursor() as cur:
        cur.execute(insert_query, (
            metrics["pipeline_name"],
            metrics["total_records_in"],
            metrics["total_records_out"],
            metrics["missing_values_count"],
            metrics["duplicate_count"],
            metrics["anomaly_count"],
            metrics["status"]
        ))
    conn.commit()
    conn.close()
    print("Quality metrics tersimpan ke data_quality_log")

def transform_crypto_data():
    # Load raw data
    filepath = get_latest_raw_file()
    with open(filepath, "r") as f:
        raw_data = json.load(f)
    
    # Convert ke DataFrame
    df = pd.DataFrame(raw_data)
    total_records_in = len(df)
    print(f"Data awal: {len(df)} baris, {len(df.columns)} kolom")
    
    # Pilih kolom yang relevan saja
    df_clean = df[[
        "id", "symbol", "name", "current_price", 
        "market_cap", "market_cap_rank", 
        "total_volume", "price_change_percentage_24h",
        "last_updated"
    ]].copy()
    
    # Data Quality Check 1: Cek missing values
    missing_count = int(df_clean.isnull().sum().sum())
    print(f"Jumlah missing values: {missing_count}")
    df_clean = df_clean.dropna(subset=["current_price", "market_cap"])
    
    # Data Quality Check 2: Cek duplikasi
    duplicate_count = int(df_clean.duplicated(subset=["id"]).sum())
    print(f"Jumlah duplikasi: {duplicate_count}")
    df_clean = df_clean.drop_duplicates(subset=["id"])
    
    # Data Quality Check 3: Cek anomaly (harga negatif atau nol)
    anomaly = df_clean[df_clean["current_price"] <= 0]
    anomaly_count = len(anomaly)

    if anomaly_count > 0:
        print(f"Ditemukan {anomaly_count} anomaly (harga <= 0), akan dihapus")
        df_clean = df_clean[df_clean["current_price"] > 0]
    
    # Rename kolom biar lebih rapi
    df_clean = df_clean.rename(columns={
        "current_price": "price_usd",
        "price_change_percentage_24h": "price_change_24h_pct"
    })
    
    total_records_out = len(df_clean)
    print(f"Data setelah cleaning: {total_records_out} baris")
    
    # Tentukan status: FAIL kalau data yang lolos < 80% dari data awal
    status = "PASS" if (total_records_out / total_records_in) >= 0.8 else "FAIL"
    
    # Log quality metrics ke database
    log_quality_metrics({
        "pipeline_name": "crypto_etl_pipeline",
        "total_records_in": total_records_in,
        "total_records_out": total_records_out,
        "missing_values_count": missing_count,
        "duplicate_count": duplicate_count,
        "anomaly_count": anomaly_count,
        "status": status
    })
    
    # Simpan hasil transform
    os.makedirs("transform/output", exist_ok=True)
    output_path = "transform/output/cleaned_data.csv"
    df_clean.to_csv(output_path, index=False)
    print(f"Data bersih disimpan di: {output_path}")

    
    return df_clean

if __name__ == "__main__":
    transform_crypto_data()
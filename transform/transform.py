import json
import pandas as pd
import glob
import os

def get_latest_raw_file():
    """Ambil file JSON terbaru dari folder extract/output"""
    files = glob.glob("extract/output/raw_data_*.json")
    if not files:
        raise FileNotFoundError("Tidak ada file raw data ditemukan")
    latest_file = max(files, key=os.path.getctime)
    return latest_file

def transform_crypto_data():
    # Load raw data
    filepath = get_latest_raw_file()
    with open(filepath, "r") as f:
        raw_data = json.load(f)
    
    # Convert ke DataFrame
    df = pd.DataFrame(raw_data)
    
    print(f"Data awal: {len(df)} baris, {len(df.columns)} kolom")
    
    # Pilih kolom yang relevan saja
    df_clean = df[[
        "id", "symbol", "name", "current_price", 
        "market_cap", "market_cap_rank", 
        "total_volume", "price_change_percentage_24h",
        "last_updated"
    ]].copy()
    

    # Data Quality Check 1: Cek missing values
    missing_count = df_clean.isnull().sum().sum()
    print(f"Jumlah missing values: {missing_count}")
    
    # Handle missing values (kalau ada)
    df_clean = df_clean.dropna(subset=["current_price", "market_cap"])
    
    # Data Quality Check 2: Cek duplikasi
    duplicate_count = df_clean.duplicated(subset=["id"]).sum()
    print(f"Jumlah duplikasi: {duplicate_count}")
    df_clean = df_clean.drop_duplicates(subset=["id"])
    
    # Data Quality Check 3: Cek anomaly (harga negatif atau nol, tidak masuk akal untuk crypto)
    anomaly = df_clean[df_clean["current_price"] <= 0]
    if len(anomaly) > 0:
        print(f"Ditemukan {len(anomaly)} anomaly (harga <= 0), akan dihapus")
        df_clean = df_clean[df_clean["current_price"] > 0]
    
    # Rename kolom biar lebih rapi
    df_clean = df_clean.rename(columns={
        "current_price": "price_usd",
        "price_change_percentage_24h": "price_change_24h_pct"
    })
    
    print(f"Data setelah cleaning: {len(df_clean)} baris")
    
    # Simpan hasil transform
    os.makedirs("transform/output", exist_ok=True)
    output_path = "transform/output/cleaned_data.csv"
    df_clean.to_csv(output_path, index=False)
    print(f"Data bersih disimpan di: {output_path}")
    

    return df_clean

if __name__ == "__main__":
    transform_crypto_data()
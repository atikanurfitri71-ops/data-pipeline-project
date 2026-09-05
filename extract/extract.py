import requests
import json
from datetime import datetime
import os

def extract_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
    "vs_currency": "usd",
    "ids": "bitcoin,ethereum,binancecoin,solana,ripple",
    "order": "market_cap_desc"
}
    response = requests.get(url, params=params)
    data = response.json()
    
    # Buat folder output kalau belum ada
    os.makedirs("extract/output", exist_ok=True)
    
    # Simpan raw data dengan timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"extract/output/raw_data_{timestamp}.json"
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Berhasil extract {len(data)} records")
    print(f"Disimpan di: {filepath}")
    return data

if __name__ == "__main__":
    extract_crypto_data()
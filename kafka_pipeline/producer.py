from kafka import KafkaProducer
import requests
import json
import time
from datetime import datetime
import os

def create_producer():
    return KafkaProducer(
        bootstrap_servers=[os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")],
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

def fetch_crypto_price():
    """Ambil 3 koin dengan market cap tertinggi saat itu (dinamis)"""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
    "vs_currency": "usd",
    "ids": "dogecoin,cardano,tron",
    "order": "market_cap_desc"
    }
    response = requests.get(url, params=params)
    return response.json()

def run_producer():
    producer = create_producer()
    topic = "crypto_prices_stream"
    
    print("Producer mulai jalan... (Ctrl+C untuk berhenti)")
    
    try:

        while True:
            data = fetch_crypto_price()
            
            # Cek dulu apakah response error (misal rate limit)
            if isinstance(data, dict) and "status" in data:
                error_msg = data["status"].get("error_message", "Unknown error")
                print(f"⚠️ API error, dilewati: {error_msg}")
            else:
                for coin_data in data:
                    message = {
                        "coin": coin_data.get("id"),
                        "price_usd": coin_data.get("current_price"),
                        "change_24h": coin_data.get("price_change_percentage_24h"),
                        "timestamp": datetime.now().isoformat()
                    }
                    producer.send(topic, value=message)
                    print(f"Terkirim: {message}")
                
                producer.flush()
            
            time.sleep(900)  # 15 menit = 900 detik
            
    except KeyboardInterrupt:
        print("\nProducer dihentikan.")
        producer.close()

if __name__ == "__main__":
    run_producer()
    run_producer()
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
    """Ambil harga Bitcoin & Ethereum saja untuk simulasi streaming"""
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "bitcoin,ethereum",
        "vs_currencies": "usd",
        "include_24hr_change": "true"
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

            
            for coin, price_info in data.items():
                message = {
                    "coin": coin,
                    "price_usd": price_info.get("usd"),
                    "change_24h": price_info.get("usd_24h_change"),
                    "timestamp": datetime.now().isoformat()
                }
                producer.send(topic, value=message)
                print(f"Terkirim: {message}")
            
            producer.flush()
            time.sleep(10)  # ambil data tiap 10 detik
            
    except KeyboardInterrupt:
        print("\nProducer dihentikan.")
        producer.close()

if __name__ == "__main__":
    run_producer()
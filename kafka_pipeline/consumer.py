from kafka import KafkaConsumer
import json
import psycopg2
import os

def create_consumer():
    return KafkaConsumer(
        'crypto_prices_stream',
        bootstrap_servers=[os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")],
        auto_offset_reset='earliest',
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port="5432",
        dbname="pipeline_db",
        user="dataeng",
        password="password123"
    )

def create_table(conn):
    create_query = """
    CREATE TABLE IF NOT EXISTS crypto_prices_streaming (
        id SERIAL PRIMARY KEY,
        coin VARCHAR(50),
        price_usd NUMERIC,
        change_24h NUMERIC,
        event_timestamp TIMESTAMP,
        received_at TIMESTAMP DEFAULT NOW()
    );
    """
    with conn.cursor() as cur:
        cur.execute(create_query)
    conn.commit()

def run_consumer():
    conn = get_connection()
    create_table(conn)
    consumer = create_consumer()
    
    print("Consumer mulai mendengarkan... (Ctrl+C untuk berhenti)")
    
    try:
        for message in consumer:
            data = message.value
            
            # Simple validation sebelum insert (data quality check)
            if data.get("price_usd") is None or data["price_usd"] <= 0:
                print(f"Data tidak valid, dilewati: {data}")
                continue
            
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO crypto_prices_streaming 
                    (coin, price_usd, change_24h, event_timestamp)
                    VALUES (%s, %s, %s, %s)
                """, (
                    data["coin"], 
                    data["price_usd"], 
                    data["change_24h"], 
                    data["timestamp"]
                ))
            conn.commit()
            print(f"Tersimpan: {data}")
            
    except KeyboardInterrupt:
        print("\nConsumer dihentikan.")
        consumer.close()
        conn.close()

if __name__ == "__main__":
    run_consumer()
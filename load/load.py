import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        dbname="pipeline_db",
        user="dataeng",
        password="password123"
    )

def create_table(conn):
    """Buat tabel kalau belum ada"""
    create_query = """
    CREATE TABLE IF NOT EXISTS crypto_prices (
        id VARCHAR(100),
        symbol VARCHAR(20),
        name VARCHAR(100),
        price_usd NUMERIC,
        market_cap NUMERIC,
        market_cap_rank INTEGER,
        total_volume NUMERIC,
        price_change_24h_pct NUMERIC,
        last_updated TIMESTAMP,
        loaded_at TIMESTAMP DEFAULT NOW()
    );
    """
    with conn.cursor() as cur:
        cur.execute(create_query)
    conn.commit()

    print("Tabel siap (dibuat atau sudah ada sebelumnya)")

def load_data():
    # Load data yang sudah di-transform
    df = pd.read_csv("transform/output/cleaned_data.csv")
    
    conn = get_connection()
    create_table(conn)
    
    # Convert dataframe ke list of tuples untuk insert
    columns = [
        "id", "symbol", "name", "price_usd", "market_cap",
        "market_cap_rank", "total_volume", 
        "price_change_24h_pct", "last_updated"
    ]
    values = [tuple(row) for row in df[columns].values]
    
    insert_query = f"""
        INSERT INTO crypto_prices ({', '.join(columns)})
        VALUES %s
    """
    
    with conn.cursor() as cur:
        execute_values(cur, insert_query, values)
    conn.commit()
    
    print(f"Berhasil load {len(values)} baris ke PostgreSQL")
    
    conn.close()

if __name__ == "__main__":
    load_data()
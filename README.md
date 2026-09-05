# Crypto Data Pipeline (ETL + Orchestration)

Pipeline data engineering end-to-end yang mengambil data harga cryptocurrency secara berkala, membersihkan datanya, dan menyimpannya ke database — dijalankan otomatis menggunakan Apache Airflow.

## 🎯 Tujuan Project

Project ini dibuat untuk mempraktikkan skill-skill inti Data Engineering:
- Membangun pipeline ETL (Extract, Transform, Load) end-to-end
- Menerapkan data quality checks (validasi, deduplikasi, anomaly detection)
- Orkestrasi & penjadwalan pipeline menggunakan Apache Airflow
- Containerization menggunakan Docker & Docker Compose

## 🏗️ Arsitektur
CoinGecko API → Extract (Python) → Transform (Pandas) → Load (PostgreSQL)
↑
Diorkestrasi oleh Airflow (scheduled @hourly)


**Tech Stack:**
- **Python** — bahasa utama untuk extract, transform, load
- **Pandas** — data cleaning & transformation
- **PostgreSQL** — database penyimpanan
- **Apache Airflow** — orkestrasi & penjadwalan pipeline
- **Docker & Docker Compose** — containerization environment
- **GitHub Codespaces** — development environment (cloud-based)

## 📁 Struktur Folder
data-pipeline-project/
├── extract/
│ └── extract.py # Ambil data dari CoinGecko API
├── transform/
│ └── transform.py # Cleaning, dedup, anomaly detection
├── load/
│ └── load.py # Load data ke PostgreSQL
├── dags/
│ └── crypto_pipeline_dag.py # DAG Airflow untuk orkestrasi
├── docker-compose.yml # Konfigurasi semua service (Postgres, Airflow)
├── Dockerfile.airflow # Custom image Airflow dengan dependencies
├── requirements.txt # Python dependencies
└── README.md


## 🔄 Alur Pipeline

1. **Extract**: Mengambil data 20 cryptocurrency teratas (harga, market cap, volume) dari [CoinGecko API](https://www.coingecko.com/en/api)
2. **Transform**: 
   - Memilih kolom relevan
   - Mengecek & menangani missing values
   - Menghapus duplikasi data
   - Mendeteksi anomaly (harga ≤ 0)
3. **Load**: Menyimpan data bersih ke tabel `crypto_prices` di PostgreSQL

Pipeline dijalankan otomatis **setiap 1 jam** menggunakan Airflow DAG.

## 🚀 Cara Menjalankan

### Prasyarat
- Docker & Docker Compose
- (Atau bisa langsung pakai GitHub Codespaces — tidak perlu install apapun)

### Langkah-langkah

1. Clone repository:
```bash
   git clone https://github.com/atikanurfitri71-ops/data-pipeline-project.git
   cd data-pipeline-project
```

2. Jalankan semua service:
```bash
   docker-compose up --build
```

3. Akses Airflow UI di `http://localhost:8080` (atau URL Codespaces forwarded port)
   - Username: `admin`
   - Password: `admin`

4. Aktifkan DAG `crypto_etl_pipeline` dan trigger manual atau tunggu jadwal otomatis

### Menjalankan Manual (Tanpa Airflow)

```bash
python extract/extract.py
python transform/transform.py
python load/load.py
```

## 🐛 Tantangan & Solusi Selama Development

Beberapa masalah nyata yang saya temui dan pecahkan selama membangun pipeline ini:

1. **Container networking**: Script awalnya connect ke `localhost` untuk database, gagal saat dijalankan di dalam container Airflow. **Solusi**: gunakan environment variable `DB_HOST` yang bisa di-override (`postgres` untuk Docker network, `localhost` untuk run manual).

2. **Airflow auth di mode `standalone`**: Password admin auto-generate random, bentrok dengan user manual yang dibuat di init. **Solusi**: pisahkan service jadi `airflow-webserver` dan `airflow-scheduler` dengan command eksplisit.

3. **Redirect ke localhost di Codespaces**: Airflow redirect ke `localhost:8080` setelah login, padahal diakses lewat proxy Codespaces. **Solusi**: tambahkan `AIRFLOW__WEBSERVER__ENABLE_PROXY_FIX: true`.

## 📈 Rencana Pengembangan Selanjutnya

- [ ] Real-time data ingestion menggunakan Kafka
- [ ] Data quality monitoring dengan logging ke tabel terpisah
- [ ] Migrasi evaluasi ke dedicated data warehouse (BigQuery)
- [ ] Integrasi pipeline sebagai feed untuk model AI sederhana

## 👤 Author

Atika Nur Fitri

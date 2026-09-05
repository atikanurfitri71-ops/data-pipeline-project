export type Coin = {
  symbol: string;
  name: string;
  price: number;
  change24h: number;
  volume: number;
  marketCap: number;
};

export const COINS: Coin[] = [
  { symbol: "BTC", name: "Bitcoin", price: 80125, change24h: 1.84, volume: 24_500_000_000, marketCap: 1_586_000_000_000 },
  { symbol: "ETH", name: "Ethereum", price: 3412.5, change24h: 2.31, volume: 12_100_000_000, marketCap: 410_000_000_000 },
  { symbol: "SOL", name: "Solana", price: 178.42, change24h: 4.12, volume: 3_800_000_000, marketCap: 84_000_000_000 },
  { symbol: "BNB", name: "BNB", price: 612.9, change24h: -0.74, volume: 1_400_000_000, marketCap: 89_000_000_000 },
  { symbol: "XRP", name: "XRP", price: 2.14, change24h: 0.62, volume: 2_200_000_000, marketCap: 122_000_000_000 },
  { symbol: "ADA", name: "Cardano", price: 0.842, change24h: -1.35, volume: 640_000_000, marketCap: 29_000_000_000 },
  { symbol: "DOGE", name: "Dogecoin", price: 0.187, change24h: 6.48, volume: 1_100_000_000, marketCap: 27_000_000_000 },
  { symbol: "AVAX", name: "Avalanche", price: 34.18, change24h: 3.05, volume: 480_000_000, marketCap: 13_800_000_000 },
  { symbol: "LINK", name: "Chainlink", price: 18.62, change24h: -2.18, volume: 520_000_000, marketCap: 11_600_000_000 },
  { symbol: "DOT", name: "Polkadot", price: 6.94, change24h: 0.41, volume: 210_000_000, marketCap: 9_900_000_000 },
];

const SEED_POINTS = 24;

/** Deterministic pseudo-random so SSR and client render the same first paint. */
function seeded(i: number, salt: number) {
  const x = Math.sin(i * 12.9898 + salt * 78.233) * 43758.5453;
  return x - Math.floor(x);
}

export type SeriesPoint = { t: string } & Record<string, number | string>;

export function buildSeries(coins: Coin[]): SeriesPoint[] {
  return Array.from({ length: SEED_POINTS }, (_, i) => {
    const hour = (i + 1) % 24;
    const point: SeriesPoint = { t: `${String(hour).padStart(2, "0")}:00` };
    coins.forEach((c, ci) => {
      const drift = (seeded(i, ci) - 0.45) * 0.02;
      const trend = ((i - SEED_POINTS / 2) / SEED_POINTS) * (c.change24h / 100);
      point[c.symbol] = Number((c.price * (1 + drift + trend)).toFixed(c.price > 100 ? 0 : 4));
    });
    return point;
  });
}

export const QUALITY_CHECKS = [
  { name: "Schema validation", detail: "10 kolom sesuai kontrak data", status: "pass" as const },
  { name: "Null / missing value", detail: "0 nilai kosong pada kolom harga", status: "pass" as const },
  { name: "Duplikat primary key", detail: "0 duplikat (symbol + loaded_at)", status: "pass" as const },
  { name: "Freshness ingest", detail: "Data terakhir masuk 42 detik lalu", status: "pass" as const },
  { name: "Range harga wajar", detail: "1 nilai di luar batas 3-sigma", status: "warn" as const },
];

export const ANOMALIES = [
  {
    symbol: "DOGE",
    name: "Dogecoin",
    kind: "Lonjakan ekstrem",
    detail: "Harga naik 6.48% dalam 1 jam, 3.4x deviasi standar historis.",
    severity: "high" as const,
    at: "17:04",
  },
  {
    symbol: "LINK",
    name: "Chainlink",
    kind: "Penurunan tajam",
    detail: "Turun 2.18% dengan volume 1.8x rata-rata harian.",
    severity: "medium" as const,
    at: "16:31",
  },
  {
    symbol: "ADA",
    name: "Cardano",
    kind: "Volume tidak wajar",
    detail: "Volume 24 jam 62% di bawah baseline 30 hari.",
    severity: "low" as const,
    at: "15:58",
  },
];

export const AI_INSIGHTS = [
  {
    title: "Sentimen pasar bullish moderat",
    body: "8 dari 10 koin pantauan bergerak positif dalam 24 jam terakhir dengan rata-rata perubahan +1.45%. Momentum terkuat datang dari aset beta tinggi (DOGE, SOL, AVAX), pola khas fase risk-on awal.",
  },
  {
    title: "Rotasi modal ke altcoin",
    body: "Dominasi Bitcoin melemah 0.6 poin sementara volume altcoin naik 18%. Sinyal awal rotasi likuiditas dari BTC ke aset lapis dua.",
  },
  {
    title: "Risiko yang perlu diawasi",
    body: "Lonjakan DOGE tidak didukung penguatan fundamental dan tercatat sebagai anomali statistik. Perlakukan sebagai pergerakan spekulatif jangka pendek, bukan tren.",
  },
];

export const PIPELINE_STAGES = [
  { name: "Ingest API", detail: "CoinGecko REST", status: "healthy", meta: "12 rb rec/jam" },
  { name: "Stream Kafka", detail: "topic: crypto.ticks", status: "healthy", meta: "lag 0.4s" },
  { name: "Transform dbt", detail: "18 model, 42 test", status: "healthy", meta: "run 1m 12s" },
  { name: "Orkestrasi Airflow", detail: "DAG crypto_hourly", status: "healthy", meta: "sukses 99.2%" },
];

export function formatPrice(value: number) {
  return value >= 100
    ? `$${value.toLocaleString("en-US", { maximumFractionDigits: 0 })}`
    : `$${value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`;
}

export function formatCompact(value: number) {
  return `$${new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 2 }).format(value)}`;
}

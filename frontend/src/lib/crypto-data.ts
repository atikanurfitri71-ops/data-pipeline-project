export type Coin = {
  symbol: string;
  name: string;
  price: number;
  change24h: number;
  volume: number;
  marketCap: number;
};

export type SeriesPoint = { t: string } & Record<string, number | string>;

export type Insight = { title: string; body: string };

export type Anomaly = {
  name: string;
  detail: string;
  at: string;
};

export type QualitySummary = {
  status: "pass" | "fail" | string;
  totalIn: number;
  totalOut: number;
  missing: number;
  duplicates: number;
  anomalies: number;
  runAt: string;
};

const API_URL = import.meta.env.VITE_API_URL;

export async function fetchCoins(): Promise<Coin[]> {

  const res = await fetch(`${API_URL}/api/coins`);
  return res.json();
}

export async function fetchSeries(): Promise<SeriesPoint[]> {
  const res = await fetch(`${API_URL}/api/price-series`);
  return res.json();
}

export async function fetchInsightsAndAnomalies(): Promise<{
  insights: Insight[];
  anomalies: Anomaly[];
}> {
  const res = await fetch(`${API_URL}/api/insights`);
  const rows: {
    coin_name: string;
    insight_type: string;
    insight_text: string;
    is_anomaly: boolean;
    generated_at: string;
  }[] = await res.json();

  const insights = rows
    .filter((r) => !r.is_anomaly)
    .map((r) => ({ title: `${r.coin_name} · ${r.insight_type}`, body: r.insight_text }));

  const anomalies = rows
    .filter((r) => r.is_anomaly)
    .map((r) => ({
      name: r.coin_name,
      detail: r.insight_text,
      at: new Date(r.generated_at).toLocaleTimeString("id-ID"),

    }));

  return { insights, anomalies };
}

export async function fetchQuality(): Promise<QualitySummary | null> {
  const res = await fetch(`${API_URL}/api/quality`);
  const q = await res.json();
  if (!q || Object.keys(q).length === 0) return null;
  return {
    status: q.status,
    totalIn: q.total_records_in,
    totalOut: q.total_records_out,
    missing: q.missing_values_count,
    duplicates: q.duplicate_count,
    anomalies: q.anomaly_count,
    runAt: new Date(q.run_timestamp).toLocaleString("id-ID"),
  };
}

export function formatPrice(value: number) {
  return value >= 100
    ? `$${value.toLocaleString("en-US", { maximumFractionDigits: 0 })}`
    : `$${value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`;
}

export function formatCompact(value: number) {
  return `$${new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 2 }).format(value)}`;
}
export type PipelineStatus = {
  lastExtract: string | null;
  lastStream: string | null;
  qualityStatus: string | null;
};

export async function fetchPipelineStatus(): Promise<PipelineStatus> {
  const res = await fetch(`${API_URL}/api/pipeline-status`);
  const p = await res.json();
  return {
    lastExtract: p.last_extract ? new Date(p.last_extract).toLocaleTimeString("id-ID") : null,
    lastStream: p.last_stream ? new Date(p.last_stream).toLocaleTimeString("id-ID") : null,
    qualityStatus: p.quality_status ?? null,
  };
}
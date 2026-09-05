import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  CartesianGrid,
} from "recharts";
import {
  Activity,
  ArrowDownRight,
  ArrowUpRight,
  BrainCircuit,
  CheckCircle2,
  Database,
  Github,
  Linkedin,
  ShieldAlert,
  TriangleAlert,
} from "lucide-react";
import {
  AI_INSIGHTS,
  ANOMALIES,
  COINS,
  PIPELINE_STAGES,
  QUALITY_CHECKS,
  buildSeries,
  formatCompact,
  formatPrice,
  type Coin,
} from "@/lib/crypto-data";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Crypto Data Pipeline Dashboard — Portofolio Data Engineering" },
      {
        name: "description",
        content:
          "Dashboard portofolio pemantauan harga kripto real-time: insight AI, tabel harga dan perubahan 24 jam, hasil data quality control, dan deteksi anomali nilai ekstrem.",
      },
      { property: "og:title", content: "Crypto Data Pipeline Dashboard — Portofolio Data Engineering" },
      {
        property: "og:description",
        content:
          "Pemantauan harga kripto real-time dengan insight AI, data quality control, dan deteksi anomali.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Dashboard,
});

const CHART_COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
];

function ChangeBadge({ value }: { value: number }) {
  const up = value >= 0;
  return (
    <span
      className="num inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium"
      style={{
        color: up ? "var(--up)" : "var(--down)",
        backgroundColor: `color-mix(in oklab, ${up ? "var(--up)" : "var(--down)"} 14%, transparent)`,
      }}
    >
      {up ? <ArrowUpRight className="size-3" /> : <ArrowDownRight className="size-3" />}
      {up ? "+" : ""}
      {value.toFixed(2)}%
    </span>
  );
}

function SectionTitle({
  icon,
  title,
  subtitle,
}: {
  icon: React.ReactNode;
  title: string;
  subtitle?: string;
}) {
  return (
    <div className="mb-5 flex items-start gap-3">
      <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-secondary text-primary">
        {icon}
      </div>
      <div>
        <h2 className="text-lg font-semibold">{title}</h2>
        {subtitle ? <p className="text-sm text-muted-foreground">{subtitle}</p> : null}
      </div>
    </div>
  );
}

function Dashboard() {
  const baseSeries = useMemo(() => buildSeries(COINS), []);
  const [selected, setSelected] = useState<string[]>(["BTC", "ETH", "SOL"]);
  const [tick, setTick] = useState(0);
  const [clock, setClock] = useState<string | null>(null);

  useEffect(() => {
    const id = setInterval(() => {
      setTick((t) => t + 1);
      setClock(
        new Date().toLocaleTimeString("id-ID", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        }),
      );
    }, 3000);
    setClock(
      new Date().toLocaleTimeString("id-ID", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      }),
    );
    return () => clearInterval(id);
  }, []);

  const coins: Coin[] = useMemo(
    () =>
      COINS.map((c, i) => {
        if (tick === 0) return c;
        const jitter = Math.sin(tick * 0.7 + i) * 0.0035;
        return {
          ...c,
          price: c.price * (1 + jitter),
          change24h: c.change24h + jitter * 100,
        };
      }),
    [tick],
  );

  const positives = coins.filter((c) => c.change24h >= 0).length;
  const avgChange = coins.reduce((s, c) => s + c.change24h, 0) / coins.length;
  const totalVolume = coins.reduce((s, c) => s + c.volume, 0);
  const shown = selected.length ? selected : ["BTC"];

  const toggle = (symbol: string) =>
    setSelected((prev) =>
      prev.includes(symbol) ? prev.filter((s) => s !== symbol) : [...prev, symbol],
    );

  return (
    <main className="min-h-screen">
      <div className="glow-top border-b border-border">
        <header className="mx-auto max-w-7xl px-6 py-14 md:py-20">
          <div className="flex flex-wrap items-center gap-3">
            <span className="inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1 text-xs text-muted-foreground">
              <span className="relative flex size-2">
                <span className="live-dot size-2 rounded-full" />
                <span className="size-2 rounded-full bg-up" />
              </span>
              Live · auto-refresh 3 detik
            </span>
            <span className="rounded-full border border-border bg-surface px-3 py-1 text-xs text-muted-foreground">
              Portofolio Data Engineering
            </span>
          </div>

          <h1 className="mt-6 max-w-3xl text-4xl font-bold leading-tight md:text-6xl">
            Crypto Data Pipeline{" "}
            <span className="text-primary">Dashboard</span>
          </h1>
          <p className="mt-4 max-w-2xl text-base text-muted-foreground md:text-lg">
            Pemantauan harga kripto secara real-time dari pipeline ETL end-to-end: ingest API,
            streaming Kafka, transformasi dbt, dan orkestrasi Airflow — dilengkapi insight AI,
            kontrol kualitas data, serta deteksi anomali nilai ekstrem.
          </p>

          <dl className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { label: "Koin dipantau", value: `${coins.length}`, hint: "refresh tiap 3 detik" },
              {
                label: "Rata-rata 24 jam",
                value: `${avgChange >= 0 ? "+" : ""}${avgChange.toFixed(2)}%`,
                hint: `${positives} naik · ${coins.length - positives} turun`,
              },
              { label: "Volume 24 jam", value: formatCompact(totalVolume), hint: "agregat pasar" },
              {
                label: "Update terakhir",
                value: clock ?? "—",
                hint: "waktu lokal browser",
              },
            ].map((s) => (
              <div key={s.label} className="panel p-5">
                <dt className="text-xs uppercase tracking-wider text-muted-foreground">
                  {s.label}
                </dt>
                <dd className="num mt-2 text-2xl font-semibold">{s.value}</dd>
                <p className="mt-1 text-xs text-muted-foreground">{s.hint}</p>
              </div>
            ))}
          </dl>
        </header>
      </div>

      <div className="mx-auto max-w-7xl space-y-8 px-6 py-12">
        {/* Pipeline health */}
        <section className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {PIPELINE_STAGES.map((stage) => (
            <div key={stage.name} className="panel flex items-start gap-3 p-5">
              <Activity className="mt-0.5 size-4 text-primary" />
              <div>
                <p className="text-sm font-medium">{stage.name}</p>
                <p className="text-xs text-muted-foreground">{stage.detail}</p>
                <p className="num mt-2 text-xs text-primary">{stage.meta}</p>
              </div>
            </div>
          ))}
        </section>

        {/* Chart + AI insight */}
        <section className="grid gap-6 lg:grid-cols-3">
          <div className="panel p-6 lg:col-span-2">
            <SectionTitle
              icon={<Activity className="size-5" />}
              title="Trend harga per koin"
              subtitle="Pergerakan harga 24 jam terakhir (batch Airflow, granularitas 1 jam)"
            />
            <div className="mb-4 flex flex-wrap gap-2">
              {COINS.map((c) => {
                const active = shown.includes(c.symbol);
                return (
                  <button
                    key={c.symbol}
                    onClick={() => toggle(c.symbol)}
                    className={`num rounded-full border px-3 py-1 text-xs transition-colors ${
                      active
                        ? "border-primary bg-primary/15 text-primary"
                        : "border-border bg-surface-2 text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {c.symbol}
                  </button>
                );
              })}
            </div>
            <div className="h-[320px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={baseSeries}>
                  <CartesianGrid stroke="var(--border)" vertical={false} />
                  <XAxis
                    dataKey="t"
                    stroke="var(--muted-foreground)"
                    tick={{ fontSize: 11 }}
                    tickLine={false}
                  />
                  <YAxis
                    stroke="var(--muted-foreground)"
                    tick={{ fontSize: 11 }}
                    tickLine={false}
                    scale="log"
                    domain={["auto", "auto"]}
                    tickFormatter={(v: number) =>
                      v >= 1000 ? `${(v / 1000).toFixed(0)}k` : `${v}`
                    }
                  />
                  <Tooltip
                    contentStyle={{
                      background: "var(--surface-2)",
                      border: "1px solid var(--border)",
                      borderRadius: "12px",
                      fontSize: 12,
                    }}
                    labelStyle={{ color: "var(--muted-foreground)" }}
                  />
                  {shown.map((symbol) => (
                    <Line
                      key={symbol}
                      type="monotone"
                      dataKey={symbol}
                      stroke={CHART_COLORS[COINS.findIndex((c) => c.symbol === symbol) % 5]}
                      strokeWidth={2}
                      dot={false}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            </div>
            <p className="mt-3 text-xs text-muted-foreground">
              Skala logaritmik agar koin dengan harga sangat berbeda tetap terbaca dalam satu grafik.
            </p>
          </div>

          <div className="panel p-6">
            <SectionTitle
              icon={<BrainCircuit className="size-5" />}
              title="Insight AI"
              subtitle="Ringkasan otomatis dari data terbaru"
            />
            <div className="space-y-4">
              {AI_INSIGHTS.map((ins) => (
                <article key={ins.title} className="rounded-lg bg-surface-2 p-4">
                  <h3 className="text-sm font-semibold text-primary">{ins.title}</h3>
                  <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">{ins.body}</p>
                </article>
              ))}
            </div>
          </div>
        </section>

        {/* Table */}
        <section className="panel p-6">
          <SectionTitle
            icon={<Database className="size-5" />}
            title="Tabel data harga"
            subtitle="Snapshot terakhir dari tabel mart_crypto_prices"
          />
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs uppercase tracking-wider text-muted-foreground">
                  <th className="py-3 pr-4 font-medium">Koin</th>
                  <th className="py-3 pr-4 font-medium">Harga</th>
                  <th className="py-3 pr-4 font-medium">Perubahan 24 jam</th>
                  <th className="py-3 pr-4 font-medium">Volume 24 jam</th>
                  <th className="py-3 pr-4 font-medium">Kapitalisasi pasar</th>
                  <th className="py-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {coins.map((c) => {
                  const flagged = ANOMALIES.some((a) => a.symbol === c.symbol);
                  return (
                    <tr key={c.symbol} className="border-b border-border/60 last:border-0">
                      <td className="py-3 pr-4">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{c.name}</span>
                          <span className="num text-xs text-muted-foreground">{c.symbol}</span>
                        </div>
                      </td>
                      <td className="num py-3 pr-4">{formatPrice(c.price)}</td>
                      <td className="py-3 pr-4">
                        <ChangeBadge value={c.change24h} />
                      </td>
                      <td className="num py-3 pr-4 text-muted-foreground">
                        {formatCompact(c.volume)}
                      </td>
                      <td className="num py-3 pr-4 text-muted-foreground">
                        {formatCompact(c.marketCap)}
                      </td>
                      <td className="py-3">
                        {flagged ? (
                          <span className="inline-flex items-center gap-1 text-xs text-warn">
                            <TriangleAlert className="size-3.5" /> Anomali
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                            <CheckCircle2 className="size-3.5 text-up" /> Normal
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>

        {/* Quality + anomaly */}
        <section className="grid gap-6 lg:grid-cols-2">
          <div className="panel p-6">
            <SectionTitle
              icon={<CheckCircle2 className="size-5" />}
              title="Data quality control"
              subtitle="Hasil test dbt pada run terakhir"
            />
            <div className="mb-5 flex items-center gap-4 rounded-lg bg-surface-2 p-4">
              <span className="flex size-12 items-center justify-center rounded-full bg-up/15 text-up">
                <CheckCircle2 className="size-6" />
              </span>
              <div>
                <p className="num text-2xl font-semibold text-up">PASS</p>
                <p className="text-xs text-muted-foreground">
                  Records in → out: 12.480 → 12.480 · 1 peringatan
                </p>
              </div>
            </div>
            <ul className="space-y-3">
              {QUALITY_CHECKS.map((q) => (
                <li key={q.name} className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm font-medium">{q.name}</p>
                    <p className="text-xs text-muted-foreground">{q.detail}</p>
                  </div>
                  <span
                    className="shrink-0 rounded-full px-2 py-0.5 text-xs font-medium"
                    style={{
                      color: q.status === "pass" ? "var(--up)" : "var(--warn)",
                      backgroundColor: `color-mix(in oklab, ${
                        q.status === "pass" ? "var(--up)" : "var(--warn)"
                      } 14%, transparent)`,
                    }}
                  >
                    {q.status === "pass" ? "PASS" : "WARN"}
                  </span>
                </li>
              ))}
            </ul>
          </div>

          <div className="panel p-6">
            <SectionTitle
              icon={<ShieldAlert className="size-5" />}
              title="Deteksi anomali & nilai ekstrem"
              subtitle="Z-score 3-sigma pada harga dan volume"
            />
            <div className="space-y-3">
              {ANOMALIES.map((a) => {
                const color =
                  a.severity === "high"
                    ? "var(--down)"
                    : a.severity === "medium"
                      ? "var(--warn)"
                      : "var(--accent)";
                return (
                  <article
                    key={a.symbol}
                    className="rounded-lg border-l-2 bg-surface-2 p-4"
                    style={{ borderLeftColor: color }}
                  >
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm font-semibold">
                        {a.name} <span className="num text-xs text-muted-foreground">{a.symbol}</span>
                      </p>
                      <span className="num text-xs text-muted-foreground">{a.at}</span>
                    </div>
                    <p className="mt-1 text-xs font-medium" style={{ color }}>
                      {a.kind} · severity {a.severity}
                    </p>
                    <p className="mt-1.5 text-sm text-muted-foreground">{a.detail}</p>
                  </article>
                );
              })}
            </div>
          </div>
        </section>
      </div>

      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-10 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-medium">Atika Nurfitri · Data Engineering Portfolio</p>
            <p className="text-xs text-muted-foreground">
              Angka pada halaman ini adalah data demo untuk keperluan portofolio.
            </p>
          </div>
          <div className="flex gap-3 text-muted-foreground">
            <a
              href="https://github.com"
              className="rounded-lg border border-border bg-surface p-2 transition-colors hover:text-primary"
              aria-label="GitHub"
            >
              <Github className="size-4" />
            </a>
            <a
              href="https://linkedin.com"
              className="rounded-lg border border-border bg-surface p-2 transition-colors hover:text-primary"
              aria-label="LinkedIn"
            >
              <Linkedin className="size-4" />
            </a>
          </div>
        </div>
      </footer>
    </main>
  );
}

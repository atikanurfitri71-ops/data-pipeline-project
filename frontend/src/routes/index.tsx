import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useState } from "react";
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
  XCircle,
} from "lucide-react";

import {
  fetchCoins,
  fetchSeries,
  fetchInsightsAndAnomalies,
  fetchQuality,
  fetchPipelineStatus,
  formatCompact,
  formatPrice,
  type Coin,
  type SeriesPoint,
  type Insight,
  type Anomaly,
  type QualitySummary,
  type PipelineStatus,
} from "@/lib/crypto-data";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      {
        title: "Crypto Data Pipeline Dashboard — Portofolio Data Engineering",
      },
      {
        name: "description",
        content:
          "Dashboard portofolio pemantauan harga kripto real-time: insight AI, tabel harga dan perubahan 24 jam, hasil data quality control, dan deteksi anomali nilai ekstrem.",
      },
      {
        property: "og:title",
        content:
          "Crypto Data Pipeline Dashboard — Portofolio Data Engineering",
      },
      {
        property: "og:description",
        content:
          "Pemantauan harga kripto real-time dengan insight AI, data quality control, dan deteksi anomali.",
      },
      {
        property: "og:type",
        content: "website",
      },
      {
        name: "twitter:card",
        content: "summary_large_image",
      },
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

/* =========================================================
   CHANGE BADGE
========================================================= */

function ChangeBadge({ value }: { value: number }) {
  const up = value >= 0;

  return (
    <span
      className="num inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium"
      style={{
        color: up ? "var(--up)" : "var(--down)",
        backgroundColor: `color-mix(in oklab, ${
          up ? "var(--up)" : "var(--down)"
        } 14%, transparent)`,
      }}
    >
      {up ? (
        <ArrowUpRight className="size-3" />
      ) : (
        <ArrowDownRight className="size-3" />
      )}

      {up ? "+" : ""}
      {value.toFixed(2)}%
    </span>
  );
}

/* =========================================================
   SECTION TITLE
========================================================= */

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

        {subtitle ? (
          <p className="text-sm text-muted-foreground">{subtitle}</p>
        ) : null}
      </div>
    </div>
  );
}

/* =========================================================
   DASHBOARD
========================================================= */

function Dashboard() {
  const [coins, setCoins] = useState<Coin[]>([]);
  const [series, setSeries] = useState<SeriesPoint[]>([]);
  const [insights, setInsights] = useState<Insight[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [quality, setQuality] = useState<QualitySummary | null>(null);
  const [pipeline, setPipeline] = useState<PipelineStatus | null>(null);

  const [selected, setSelected] = useState<string[]>([
    "BTC",
    "ETH",
    "SOL",
  ]);

  const [clock, setClock] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  /* =========================================================
     LOAD DATA
  ========================================================= */

  const loadAll = useCallback(async () => {
    try {
      const [c, s, ia, q, p] = await Promise.all([
        fetchCoins(),
        fetchSeries(),
        fetchInsightsAndAnomalies(),
        fetchQuality(),
        fetchPipelineStatus(),
      ]);

      setCoins(c);
      setSeries(s);
      setInsights(ia.insights);
      setAnomalies(ia.anomalies);
      setQuality(q);
      setPipeline(p);

      setClock(
        new Date().toLocaleTimeString("id-ID", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
        }),
      );
    } catch (err) {
      console.error("Gagal memuat data dashboard:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  /* =========================================================
     AUTO REFRESH
  ========================================================= */

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      if (mounted) {
        await loadAll();
      }
    };

    load();

    const id = window.setInterval(load, 5000);

    return () => {
      mounted = false;
      window.clearInterval(id);
    };
  }, [loadAll]);

  /* =========================================================
     CALCULATIONS
  ========================================================= */

  const positives = coins.filter(
    (coin) => coin.change24h >= 0,
  ).length;

  const avgChange = coins.length
    ? coins.reduce(
        (sum, coin) => sum + coin.change24h,
        0,
      ) / coins.length
    : 0;

  const totalVolume = coins.reduce(
    (sum, coin) => sum + coin.volume,
    0,
  );

  const shown =
    selected.length > 0
      ? selected
      : coins[0]
        ? [coins[0].symbol]
        : [];

  /* =========================================================
     TOGGLE COIN
  ========================================================= */

  const toggle = (symbol: string) => {
    setSelected((prev) =>
      prev.includes(symbol)
        ? prev.filter((s) => s !== symbol)
        : [...prev, symbol],
    );
  };

  /* =========================================================
     LOADING
  ========================================================= */

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <Activity className="mx-auto mb-3 size-6 animate-pulse text-primary" />

          <p className="text-sm text-muted-foreground">
            Memuat data pipeline...
          </p>
        </div>
      </main>
    );
  }

  /* =========================================================
     MAIN
  ========================================================= */

  return (
    <main className="min-h-screen">

      {/* =====================================================
          HEADER
      ===================================================== */}

      <div className="glow-top border-b border-border">
        <header className="mx-auto max-w-7xl px-6 py-14 md:py-20">

          <div className="flex flex-wrap items-center gap-3">

            <span className="inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1 text-xs text-muted-foreground">

              <span className="relative flex size-2">
                <span className="live-dot size-2 rounded-full" />
                <span className="size-2 rounded-full bg-up" />
              </span>

              Live · auto-refresh 5 detik
            </span>

            <span className="rounded-full border border-border bg-surface px-3 py-1 text-xs text-muted-foreground">
              Portofolio Data Engineering
            </span>

          </div>

          <h1 className="mt-6 max-w-3xl text-4xl font-bold leading-tight md:text-6xl">
            Crypto Data Pipeline{" "}
            <span className="text-primary">
              Dashboard
            </span>
          </h1>

          <p className="mt-4 max-w-2xl text-base text-muted-foreground md:text-lg">
            Pemantauan harga kripto secara real-time dari
            pipeline ETL end-to-end: ingest API, streaming
            Kafka, transformasi dbt, dan orkestrasi Airflow —
            dilengkapi insight AI, kontrol kualitas data,
            serta deteksi anomali nilai ekstrem.
          </p>

          {/* =================================================
              SUMMARY
          ================================================= */}

          <dl className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

            {[
              {
                label: "Koin dipantau",
                value: `${coins.length}`,
                hint: "refresh tiap 5 detik",
              },
              {
                label: "Rata-rata 24 jam",
                value: `${avgChange >= 0 ? "+" : ""}${avgChange.toFixed(
                  2,
                )}%`,
                hint: `${positives} naik · ${
                  coins.length - positives
                } turun`,
              },
              {
                label: "Volume 24 jam",
                value: formatCompact(totalVolume),
                hint: "agregat pasar",
              },
              {
                label: "Update terakhir",
                value: clock ?? "—",
                hint: "waktu lokal browser",
              },
            ].map((stat) => (
              <div
                key={stat.label}
                className="panel p-5"
              >
                <dt className="text-xs uppercase tracking-wider text-muted-foreground">
                  {stat.label}
                </dt>

                <dd className="num mt-2 text-2xl font-semibold">
                  {stat.value}
                </dd>

                <p className="mt-1 text-xs text-muted-foreground">
                  {stat.hint}
                </p>
              </div>
            ))}

          </dl>
        </header>
      </div>

      {/* =====================================================
          CONTENT
      ===================================================== */}

      <div className="mx-auto max-w-7xl space-y-8 px-6 py-12">

        {/* ===================================================
            PIPELINE HEALTH
        =================================================== */}

        <section className="grid gap-4 md:grid-cols-3">

          <div className="panel flex items-start gap-3 p-5">
            <Activity className="mt-0.5 size-4 text-primary" />

            <div>
              <p className="text-sm font-medium">
                Ingest batch (Airflow)
              </p>

              <p className="text-xs text-muted-foreground">
                Tabel crypto_prices
              </p>

              <p className="num mt-2 text-xs text-primary">
                {pipeline?.lastExtract
                  ? `Terakhir: ${pipeline.lastExtract}`
                  : "Belum ada data"}
              </p>
            </div>
          </div>

          <div className="panel flex items-start gap-3 p-5">
            <Activity className="mt-0.5 size-4 text-primary" />

            <div>
              <p className="text-sm font-medium">
                Streaming Kafka
              </p>

              <p className="text-xs text-muted-foreground">
                Tabel crypto_prices_streaming
              </p>

              <p className="num mt-2 text-xs text-primary">
                {pipeline?.lastStream
                  ? `Terakhir: ${pipeline.lastStream}`
                  : "Belum ada data"}
              </p>
            </div>
          </div>

          <div className="panel flex items-start gap-3 p-5">
            <Activity className="mt-0.5 size-4 text-primary" />

            <div>
              <p className="text-sm font-medium">
                Data quality run
              </p>

              <p className="text-xs text-muted-foreground">
                Log terakhir
              </p>

              <p className="num mt-2 text-xs text-primary">
                {pipeline?.qualityStatus
                  ? pipeline.qualityStatus.toUpperCase()
                  : "Belum ada data"}
              </p>
            </div>
          </div>

        </section>

        {/* ===================================================
            CHART + AI
        =================================================== */}

        <section className="grid gap-6 lg:grid-cols-3">

          {/* CHART */}

          <div className="panel p-6 lg:col-span-2">

            <SectionTitle
              icon={<Activity className="size-5" />}
              title="Trend harga per koin"
              subtitle="Riwayat harga dari tabel crypto_prices"
            />

            {/* COIN FILTER */}

            <div className="mb-4 flex flex-wrap gap-2">

              {coins.map((coin) => {
                const active = shown.includes(
                  coin.symbol,
                );

                return (
                  <button
                    key={coin.symbol}
                    type="button"
                    onClick={() =>
                      toggle(coin.symbol)
                    }
                    aria-pressed={active}
                    className={`num rounded-full border px-3 py-1 text-xs transition-colors ${
                      active
                        ? "border-primary bg-primary/15 text-primary"
                        : "border-border bg-surface-2 text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {coin.symbol}
                  </button>
                );
              })}

            </div>

            {/* CHART */}

            <div className="h-[320px]">

              {series.length === 0 ? (
                <div className="flex h-full items-center justify-center">
                  <p className="text-sm text-muted-foreground">
                    Belum ada data historis.
                  </p>
                </div>
              ) : (
                <ResponsiveContainer
                  width="100%"
                  height="100%"
                >
                  <LineChart data={series}>

                    <CartesianGrid
                      stroke="var(--border)"
                      vertical={false}
                    />

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
                      tickFormatter={(value: number) =>
                        value >= 1000
                          ? `${(
                              value / 1000
                            ).toFixed(0)}k`
                          : `${value}`
                      }
                    />

                    <Tooltip
                      contentStyle={{
                        background:
                          "var(--surface-2)",
                        border:
                          "1px solid var(--border)",
                        borderRadius: "12px",
                        fontSize: 12,
                      }}
                      labelStyle={{
                        color:
                          "var(--muted-foreground)",
                      }}
                    />

                    {shown.map((symbol) => {

                      const coinIndex =
                        coins.findIndex(
                          (coin) =>
                            coin.symbol === symbol,
                        );

                      return (
                        <Line
                          key={symbol}
                          type="monotone"
                          dataKey={symbol}
                          stroke={
                            CHART_COLORS[
                              coinIndex >= 0
                                ? coinIndex %
                                  CHART_COLORS.length
                                : 0
                            ]
                          }
                          strokeWidth={2}
                          dot={false}
                          connectNulls
                        />
                      );
                    })}

                  </LineChart>
                </ResponsiveContainer>
              )}

            </div>

            <p className="mt-3 text-xs text-muted-foreground">
              Skala logaritmik digunakan agar koin dengan
              perbedaan harga yang besar tetap dapat terbaca
              dalam satu grafik.
            </p>

          </div>

          {/* AI INSIGHT */}

          <div className="panel p-6">

            <SectionTitle
              icon={
                <BrainCircuit className="size-5" />
              }
              title="Insight AI"
              subtitle="Dari tabel ai_dialog_feed"
            />

            <div className="space-y-4">

              {insights.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Belum ada insight tersedia.
                </p>
              ) : (
                insights.map((insight, index) => (
                  <article
                    key={`${insight.title}-${index}`}
                    className="rounded-lg bg-surface-2 p-4"
                  >
                    <h3 className="text-sm font-semibold text-primary">
                      {insight.title}
                    </h3>

                    <p className="mt-1.5 text-sm leading-relaxed text-muted-foreground">
                      {insight.body}
                    </p>
                  </article>
                ))
              )}

            </div>

          </div>
        </section>

        {/* ===================================================
            PRICE TABLE
        =================================================== */}

        <section className="panel p-6">

          <SectionTitle
            icon={<Database className="size-5" />}
            title="Tabel data harga"
            subtitle="Snapshot terakhir dari tabel crypto_prices"
          />

          <div className="overflow-x-auto">

            <table className="w-full min-w-[720px] text-sm">

              <thead>
                <tr className="border-b border-border text-left text-xs uppercase tracking-wider text-muted-foreground">

                  <th className="py-3 pr-4 font-medium">
                    Koin
                  </th>

                  <th className="py-3 pr-4 font-medium">
                    Harga
                  </th>

                  <th className="py-3 pr-4 font-medium">
                    Perubahan 24 jam
                  </th>

                  <th className="py-3 pr-4 font-medium">
                    Volume 24 jam
                  </th>

                  <th className="py-3 pr-4 font-medium">
                    Kapitalisasi pasar
                  </th>

                  <th className="py-3 font-medium">
                    Status
                  </th>

                </tr>
              </thead>

              <tbody>

                {coins.length === 0 ? (
                  <tr>
                    <td
                      colSpan={6}
                      className="py-8 text-center text-sm text-muted-foreground"
                    >
                      Tidak ada data koin.
                    </td>
                  </tr>
                ) : (
                  coins.map((coin) => {

                    const flagged =
                      anomalies.some(
                        (anomaly) =>
                          anomaly.name ===
                          coin.name,
                      );

                    return (
                      <tr
                        key={coin.symbol}
                        className="border-b border-border/60 last:border-0"
                      >

                        <td className="py-3 pr-4">

                          <div className="flex items-center gap-2">

                            <span className="font-medium">
                              {coin.name}
                            </span>

                            <span className="num text-xs text-muted-foreground">
                              {coin.symbol}
                            </span>

                          </div>

                        </td>

                        <td className="num py-3 pr-4">
                          {formatPrice(coin.price)}
                        </td>

                        <td className="py-3 pr-4">
                          <ChangeBadge
                            value={coin.change24h}
                          />
                        </td>

                        <td className="num py-3 pr-4 text-muted-foreground">
                          {formatCompact(
                            coin.volume,
                          )}
                        </td>

                        <td className="num py-3 pr-4 text-muted-foreground">
                          {formatCompact(
                            coin.marketCap,
                          )}
                        </td>

                        <td className="py-3">

                          {flagged ? (
                            <span className="inline-flex items-center gap-1 text-xs text-warn">
                              <TriangleAlert className="size-3.5" />
                              Anomali
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-xs text-muted-foreground">
                              <CheckCircle2 className="size-3.5 text-up" />
                              Normal
                            </span>
                          )}

                        </td>

                      </tr>
                    );
                  })
                )}

              </tbody>
            </table>

          </div>
        </section>

        {/* ===================================================
            QUALITY + ANOMALY
        =================================================== */}

        <section className="grid gap-6 lg:grid-cols-2">

          {/* DATA QUALITY */}

          <div className="panel p-6">

            <SectionTitle
              icon={
                <CheckCircle2 className="size-5" />
              }
              title="Data quality control"
              subtitle="Ringkasan run terakhir dari data_quality_log"
            />

            {quality ? (
              <>
                <div className="mb-5 flex items-center gap-4 rounded-lg bg-surface-2 p-4">

                  <span
                    className={`flex size-12 items-center justify-center rounded-full ${
                      quality.status === "pass"
                        ? "text-up"
                        : "text-warn"
                    }`}
                    style={{
                      backgroundColor:
                        quality.status === "pass"
                          ? "color-mix(in oklab, var(--up) 15%, transparent)"
                          : "color-mix(in oklab, var(--warn) 15%, transparent)",
                    }}
                  >
                    {quality.status === "pass" ? (
                      <CheckCircle2 className="size-6" />
                    ) : (
                      <XCircle className="size-6" />
                    )}
                  </span>

                  <div>

                    <p
                      className={`num text-2xl font-semibold ${
                        quality.status === "pass"
                          ? "text-up"
                          : "text-warn"
                      }`}
                    >
                      {quality.status.toUpperCase()}
                    </p>

                    <p className="text-xs text-muted-foreground">
                      Records in → out:{" "}
                      {quality.totalIn.toLocaleString(
                        "id-ID",
                      )}{" "}
                      →{" "}
                      {quality.totalOut.toLocaleString(
                        "id-ID",
                      )}{" "}
                      · run {quality.runAt}
                    </p>

                  </div>
                </div>

                <ul className="space-y-3">

                  {[
                    {
                      name: "Missing values",
                      detail: `${quality.missing} nilai kosong terdeteksi`,
                    },
                    {
                      name: "Duplikat",
                      detail: `${quality.duplicates} baris duplikat terdeteksi`,
                    },
                    {
                      name: "Anomali",
                      detail: `${quality.anomalies} anomali terdeteksi pada run ini`,
                    },
                  ].map((item) => (
                    <li
                      key={item.name}
                      className="flex items-start justify-between gap-4"
                    >
                      <div>

                        <p className="text-sm font-medium">
                          {item.name}
                        </p>

                        <p className="text-xs text-muted-foreground">
                          {item.detail}
                        </p>

                      </div>
                    </li>
                  ))}

                </ul>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">
                Belum ada log data quality.
              </p>
            )}

          </div>

          {/* ANOMALY */}

          <div className="panel p-6">

            <SectionTitle
              icon={
                <ShieldAlert className="size-5" />
              }
              title="Deteksi anomali"
              subtitle="Dari tabel ai_dialog_feed (is_anomaly = true)"
            />

            <div className="space-y-3">

              {anomalies.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  Tidak ada anomali terdeteksi saat ini.
                </p>
              ) : (
                anomalies.map((anomaly, index) => (
                  <article
                    key={`${anomaly.name}-${index}`}
                    className="rounded-lg border-l-2 bg-surface-2 p-4"
                    style={{
                      borderLeftColor:
                        "var(--down)",
                    }}
                  >

                    <div className="flex items-center justify-between gap-3">

                      <p className="text-sm font-semibold">
                        {anomaly.name}
                      </p>

                      <span className="num text-xs text-muted-foreground">
                        {anomaly.at}
                      </span>

                    </div>

                    <p className="mt-1.5 text-sm text-muted-foreground">
                      {anomaly.detail}
                    </p>

                  </article>
                ))
              )}

            </div>
          </div>

        </section>

      </div>

      {/* =====================================================
          FOOTER
      ===================================================== */}

      <footer className="border-t border-border">

        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-6 py-10 sm:flex-row sm:items-center sm:justify-between">

          <div>

            <p className="text-sm font-medium">
              Atika Nurfitri · Data Engineering Portfolio
            </p>

            <p className="text-xs text-muted-foreground">
              Data pada halaman ini diambil langsung dari
              pipeline ETL/Kafka secara real-time.
            </p>

          </div>

          <div className="flex gap-3 text-muted-foreground">

            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-lg border border-border bg-surface p-2 transition-colors hover:text-primary"
              aria-label="GitHub"
            >
              <Github className="size-4" />
            </a>

            <a
              href="https://linkedin.com"
              target="_blank"
              rel="noopener noreferrer"
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
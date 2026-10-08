"use client";
import { api } from "@/lib/api";
import usePolling from "@/hooks/usePolling";
import { ErrorBox, Loading } from "@/components/ui";

const pct = (v) => (v == null ? "—" : `${v}%`);

export default function StatsPage() {
  const { data: s, error, loading, refresh } = usePolling(() => api("/api/admin/stats"), 30000, "stats");

  if (loading) return <Loading />;
  if (!s) return <ErrorBox message={error || "No stats available."} onRetry={refresh} />;

  const cards = [
    ["Total tickets", s.total_tickets],
    ["AI category accepted", pct(s.category_accepted_pct)],
    ["AI priority accepted", pct(s.priority_accepted_pct)],
    ["AI calls", s.ai_calls],
    ["Failed AI calls", s.ai_failed_calls],
    ["Avg AI latency", `${s.avg_latency_ms} ms`],
    ["Input tokens", s.input_tokens.toLocaleString()],
    ["Output tokens", s.output_tokens.toLocaleString()],
    ["Estimated AI cost", `$${s.estimated_cost_usd}`],
  ];

  return (
    <>
      <h1>AI Accuracy &amp; Cost</h1>
      {error && <div className="banner warn">Could not refresh. Showing the last loaded stats.</div>}
      <div className="stats">
        {cards.map(([label, value]) => (
          <div key={label} className="card stat">
            <span className="small muted">{label}</span>
            <b>{value}</b>
          </div>
        ))}
      </div>

      <h2 style={{ marginTop: "1.5rem" }}>Tickets by status</h2>
      <div className="row">
        {Object.entries(s.tickets_by_status).map(([k, v]) => (
          <span key={k} className="badge status-Closed">{k}: {v}</span>
        ))}
      </div>
      <p className="small muted" style={{ marginTop: "1rem" }}>
        &quot;Accepted&quot; = the admin kept the AI&apos;s suggestion. Cost is an estimate based on Claude Haiku token prices.
      </p>
    </>
  );
}
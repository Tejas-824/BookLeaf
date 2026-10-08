"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { api } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import usePolling from "@/hooks/usePolling";
import StatusBadge from "@/components/StatusBadge";
import TicketThread from "@/components/TicketThread";
import { ErrorBox, Loading } from "@/components/ui";

export default function TicketPage() {
  const { id } = useParams();
  const { data: t, error, loading, refresh } = usePolling(() => api(`/api/tickets/${id}`), 6000, String(id));

  if (loading) return <Loading />;
  if (!t) return <ErrorBox message={error || "Ticket not found."} onRetry={refresh} />;

  return (
    <>
      <Link href="/author/tickets" className="small">← Back to my tickets</Link>
      <div className="spread" style={{ marginTop: ".5rem" }}>
        <h1 style={{ margin: 0 }}>#{t.id} · {t.subject}</h1>
        <StatusBadge status={t.status} />
      </div>
      <p className="small muted">
        {t.book_title || "General / Account Level"} · Opened {formatDateTime(t.created_at)} ·{" "}
        <span className="live" />Updates automatically
      </p>
      {error && <div className="banner warn">Could not refresh just now. Showing the last loaded version.</div>}
      <TicketThread ticket={t} />
    </>
  );
}
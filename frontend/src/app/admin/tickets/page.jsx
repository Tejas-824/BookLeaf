"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { getAuth } from "@/lib/auth";
import { EMPTY_FILTERS, PAGE_SIZE } from "@/lib/constants";
import { formatAge, formatDateTime } from "@/lib/format";
import usePolling from "@/hooks/usePolling";
import Filters from "@/components/Filters";
import PriorityBadge from "@/components/PriorityBadge";
import StatusBadge from "@/components/StatusBadge";
import { Empty, ErrorBox, Loading } from "@/components/ui";

export default function AdminQueuePage() {
  const router = useRouter();
  const me = getAuth();
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [page, setPage] = useState(1);

  const params = new URLSearchParams();
  Object.entries(filters).forEach(([k, v]) => { if (v) params.set(k, String(v)); });
  params.set("page", page);
  params.set("page_size", PAGE_SIZE);
  const qs = params.toString();

  const { data, error, loading, refresh } = usePolling(() => api(`/api/admin/tickets?${qs}`), 10000, qs);

  const items = data?.items || [];
  const totalPages = Math.max(1, Math.ceil((data?.total || 0) / PAGE_SIZE));

  const assignedLabel = (id) => (!id ? "Unassigned" : id === me?.user_id ? "You" : `Admin #${id}`);

  return (
    <>
      <h1><span className="live" />Ticket Queue</h1>
      <Filters value={filters} onChange={(f) => { setFilters(f); setPage(1); }} />

      {error && <ErrorBox message={error} onRetry={refresh} />}
      {loading && <Loading />}
      {data && items.length === 0 && <Empty text="No tickets match these filters." />}

      {items.length > 0 && (
        <div className="table-wrap">
          <table className="queue">
            <thead>
              <tr>
                <th>Ticket</th><th>Author</th><th>Category</th><th>Priority</th>
                <th>Status</th><th>Age</th><th>Assigned</th>
              </tr>
            </thead>
            <tbody>
              {items.map((t) => {
                const open = t.status === "Open" || t.status === "In Progress";
                return (
                  <tr key={t.id}
                      className={`${t.overdue ? "overdue" : ""} ${t.priority === "Critical" && open ? "critical" : ""}`}
                      onClick={() => router.push(`/admin/tickets/${t.id}`)}>
                    <td data-label="Ticket">
                      <div>
                        <Link href={`/admin/tickets/${t.id}`} onClick={(e) => e.stopPropagation()}>
                          <strong>#{t.id} {t.subject}</strong>
                        </Link>
                        <div className="small muted">{formatDateTime(t.created_at)}</div>
                      </div>
                    </td>
                    <td data-label="Author">{t.author_name}</td>
                    <td data-label="Category">
                      <div style={{ textAlign: "right" }}>
                        {t.category || <span className="muted">Classifying…</span>}
                        {t.ai_status === "ai_failed" && <div className="small muted">⚠ AI failed</div>}
                      </div>
                    </td>
                    <td data-label="Priority"><PriorityBadge priority={t.priority} /></td>
                    <td data-label="Status"><StatusBadge status={t.status} /></td>
                    <td data-label="Age">
                      {open ? formatAge(t.age_hours) : "—"}{" "}
                      {t.overdue && <span className="badge overdue">Overdue</span>}
                    </td>
                    <td data-label="Assigned">{assignedLabel(t.assigned_to)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {data && data.total > 0 && (
        <div className="pager">
          <button className="btn secondary sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>← Prev</button>
          <span className="small muted">Page {page} of {totalPages} · {data.total} tickets</span>
          <button className="btn secondary sm" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Next →</button>
        </div>
      )}
    </>
  );
}
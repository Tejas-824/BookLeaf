"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { getAuth } from "@/lib/auth";
import { CATEGORIES, PRIORITIES, STATUSES } from "@/lib/constants";
import { formatDate, formatDateTime, formatMoney } from "@/lib/format";
import usePolling from "@/hooks/usePolling";
import AiLabel from "@/components/AiLabel";
import DraftEditor from "@/components/DraftEditor";
import PriorityBadge from "@/components/PriorityBadge";
import StatusBadge from "@/components/StatusBadge";
import TicketThread from "@/components/TicketThread";
import { ErrorBox, Loading } from "@/components/ui";

export default function AdminTicketPage() {
  const { id } = useParams();
  const me = getAuth();
  const { data: t, error, loading, refresh, setData } = usePolling(
    () => api(`/api/admin/tickets/${id}`), 8000, String(id)
  );
  const [actionError, setActionError] = useState("");
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState("");

  // One helper: runs any admin action with try/catch and a busy flag
  async function run(action) {
    setBusy(true);
    setActionError("");
    try {
      await action();
    } catch (e) {
      setActionError(e.message);
    } finally {
      setBusy(false);
    }
  }

  const patch = (changes) =>
    run(async () => setData(await api(`/api/admin/tickets/${id}`, { method: "PATCH", body: changes })));

  const assignMe = () =>
    run(async () => setData(await api(`/api/admin/tickets/${id}/assign-me`, { method: "POST" })));

  const addNote = () =>
    run(async () => {
      if (!note.trim()) return;
      const created = await api(`/api/admin/tickets/${id}/notes`, { method: "POST", body: { body: note.trim() } });
      setData((prev) => ({ ...prev, notes: [...prev.notes, created] }));
      setNote("");
    });

  if (loading) return <Loading />;
  if (!t) return <ErrorBox message={error || "Ticket not found."} onRetry={refresh} />;

  const assignedToMe = t.assigned_to === me?.user_id;
  const assignedLabel = !t.assigned_to ? "Unassigned" : assignedToMe ? "You" : `Admin #${t.assigned_to}`;
  const b = t.book;

  return (
    <>
      <Link href="/admin/tickets" className="small">← Back to queue</Link>
      <div className="spread" style={{ margin: ".5rem 0" }}>
        <h1 style={{ margin: 0 }}>#{t.id} · {t.subject}</h1>
        <div className="row"><PriorityBadge priority={t.priority} /><StatusBadge status={t.status} /></div>
      </div>
      <p className="small muted">Opened {formatDateTime(t.created_at)} by {t.author.name}</p>

      {error && <div className="banner warn">Could not refresh just now. Showing the last loaded version.</div>}
      {actionError && <ErrorBox message={actionError} />}
      {t.ai_status === "ai_pending" && <div className="banner info">AI is classifying this ticket and writing a draft…</div>}
      {t.ai_status === "ai_failed" && (
        <div className="banner warn">AI was unavailable. Category and priority came from keyword rules. Please check them and reply manually if needed.</div>
      )}
      {t.ai_confidence === "low" && t.category_source === "ai" && (
        <div className="banner warn">The AI is not sure about this ticket. Please double-check the category and priority.</div>
      )}

      <div className="detail">
        {/* Main column */}
        <div className="stack">
          <div className="card">
            <h2>Conversation</h2>
            <TicketThread ticket={t} authorName={t.author.name} adminLabel="BookLeaf (admin)" />
          </div>
          <DraftEditor ticket={t} onUpdated={setData} />
        </div>

        {/* Side column */}
        <div className="stack">
          <div className="card">
            <h2>Manage</h2>
            <label>Status</label>
            <select value={t.status} disabled={busy} onChange={(e) => patch({ status: e.target.value })}>
              {STATUSES.map((s) => <option key={s}>{s}</option>)}
            </select>

            <label>Category</label>
            <select value={t.category || ""} disabled={busy} onChange={(e) => patch({ category: e.target.value })}>
              {!t.category && <option value="" disabled>Classifying…</option>}
              {CATEGORIES.map((c) => <option key={c}>{c}</option>)}
            </select>
            <AiLabel source={t.category_source} aiValue={t.ai_category} current={t.category} />

            <label>Priority</label>
            <select value={t.priority} disabled={busy} onChange={(e) => patch({ priority: e.target.value })}>
              {PRIORITIES.map((p) => <option key={p}>{p}</option>)}
            </select>
            <AiLabel source={t.priority_source} aiValue={t.ai_priority} current={t.priority} />

            <p style={{ marginTop: "1rem" }}>Assigned to: <strong>{assignedLabel}</strong></p>
            {!assignedToMe && (
              <button className="btn secondary sm" onClick={assignMe} disabled={busy}>Assign to me</button>
            )}
          </div>

          <div className="card">
            <h2>Author &amp; book</h2>
            <p style={{ marginTop: 0 }}>
              <strong>{t.author.name}</strong><br />
              <span className="small muted">{t.author.email} · {t.author.city || "—"}</span>
            </p>
            {b ? (
              <dl className="kv">
                <dt>Book</dt><dd>{b.title}</dd>
                <dt>ISBN</dt><dd>{b.isbn}</dd>
                <dt>Status</dt><dd>{b.status}</dd>
                <dt>Copies sold</dt><dd>{b.total_copies_sold}</dd>
                <dt>Earned</dt><dd>{formatMoney(b.total_royalty_earned)}</dd>
                <dt>Paid</dt><dd>{formatMoney(b.royalty_paid)}</dd>
                <dt>Pending</dt><dd>{formatMoney(b.royalty_pending)}</dd>
                <dt>Last payout</dt><dd>{formatDate(b.last_royalty_payout_date)}</dd>
              </dl>
            ) : (
              <p className="small muted">General / account-level ticket (no specific book).</p>
            )}
          </div>

          <div className="card">
            <h2>Internal notes</h2>
            <p className="small muted" style={{ marginTop: 0 }}>Private. Never shown to the author.</p>
            {t.notes.length === 0 && <p className="small muted">No notes yet.</p>}
            {t.notes.map((n) => (
              <div key={n.id} className="note">
                <div className="small muted">Admin #{n.admin_id} · {formatDateTime(n.created_at)}</div>
                <div style={{ whiteSpace: "pre-wrap" }}>{n.body}</div>
              </div>
            ))}
            <textarea value={note} onChange={(e) => setNote(e.target.value)} placeholder="Add an internal note…" style={{ minHeight: 80 }} />
            <button className="btn secondary sm" onClick={addNote} disabled={busy || !note.trim()} style={{ marginTop: ".5rem" }}>
              Add note
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
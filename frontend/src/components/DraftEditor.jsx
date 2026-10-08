"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { STATUSES } from "@/lib/constants";
import { ErrorBox } from "./ui";

export default function DraftEditor({ ticket, onUpdated }) {
  const [text, setText] = useState("");
  const [dirty, setDirty] = useState(false); // true once admin edits (or after sending)
  const [afterStatus, setAfterStatus] = useState("In Progress");
  const [sending, setSending] = useState(false);
  const [regen, setRegen] = useState(false);
  const [error, setError] = useState("");

  // Fill the box with the AI draft, but never overwrite what the admin is typing
  useEffect(() => {
    if (!dirty) setText(ticket.ai_draft || "");
  }, [ticket.ai_draft, dirty]);

  async function send() {
    if (text.trim().length < 5) return setError("Reply must be at least 5 characters.");
    setSending(true);
    setError("");
    try {
      const updated = await api(`/api/admin/tickets/${ticket.id}/reply`, {
        method: "POST",
        body: { body: text.trim(), set_status: afterStatus },
      });
      onUpdated(updated);
      setText("");
      setDirty(true); // keep box empty after sending
    } catch (e) {
      setError(e.message); // text is kept so nothing is lost
    } finally {
      setSending(false);
    }
  }

  async function regenerate() {
    if (dirty && text.trim() && !window.confirm("Replace your text with a new AI draft?")) return;
    setRegen(true);
    setError("");
    try {
      const updated = await api(`/api/admin/tickets/${ticket.id}/draft/regenerate`, { method: "POST" });
      onUpdated(updated);
      setText(updated.ai_draft || "");
      setDirty(false);
    } catch (e) {
      setError(e.message);
    } finally {
      setRegen(false);
    }
  }

  const pending = ticket.ai_status === "ai_pending" && !ticket.ai_draft;

  return (
    <div className="card">
      <div className="spread">
        <h2>Reply to author</h2>
        {ticket.ai_status === "ai_done" && <span className="ai-label ai">✨ AI draft: review before sending</span>}
      </div>

      {pending && <div className="banner info">AI is writing a draft. It will appear here in a few seconds.</div>}
      {ticket.ai_status === "ai_failed" && !ticket.ai_draft && (
        <div className="banner warn">AI draft is not available right now. You can write the reply manually or try again.</div>
      )}
      {error && <ErrorBox message={error} />}

      <textarea
        value={text}
        onChange={(e) => { setText(e.target.value); setDirty(true); }}
        placeholder="Write your reply to the author…"
        style={{ minHeight: 220 }}
      />

      <div className="row" style={{ marginTop: ".75rem", justifyContent: "space-between" }}>
        <div className="row">
          <label style={{ margin: 0 }} htmlFor="after">After sending, set status:</label>
          <select id="after" value={afterStatus} onChange={(e) => setAfterStatus(e.target.value)} style={{ width: "auto" }}>
            {STATUSES.map((s) => <option key={s}>{s}</option>)}
          </select>
        </div>
        <div className="row">
          <button className="btn secondary" onClick={regenerate} disabled={regen || sending}>
            {regen ? "Generating…" : "Regenerate AI draft"}
          </button>
          <button className="btn" onClick={send} disabled={sending || regen}>
            {sending ? "Sending…" : "Send reply"}
          </button>
        </div>
      </div>
    </div>
  );
}
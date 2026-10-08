"use client";
import { useRef, useState } from "react";
import { ErrorBox } from "./ui";

const makeKey = () =>
  typeof crypto !== "undefined" && crypto.randomUUID
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(36).slice(2)}`;

export default function TicketForm({ books, onSubmit }) {
  const [bookId, setBookId] = useState("");
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const idemKey = useRef(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (submitting) return;

    const s = subject.trim();
    const d = description.trim();
    if (s.length < 3) return setError("Subject must be at least 3 characters.");
    if (d.length < 10) return setError("Please describe the issue in at least 10 characters.");

    setSubmitting(true);
    setError("");
    try {
      idemKey.current ||= makeKey(); // same key on retry = no duplicate ticket
      await onSubmit({
        body: { book_id: bookId || null, subject: s, description: d, attachment_name: file?.name || null },
        idemKey: idemKey.current,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      {error && <ErrorBox message={error} />}

      <label htmlFor="book">Which book is this about?</label>
      <select id="book" value={bookId} onChange={(e) => setBookId(e.target.value)}>
        <option value="">General / Account Level</option>
        {books.map((b) => (
          <option key={b.book_id} value={b.book_id}>{b.title}</option>
        ))}
      </select>

      <label htmlFor="subject">Subject</label>
      <input id="subject" value={subject} maxLength={200} onChange={(e) => setSubject(e.target.value)}
             placeholder="e.g. Royalty not received" />

      <label htmlFor="desc">Describe your issue</label>
      <textarea id="desc" value={description} maxLength={5000} onChange={(e) => setDescription(e.target.value)}
                placeholder="Please share as many details as you can." />
      <div className="small muted" style={{ textAlign: "right" }}>{description.length}/5000</div>

      <label htmlFor="file">Attachment (optional)</label>
      <input id="file" type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <div className="small muted">Preview only for now: the file name is saved, the file is not uploaded.</div>

      <button className="btn" type="submit" disabled={submitting} style={{ marginTop: "1rem" }}>
        {submitting ? "Submitting…" : "Submit query"}
      </button>
    </form>
  );
}
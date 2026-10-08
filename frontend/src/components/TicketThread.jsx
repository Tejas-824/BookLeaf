import { formatDateTime } from "@/lib/format";

export default function TicketThread({ ticket, authorName = "You", adminLabel = "BookLeaf Support" }) {
  return (
    <div className="thread">
      <div className="bubble author">
        <div className="bubble-meta">{authorName} · {formatDateTime(ticket.created_at)}</div>
        <div className="bubble-body">{ticket.description}</div>
      </div>

      {ticket.messages.map((m) => (
        <div key={m.id} className={`bubble ${m.sender_role === "admin" ? "admin" : "author"}`}>
          <div className="bubble-meta">
            {m.sender_role === "admin" ? adminLabel : authorName} · {formatDateTime(m.created_at)}
          </div>
          <div className="bubble-body">{m.body}</div>
        </div>
      ))}

      {ticket.messages.length === 0 && (
        <p className="small muted">No reply yet. Our team will respond soon.</p>
      )}
    </div>
  );
}
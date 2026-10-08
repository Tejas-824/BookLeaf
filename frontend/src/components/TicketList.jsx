import Link from "next/link";
import { formatDateTime } from "@/lib/format";
import StatusBadge from "./StatusBadge";

export default function TicketList({ tickets }) {
  return (
    <div className="stack">
      {tickets.map((t) => {
        const replies = t.messages.filter((m) => m.sender_role === "admin").length;
        return (
          <Link key={t.id} href={`/author/tickets/${t.id}`} className="card ticket-card">
            <div className="spread">
              <strong>#{t.id} · {t.subject}</strong>
              <StatusBadge status={t.status} />
            </div>
            <div className="small muted">
              {t.book_title || "General / Account Level"} · {formatDateTime(t.created_at)}
            </div>
            {replies > 0 && (
              <div className="small reply-pill">
                {replies} repl{replies === 1 ? "y" : "ies"} from BookLeaf
              </div>
            )}
          </Link>
        );
      })}
    </div>
  );
}
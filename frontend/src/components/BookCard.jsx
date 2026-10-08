import { MIN_PAYOUT } from "@/lib/constants";
import { formatDate, formatMoney } from "@/lib/format";

export default function BookCard({ book: b }) {
  const published = !!b.publication_date;
  const belowMin = b.royalty_pending > 0 && b.royalty_pending < MIN_PAYOUT;

  return (
    <div className="card">
      <div className="spread">
        <h2 style={{ margin: 0 }}>{b.title}</h2>
        <span className={`badge ${published ? "status-Resolved" : "status-In-Progress"}`}>{b.status}</span>
      </div>

      <dl className="kv" style={{ marginTop: ".75rem" }}>
        <dt>ISBN</dt><dd>{b.isbn}</dd>
        <dt>Genre</dt><dd>{b.genre || "—"}</dd>
        <dt>Published</dt><dd>{formatDate(b.publication_date)}</dd>
        <dt>MRP</dt><dd>{formatMoney(b.mrp)}</dd>
        <dt>Copies sold</dt><dd>{b.total_copies_sold}</dd>
      </dl>

      {published ? (
        <>
          <div className="money">
            <div><b>{formatMoney(b.total_royalty_earned)}</b><span>Earned</span></div>
            <div><b>{formatMoney(b.royalty_paid)}</b><span>Paid</span></div>
            <div className="pending"><b>{formatMoney(b.royalty_pending)}</b><span>Pending</span></div>
          </div>
          {belowMin && (
            <p className="small muted">
              Pending is below the {formatMoney(MIN_PAYOUT)} minimum, so it rolls over to the next quarter.
            </p>
          )}
          {b.total_royalty_earned > 0 && b.royalty_paid === 0 && (
            <p className="small muted">No payout yet. Royalties are paid quarterly, within 45 days of quarter end.</p>
          )}
        </>
      ) : (
        <p className="small muted" style={{ marginTop: ".75rem" }}>
          Royalty details will appear after your book is published.
        </p>
      )}
    </div>
  );
}
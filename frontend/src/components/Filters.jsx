"use client";
import { CATEGORIES, EMPTY_FILTERS, PRIORITIES, STATUSES } from "@/lib/constants";

export default function Filters({ value, onChange }) {
  const set = (k, v) => onChange({ ...value, [k]: v });
  const opts = (list) => list.map((x) => <option key={x} value={x}>{x}</option>);

  return (
    <div className="card filters">
      <div>
        <label>Status</label>
        <select value={value.status} onChange={(e) => set("status", e.target.value)}>
          <option value="">All</option>{opts(STATUSES)}
        </select>
      </div>
      <div>
        <label>Category</label>
        <select value={value.category} onChange={(e) => set("category", e.target.value)}>
          <option value="">All</option>{opts(CATEGORIES)}
        </select>
      </div>
      <div>
        <label>Priority</label>
        <select value={value.priority} onChange={(e) => set("priority", e.target.value)}>
          <option value="">All</option>{opts(PRIORITIES)}
        </select>
      </div>
      <div>
        <label>From</label>
        <input type="date" value={value.date_from} onChange={(e) => set("date_from", e.target.value)} />
      </div>
      <div>
        <label>To</label>
        <input type="date" value={value.date_to} onChange={(e) => set("date_to", e.target.value)} />
      </div>
      <div className="row">
        <label style={{ display: "flex", alignItems: "center", gap: ".4rem", margin: 0 }}>
          <input type="checkbox" style={{ width: "auto" }} checked={value.mine}
                 onChange={(e) => set("mine", e.target.checked)} />
          Assigned to me
        </label>
        <button className="btn secondary sm" onClick={() => onChange(EMPTY_FILTERS)}>Clear</button>
      </div>
    </div>
  );
}
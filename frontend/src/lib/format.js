export function formatMoney(v) {
  return v == null ? "—" : "₹" + Number(v).toLocaleString("en-IN");
}

// Date-only values like "2023-06-20" (no timezone shift)
export function formatDate(v) {
  if (!v) return "—";
  return new Date(v).toLocaleDateString("en-IN", { dateStyle: "medium", timeZone: "UTC" });
}

export function formatDateTime(v) {
  if (!v) return "—";
  return new Date(v).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
}

export function formatAge(hours) {
  if (hours == null) return "—";
  if (hours < 1) return "<1h";
  if (hours < 48) return `${Math.floor(hours)}h`;
  return `${Math.floor(hours / 24)}d`;
}
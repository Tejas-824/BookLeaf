const KEY = "bookleaf_auth";

export function saveAuth(res) {
  localStorage.setItem(
    KEY,
    JSON.stringify({ token: res.access_token, role: res.role, name: res.name, user_id: res.user_id })
  );
}

export function getAuth() {
  if (typeof window === "undefined") return null;
  try {
    return JSON.parse(localStorage.getItem(KEY));
  } catch {
    return null; // corrupted value: treat as logged out
  }
}

export function clearAuth() {
  if (typeof window !== "undefined") localStorage.removeItem(KEY);
}

export function homeFor(role) {
  return role === "admin" ? "/admin/tickets" : "/author/books";
}
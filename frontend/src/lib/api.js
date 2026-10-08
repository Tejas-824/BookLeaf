import { clearAuth, getAuth } from "./auth";

const BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(message, status, code) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export async function api(path, { method = "GET", body, headers = {} } = {}) {
  const auth = getAuth();
  let res;
  try {
    res = await fetch(`${BASE}${path}`, {
      method,
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
        ...(auth?.token ? { Authorization: `Bearer ${auth.token}` } : {}),
        ...headers,
      },
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch {
    // server down, no internet, CORS problem
    throw new ApiError("Cannot reach the server. Please check your connection and try again.", 0, "network_error");
  }

  let data = null;
  try {
    data = await res.json();
  } catch {
    /* empty or non-JSON body */
  }

  if (!res.ok) {
    // Session expired: clear it and go to login (but not for a wrong-password login)
    if (res.status === 401 && auth && !path.startsWith("/api/auth/login")) {
      clearAuth();
      if (typeof window !== "undefined") window.location.href = "/login";
    }
    const err = data?.error;
    let message = err?.message || "Something went wrong. Please try again.";
    if (err?.details?.length) {
      message += " (" + err.details.map((d) => `${d.field}: ${d.message}`).join("; ") + ")";
    }
    throw new ApiError(message, res.status, err?.code);
  }
  return data;
}
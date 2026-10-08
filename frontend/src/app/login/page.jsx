"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { getAuth, homeFor, saveAuth } from "@/lib/auth";
import { ErrorBox } from "@/components/ui";

// Demo logins for reviewers. Remove in production.
const DEMO = [
  { label: "Author (Priya)", email: "priya.sharma@email.com", password: "Author@123" },
  { label: "Admin", email: "admin@bookleaf.com", password: "Admin@123" },
];

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const auth = getAuth();
    if (auth) router.replace(homeFor(auth.role)); // already logged in
  }, [router]);

  async function handleSubmit(e) {
    e.preventDefault();
    if (loading) return;
    if (!email.trim() || !password) return setError("Please enter your email and password.");
    setLoading(true);
    setError("");
    try {
      const res = await api("/api/auth/login", { method: "POST", body: { email: email.trim(), password } });
      saveAuth(res);
      router.replace(homeFor(res.role));
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  }

  return (
    <div className="login-wrap">
      <div className="card login-card">
        <h1>📖 BookLeaf Author Support</h1>
        <p className="muted small">Log in to manage your books and support tickets.</p>
        {error && <ErrorBox message={error} />}

        <form onSubmit={handleSubmit}>
          <label htmlFor="email">Email</label>
          <input id="email" type="email" autoComplete="username" value={email} onChange={(e) => setEmail(e.target.value)} />
          <label htmlFor="pw">Password</label>
          <input id="pw" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <button className="btn" type="submit" disabled={loading} style={{ width: "100%", marginTop: "1rem" }}>
            {loading ? "Logging in…" : "Log in"}
          </button>
        </form>

        <div className="banner info" style={{ marginTop: "1rem", marginBottom: 0 }}>
          <div className="small"><strong>Demo logins</strong> (click to fill)</div>
          <div className="row" style={{ marginTop: ".4rem" }}>
            {DEMO.map((d) => (
              <button key={d.label} type="button" className="btn secondary sm"
                      onClick={() => { setEmail(d.email); setPassword(d.password); }}>
                {d.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
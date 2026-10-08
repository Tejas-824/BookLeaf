"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar({ links, name, onLogout }) {
  const pathname = usePathname();
  // highlight the most specific matching link only
  const active = links
    .filter((l) => pathname === l.href || pathname.startsWith(l.href + "/"))
    .sort((a, b) => b.href.length - a.href.length)[0]?.href;

  return (
    <header className="nav">
      <div className="nav-inner">
        <span className="brand">📖 BookLeaf</span>
        <nav className="nav-links">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className={l.href === active ? "active" : ""}>
              {l.label}
            </Link>
          ))}
        </nav>
        <div className="nav-user">
          <span className="uname muted">{name}</span>
          <button className="btn secondary sm" onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
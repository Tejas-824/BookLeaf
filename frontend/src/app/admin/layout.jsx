"use client";
import Navbar from "@/components/Navbar";
import { Loading } from "@/components/ui";
import useAuth from "@/hooks/useAuth";

const LINKS = [
  { href: "/admin/tickets", label: "Ticket Queue" },
  { href: "/admin/stats", label: "AI Stats" },
];

export default function AdminLayout({ children }) {
  const { user, ready, logout } = useAuth("admin");
  if (!ready) return <Loading />;
  return (
    <>
      <Navbar links={LINKS} name={`${user.name} (Admin)`} onLogout={logout} />
      <main className="container">{children}</main>
    </>
  );
}
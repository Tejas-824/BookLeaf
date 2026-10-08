"use client";
import Navbar from "@/components/Navbar";
import { Loading } from "@/components/ui";
import useAuth from "@/hooks/useAuth";

const LINKS = [
  { href: "/author/books", label: "My Books" },
  { href: "/author/tickets/new", label: "Submit Query" },
  { href: "/author/tickets", label: "My Tickets" },
];

export default function AuthorLayout({ children }) {
  const { user, ready, logout } = useAuth("author");
  if (!ready) return <Loading />;
  return (
    <>
      <Navbar links={LINKS} name={user.name} onLogout={logout} />
      <main className="container">{children}</main>
    </>
  );
}
"use client";
import Link from "next/link";
import { api } from "@/lib/api";
import usePolling from "@/hooks/usePolling";
import TicketList from "@/components/TicketList";
import { Empty, ErrorBox, Loading } from "@/components/ui";

export default function MyTicketsPage() {
  const { data: tickets, error, loading, refresh } = usePolling(() => api("/api/tickets"), 8000, "my-tickets");

  return (
    <>
      <div className="spread">
        <h1><span className="live" />My Tickets</h1>
        <Link href="/author/tickets/new" className="btn">+ New query</Link>
      </div>
      {error && <ErrorBox message={error} onRetry={refresh} />}
      {loading && <Loading />}
      {tickets && tickets.length === 0 && <Empty text="You haven't raised any tickets yet." />}
      {tickets && tickets.length > 0 && <TicketList tickets={tickets} />}
    </>
  );
}
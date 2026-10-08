"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import TicketForm from "@/components/TicketForm";
import { ErrorBox, Loading } from "@/components/ui";

export default function NewTicketPage() {
  const router = useRouter();
  const [books, setBooks] = useState(null);
  const [error, setError] = useState("");

  async function loadBooks() {
    setError("");
    try {
      setBooks(await api("/api/books"));
    } catch (e) {
      setError(e.message);
    }
  }
  useEffect(() => { loadBooks(); }, []);

  async function submit({ body, idemKey }) {
    const ticket = await api("/api/tickets", {
      method: "POST",
      body,
      headers: { "Idempotency-Key": idemKey },
    });
    router.push(`/author/tickets/${ticket.id}`); // errors are handled inside TicketForm
  }

  return (
    <>
      <h1>Submit a Support Query</h1>
      {error && <ErrorBox message={error} onRetry={loadBooks} />}
      {!books && !error && <Loading />}
      {books && <TicketForm books={books} onSubmit={submit} />}
    </>
  );
}
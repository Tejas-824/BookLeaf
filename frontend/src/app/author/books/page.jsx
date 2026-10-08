"use client";
import { api } from "@/lib/api";
import usePolling from "@/hooks/usePolling";
import BookCard from "@/components/BookCard";
import { Empty, ErrorBox, Loading } from "@/components/ui";

export default function BooksPage() {
  const { data: books, error, loading, refresh } = usePolling(() => api("/api/books"), 60000, "books");

  return (
    <>
      <h1>My Books</h1>
      {error && <ErrorBox message={error} onRetry={refresh} />}
      {loading && <Loading />}
      {books && books.length === 0 && <Empty text="You don't have any books yet." />}
      <div className="grid">
        {books?.map((b) => <BookCard key={b.book_id} book={b} />)}
      </div>
    </>
  );
}
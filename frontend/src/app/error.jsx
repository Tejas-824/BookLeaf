"use client";

export default function Error({ error, reset }) {
  return (
    <div className="container">
      <div className="banner error">
        <strong>Something went wrong.</strong>
        <p>{error?.message || "Unexpected error."}</p>
        <button className="btn secondary sm" onClick={reset}>Try again</button>
      </div>
    </div>
  );
}
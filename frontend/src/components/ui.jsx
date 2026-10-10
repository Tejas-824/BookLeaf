// Shown while data is loading
export function Loading({ text = "Loading…" }) {
  return <div className="center muted">{text}</div>;
}

// Red box for errors, with an optional "Try again" button
export function ErrorBox({ message, onRetry }) {
  return (
    <div className="banner error" role="alert">
      <div>{message}</div>
      {onRetry && (
        <button className="btn secondary sm" style={{ marginTop: ".5rem" }} onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  );
}

// Shown when a list has no items
export function Empty({ text }) {
  return <div className="card center muted">{text}</div>;
}
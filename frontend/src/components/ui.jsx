export function Loading({ text = "Loading…" }) {
  return <div className="center muted">{text}</div>;
}

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

export function Empty({ text }) {
  return <div className="card center muted">{text}</div>;
}
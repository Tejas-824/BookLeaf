export default function AiLabel({ source, aiValue, current }) {
  if (source === "pending") return <span className="ai-label pending">Classifying…</span>;
  if (source === "ai") return <span className="ai-label ai">✨ AI suggested</span>;
  if (source === "rule") return <span className="ai-label rule">Keyword rule (AI unavailable)</span>;
  if (source === "admin") {
    const changed = aiValue && aiValue !== current;
    return (
      <span className="ai-label admin">
        Set by admin{changed ? ` (AI suggested: ${aiValue})` : ""}
      </span>
    );
  }
  return null;
}
export default function PriorityBadge({ priority }) {
  return <span className={`badge pri-${priority}`}>{priority}</span>;
}
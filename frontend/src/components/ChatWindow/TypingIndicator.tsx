import type { ProcessingStatus } from "../../types/chat";

interface TypingIndicatorProps {
  statuses: ProcessingStatus[];
}

export default function TypingIndicator({ statuses }: TypingIndicatorProps) {
  if (statuses.length === 0) {
    // No statuses yet — show classic dots
    return (
      <div className="chat__bubble chat__bubble--assistant">
        <div className="chat__bubble-content chat__typing">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    );
  }

  return (
    <div className="chat__bubble chat__bubble--assistant">
      <div className="chat__bubble-content chat__status-list">
        {statuses.map((s, i) => (
          <div key={i} className={`chat__status-item ${s.done ? "chat__status-item--done" : "chat__status-item--active"}`}>
            <span className="chat__status-icon">{s.done ? "✓" : ""}</span>
            <span className="chat__status-label">{s.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

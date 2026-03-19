interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  isError?: boolean;
  onRetry?: () => void;
}

export default function MessageBubble({ role, content, isError, onRetry }: MessageBubbleProps) {
  if (isError) {
    return (
      <div className="chat__bubble chat__bubble--assistant">
        <div className="chat__bubble-content chat__bubble-error">
          <span className="chat__error-icon">⚠</span>
          <span>{content}</span>
          <button className="chat__retry-btn" onClick={onRetry}>⟳ Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className={`chat__bubble chat__bubble--${role}`}>
      <div className="chat__bubble-content">{content}</div>
    </div>
  );
}

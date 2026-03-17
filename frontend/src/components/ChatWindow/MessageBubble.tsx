interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
}

export default function MessageBubble({ role, content }: MessageBubbleProps) {
  return (
    <div className={`chat__bubble chat__bubble--${role}`}>
      <div className="chat__bubble-content">{content}</div>
    </div>
  );
}

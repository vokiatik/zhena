import { useRef, useEffect } from "react";
import type { Message, ProcessingStatus } from "../../types/chat";
import EmptyState from "./EmptyState";
import MessageBubble from "./MessageBubble";
import TypingIndicator from "./TypingIndicator";

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  processingStatuses: ProcessingStatus[];
  onRetry: () => void;
}

export default function MessageList({ messages, isLoading, processingStatuses, onRetry }: MessageListProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, processingStatuses]);

  return (
    <div className="chat__messages">
      {messages.length === 0 && !isLoading && <EmptyState />}

      {messages.map((msg) => (
        <MessageBubble key={msg.id} role={msg.role} content={msg.content} isError={msg.isError} onRetry={onRetry} />
      ))}

      {isLoading && <TypingIndicator statuses={processingStatuses} />}

      <div ref={endRef} />
    </div>
  );
}

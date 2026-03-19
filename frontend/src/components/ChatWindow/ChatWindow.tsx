import type { Message, ProcessingStatus } from "../../types/chat";
import MessageList from "./MessageList";
import ChatInput from "./ChatInput";
import "./ChatWindow.css";

interface ChatWindowProps {
  messages: Message[];
  onSend: (text: string) => void;
  isLoading: boolean;
  processingStatuses: ProcessingStatus[];
  onRetry: () => void;
}

export default function ChatWindow({ messages, onSend, isLoading, processingStatuses, onRetry }: ChatWindowProps) {
  return (
    <main className="chat">
      <MessageList messages={messages} isLoading={isLoading} processingStatuses={processingStatuses} onRetry={onRetry} />
      <ChatInput onSend={onSend} disabled={isLoading} />
    </main>
  );
}

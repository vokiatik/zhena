import { useState, useRef, useEffect, useCallback } from "react";
import { useSpeechToText } from "../../hooks/useSpeechToText";

interface ChatInputProps {
  onSend: (text: string) => void;
  disabled: boolean;
}

export default function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleTranscript = useCallback(
    (transcript: string) => {
      setInput((prev) => (prev ? prev + " " + transcript : transcript));
    },
    []
  );

  const { isListening, toggle: toggleMic } = useSpeechToText(handleTranscript);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = "auto";
      ta.style.height = Math.min(ta.scrollHeight, 200) + "px";
    }
  }, [input]);

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat__input-area">
      <div className="chat__input-row">
        <button
          className={`chat__mic-btn ${isListening ? "chat__mic-btn--active" : ""}`}
          onClick={toggleMic}
          aria-label="Speech to text"
          title="Speech to text"
        >
          🎤
        </button>

        <textarea
          ref={textareaRef}
          className="chat__input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message…"
          rows={1}
          disabled={disabled}
        />

        <button
          className="chat__send-btn"
          onClick={handleSend}
          disabled={!input.trim() || disabled}
          aria-label="Send message"
        >
          ➤
        </button>
      </div>
    </div>
  );
}

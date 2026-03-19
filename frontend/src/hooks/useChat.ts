import { useState, useCallback, useEffect, useRef } from "react";
import { useApi } from "../api";
import { useChatSocket } from "./useChatSocket";
import type { WsMessage } from "../ws";
import type { Chat, Message, ProcessingStatus } from "../types/chat";

export function useChat() {
  const { get } = useApi();
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [processingStatuses, setProcessingStatuses] = useState<ProcessingStatus[]>([]);
  const pendingMsgRef = useRef<string | null>(null);
  const lastSentRef = useRef<{ chatId: string; content: string } | null>(null);
  const sendRef = useRef<(data: Record<string, unknown>) => void>(() => {});

  const activeChat = chats.find((c) => c.id === activeChatId) ?? null;

  // ── WebSocket handler ───────────────────────────────────────────
  const handleWsMessage = useCallback((msg: WsMessage) => {
    if (msg.type === "chat_created") {
      const newChat: Chat = {
        id: msg.chatId,
        title: msg.title,
        messages: [],
        createdAt: Date.now(),
      };
      setChats((prev) => [newChat, ...prev]);
      setActiveChatId(msg.chatId);

      const pending = pendingMsgRef.current;
      if (pending) {
        pendingMsgRef.current = null;
        lastSentRef.current = { chatId: msg.chatId, content: pending };
        sendRef.current({ type: "message", chatId: msg.chatId, content: pending });
        setIsLoading(true);
      }
    } else if (msg.type === "message") {
      const m: Message = msg.message;
      setChats((prev) =>
        prev.map((c) =>
          c.id === msg.chatId ? { ...c, messages: [...c.messages, m] } : c
        )
      );
      if (m.role === "assistant") {
        setIsLoading(false);
        setProcessingStatuses([]);
      }
    } else if (msg.type === "status") {
      if (msg.status === "complete") {
        // Mark the last status as done
        setProcessingStatuses((prev) =>
          prev.map((s) => ({ ...s, done: true }))
        );
      } else {
        setProcessingStatuses((prev) => {
          // Mark all previous statuses as done, add the new one as active
          const updated = prev.map((s) => ({ ...s, done: true }));
          return [...updated, { status: msg.status, label: msg.label, done: false }];
        });
      }
    } else if (msg.type === "chat_deleted") {
      setChats((prev) => prev.filter((c) => c.id !== msg.chatId));
      setActiveChatId((prev) => (prev === msg.chatId ? null : prev));
    } else if (msg.type === "error") {
      const errorMsg: Message = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: msg.error,
        timestamp: Date.now(),
        isError: true,
      };
      setChats((prev) =>
        prev.map((c) =>
          c.id === msg.chatId ? { ...c, messages: [...c.messages, errorMsg] } : c
        )
      );
      setIsLoading(false);
      setProcessingStatuses([]);
    }
  }, []);

  const { send } = useChatSocket(handleWsMessage);
  sendRef.current = send;

  // ── Load existing chats on mount ────────────────────────────────
  useEffect(() => {
    (async () => {
      try {
        const res = await get<{ id: string; title: string; createdAt: string }[]>("/chats");
        setChats(
          res.data.map((c) => ({
            id: c.id,
            title: c.title,
            messages: [],
            createdAt: new Date(c.createdAt).getTime(),
          }))
        );
      } catch {
        // backend may not be up yet
      }
    })();
  }, [get]);

  // ── Load messages when switching chats ──────────────────────────
  useEffect(() => {
    if (!activeChatId) return;
    const chat = chats.find((c) => c.id === activeChatId);
    if (chat && chat.messages.length > 0) return;

    (async () => {
      try {
        const res = await get<Message[]>(`/chats/${activeChatId}/messages`);
        setChats((prev) =>
          prev.map((c) =>
            c.id === activeChatId ? { ...c, messages: res.data } : c
          )
        );
      } catch {
        // ignore
      }
    })();
  }, [activeChatId, get]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Actions ─────────────────────────────────────────────────────
  const createNewChat = useCallback(() => {
    send({ type: "new_chat", title: "New Chat" });
  }, [send]);

  const selectChat = useCallback((id: string) => {
    setActiveChatId(id);
  }, []);

  const deleteChat = useCallback(
    (id: string) => {
      send({ type: "delete_chat", chatId: id });
    },
    [send]
  );

  const sendMessage = useCallback(
    (text: string) => {
      if (!activeChatId) {
        pendingMsgRef.current = text;
        send({ type: "new_chat", title: text.slice(0, 40) });
        return;
      }
      lastSentRef.current = { chatId: activeChatId, content: text };
      send({ type: "message", chatId: activeChatId, content: text });
      setIsLoading(true);
    },
    [activeChatId, send]
  );

  const retryLastMessage = useCallback(() => {
    const last = lastSentRef.current;
    if (!last) return;
    // Remove trailing error message(s) from the chat
    setChats((prev) =>
      prev.map((c) =>
        c.id === last.chatId
          ? { ...c, messages: c.messages.filter((m) => !m.isError) }
          : c
      )
    );
    send({ type: "message", chatId: last.chatId, content: last.content });
    setIsLoading(true);
  }, [send]);

  return {
    chats,
    activeChat,
    activeChatId,
    isLoading,
    processingStatuses,
    createNewChat,
    selectChat,
    deleteChat,
    sendMessage,
    retryLastMessage,
  };
}

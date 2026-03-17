import { useEffect, useRef, useCallback, useState } from "react";
import { createChatSocket } from "../ws";
import type { WsMessage } from "../ws";

export function useChatSocket(onMessage: (msg: WsMessage) => void) {
  const onMessageRef = useRef(onMessage);
  const socketRef = useRef<ReturnType<typeof createChatSocket> | null>(null);
  const [connected, setConnected] = useState(false);

  onMessageRef.current = onMessage;

  useEffect(() => {
    const socket = createChatSocket({
      onMessage: (msg) => onMessageRef.current(msg),
      onConnected: () => setConnected(true),
      onDisconnected: () => setConnected(false),
    });
    socketRef.current = socket;

    return () => socket.close();
  }, []);

  const send = useCallback((data: Record<string, unknown>) => {
    socketRef.current?.send(data);
  }, []);

  return { send, connected };
}

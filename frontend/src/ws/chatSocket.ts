import type { WsMessage } from "./types";

const WS_BASE = import.meta.env.VITE_WS_BASE_URL ?? "ws://localhost:8000";

export interface ChatSocketOptions {
  onMessage: (msg: WsMessage) => void;
  onConnected?: () => void;
  onDisconnected?: () => void;
}

export function createChatSocket({ onMessage, onConnected, onDisconnected }: ChatSocketOptions) {
  let ws: WebSocket;
  let reconnectTimer: ReturnType<typeof setTimeout>;
  let alive = true;

  function connect() {
    const token = localStorage.getItem("token");
    if (!token) {
      onDisconnected?.();
      // Retry after delay in case user logs in
      if (alive) reconnectTimer = setTimeout(connect, 2000);
      return;
    }

    ws = new WebSocket(`${WS_BASE}/ws/chat?token=${encodeURIComponent(token)}`);

    ws.onopen = () => onConnected?.();

    ws.onmessage = (event) => {
      const data: WsMessage = JSON.parse(event.data);
      onMessage(data);
    };

    ws.onclose = () => {
      onDisconnected?.();
      if (alive) {
        reconnectTimer = setTimeout(connect, 2000);
      }
    };

    ws.onerror = () => ws.close();
  }

  connect();

  return {
    send(data: Record<string, unknown>) {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(data));
      }
    },
    close() {
      alive = false;
      clearTimeout(reconnectTimer);
      ws?.close();
    },
  };
}

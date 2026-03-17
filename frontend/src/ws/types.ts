export type WsMessage =
  | { type: "chat_created"; chatId: string; title: string }
  | {
      type: "message";
      chatId: string;
      message: {
        id: string;
        role: "user" | "assistant";
        content: string;
        timestamp: number;
      };
    }
  | { type: "chat_deleted"; chatId: string }
  | {
      type: "status";
      chatId: string;
      messageId: string;
      status: string;
      label: string;
    };

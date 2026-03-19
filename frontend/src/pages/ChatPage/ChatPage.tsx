import { useUser } from "../../contexts";
import { useChat } from "../../hooks/useChat";
import Sidebar from "../../components/Sidebar";
import ChatWindow from "../../components/ChatWindow";
import "./ChatPage.css";

export default function ChatPage() {
  const { user, logout } = useUser();
  const {
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
  } = useChat();

  return (
    <div className="app">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={selectChat}
        onNewChat={createNewChat}
        onDeleteChat={deleteChat}
        userEmail={user?.email ?? ""}
        onLogout={logout}
      />
      <ChatWindow
        messages={activeChat?.messages ?? []}
        onSend={sendMessage}
        isLoading={isLoading}
        processingStatuses={processingStatuses}
        onRetry={retryLastMessage}
      />
    </div>
  );
}
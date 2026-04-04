import type { Chat } from "../../types/chat";
import SidebarItem from "./SidebarItem";
import "./Sidebar.css";

interface SidebarProps {
  chats: Chat[];
  activeChatId: string | null;
  onSelectChat: (id: string) => void;
  onNewChat: () => void;
  onDeleteChat: (id: string) => void;
  userEmail: string;
  onLogout: () => void;
}

export default function Sidebar({
  chats,
  activeChatId,
  onSelectChat,
  onNewChat,
  onDeleteChat,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <button className="sidebar__new-chat" onClick={onNewChat}>
        + New Chat
      </button>

      <nav className="sidebar__list">
        {chats.map((chat) => (
          <SidebarItem
            key={chat.id}
            title={chat.title}
            isActive={chat.id === activeChatId}
            onSelect={() => onSelectChat(chat.id)}
            onDelete={() => onDeleteChat(chat.id)}
          />
        ))}
      </nav>

    </aside>
  );
}

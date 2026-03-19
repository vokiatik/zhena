import { BrowserRouter, Routes, Route, Navigate, useParams } from "react-router-dom";
import { useUser } from "./contexts";
import { LoginPage, RegisterPage, ForgotPasswordPage, ResetPasswordPage, ConfirmEmailPage } from "./components/Auth";
import { PictureScreening } from "./components/PictureScreening";
import { useChat } from "./hooks/useChat";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import "./App.css";
import { MenuSidebar } from "./components/Menu";

function ChatApp() {
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
      <MenuSidebar />
    </div>
  );
}

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useUser();
  if (isLoading) return null;
  return user ? <>{children}</> : <Navigate to="/login" replace />;
}

function GuestRoute({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useUser();
  if (isLoading) return null;
  return !user ? <>{children}</> : <Navigate to="/" replace />;
}

function ScreeningPage() {
  const { tableName } = useParams<{ tableName: string }>();
  if (!tableName) return <Navigate to="/" replace />;
  return <PictureScreening tableName={tableName} />;
}

function App() {
  // Layout wraps all main pages for navigation
  // Auth pages remain unwrapped
    return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
        <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />
        <Route path="/forgot-password" element={<GuestRoute><ForgotPasswordPage /></GuestRoute>} />
        <Route path="/reset-password" element={<GuestRoute><ResetPasswordPage /></GuestRoute>} />
        <Route path="/confirm-email" element={<ConfirmEmailPage />} />
        <Route
          path="/screening/:tableName"
          element={<PrivateRoute><ScreeningPage /></PrivateRoute>}
        />
        <Route path="/" element={<PrivateRoute><ChatApp /></PrivateRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;

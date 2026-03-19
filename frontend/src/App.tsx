import { BrowserRouter, Routes, Route, Navigate} from "react-router-dom";
import { useUser } from "./contexts";
import { LoginPage, RegisterPage, ForgotPasswordPage, ResetPasswordPage, ConfirmEmailPage } from "./components/Auth";
import { FileUploadPage } from "./pages/UploadPage";
import { ChatPage } from "./pages/ChatPage";
import ScreeningPage from "./pages/PictureScreening/PictureScreening";
import { MainLayout } from "./pages/Layout";

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

function App() {
  // Layout wraps all main pages for navigation
  // Auth pages remain unwrapped
    return (
    <BrowserRouter>
    <Routes>
        <Route element={<MainLayout />}>
            <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
            <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />
            <Route path="/forgot-password" element={<GuestRoute><ForgotPasswordPage /></GuestRoute>} />
            <Route path="/reset-password" element={<GuestRoute><ResetPasswordPage /></GuestRoute>} />
            <Route path="/confirm-email" element={<ConfirmEmailPage />} />
            <Route
            path="/screening/:tableName"
            element={<PrivateRoute><ScreeningPage /></PrivateRoute>}
            />
            <Route
            path="/upload"
            element={<PrivateRoute><FileUploadPage /></PrivateRoute>}
            />
            <Route path="/" element={<PrivateRoute><ChatPage /></PrivateRoute>} />
            <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
    </Routes>
    </BrowserRouter>
  );
}

export default App;

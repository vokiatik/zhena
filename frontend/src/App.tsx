import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useUser } from "./contexts";
import { LoginPage, RegisterPage, ForgotPasswordPage, ResetPasswordPage, ConfirmEmailPage, RoleGuard } from "./components/Auth";
import { FileUploadPage } from "./pages/UploadPage";
import { ChatPage } from "./pages/ChatPage";
import ScreeningPage from "./pages/PictureScreening/PictureScreening";
import { MainLayout } from "./pages/Layout";
import ProcessSettingsList from "./components/ProcessSettings/ProcessSettings";
import ProcessSettingsForm from "./components/ProcessSettings/ProcessSettingsForm";
import ProcessInstancesPage from "./pages/ProcessInstances/ProcessInstances";
import LinkUploadPage from "./pages/LinkUpload/LinkUpload";
import "./assets/styles/Global.css";

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
            path="/screening/process/:processId"
            element={
              <RoleGuard allowedRoles={["admin", "marketing_specialist", "analyst"]}>
                <ScreeningPage />
              </RoleGuard>
            }
          />
          <Route
            path="/screening/:role"
            element={
              <RoleGuard allowedRoles={["admin", "marketing_specialist", "analyst"]}>
                <ScreeningPage />
              </RoleGuard>
            }
          />
          <Route
            path="/processes"
            element={
              <RoleGuard allowedRoles={["admin", "marketing_specialist", "analyst"]}>
                <ProcessInstancesPage />
              </RoleGuard>
            }
          />
          <Route
            path="/link-upload"
            element={
              <RoleGuard allowedRoles={["admin", "marketing_specialist"]}>
                <LinkUploadPage />
              </RoleGuard>
            }
          />
          <Route
            path="/upload/:defaultfiletype?"
            element={
              <RoleGuard allowedRoles={["admin", "marketing_specialist"]}>
                <FileUploadPage />
              </RoleGuard>
            }
          />
          <Route
            path="/process/:processId"
            element={
              <RoleGuard allowedRoles={["admin"]}>
                <ProcessSettingsForm />
              </RoleGuard>
            }
          />
          <Route
            path="/process"
            element={
              <RoleGuard allowedRoles={["admin"]}>
                <ProcessSettingsList />
              </RoleGuard>
            }
          />
          <Route
            path="/"
            element={
              <PrivateRoute>
                <ChatPage />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;

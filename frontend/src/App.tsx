import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { useUser } from "./contexts";
import { LoginPage, RegisterPage, ForgotPasswordPage, ResetPasswordPage, ConfirmEmailPage, RoleGuard } from "./components/Auth";
import { FileUploadPage } from "./pages/UploadPage";
import { ChatPage } from "./pages/ChatPage";
import ScreeningPage from "./pages/PictureScreening/PictureScreening";
import { MainLayout } from "./pages/Layout";
import ProcessSettingsList from "./components/ProcessSettings/ProcessSettings";
import ProcessInstancesPage from "./pages/ProcessInstances/ProcessInstances";
import LinkUploadPage from "./pages/LinkUpload/LinkUpload";
import "./assets/styles/Global.css";
import { ReferenceSettings } from "./pages/Settings/Reference";
import { AppFooter } from "./components/AppFooter";

function LogoutRoute() {
  const { logout } = useUser();
  React.useEffect(() => { logout(); }, [logout]);
  return <Navigate to="/login" replace />;
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

function App() {
  return (
    <>
      <BrowserRouter>
        <div className="app-wrapper">
          <Routes>
            <Route element={<MainLayout />}>
              <Route path="/login" element={<GuestRoute><LoginPage /></GuestRoute>} />
              <Route path="/register" element={<GuestRoute><RegisterPage /></GuestRoute>} />
              <Route path="/forgot-password" element={<GuestRoute><ForgotPasswordPage /></GuestRoute>} />
              <Route path="/reset-password" element={<GuestRoute><ResetPasswordPage /></GuestRoute>} />
              <Route path="/confirm-email" element={<ConfirmEmailPage />} />
              <Route path="/logout" element={<LogoutRoute />} />
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
                path="/settings/process"
                element={
                  <RoleGuard allowedRoles={["admin"]}>
                    <ProcessSettingsList />
                  </RoleGuard>
                }
              />
              <Route
                path="/settings/reference"
                element={
                  <RoleGuard allowedRoles={["admin"]}>
                    <ReferenceSettings />
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
          <AppFooter />
        </div>
      </BrowserRouter>
    </>
  );
}

export default App;

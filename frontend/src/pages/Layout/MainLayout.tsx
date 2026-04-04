import "./MainLayout.css";
import { MenuSidebar } from "../../components/Menu";
import { Outlet } from "react-router-dom";
import { useUser } from "../../contexts";

export default function MainLayout() {
  const { user } = useUser();

  return (
    <div className="main-layout">
      <main className="layout__content">
        <Outlet />
      </main>
      {user && (
        <div className="layout__sidebar">
          <MenuSidebar />
        </div>
      )}
    </div>
  );
}
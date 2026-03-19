
import "./MainLayout.css";

import { MenuSidebar } from "../../components/Menu";
import { Outlet } from "react-router-dom";

export default function MainLayout() {
  return (
    <div className="main-layout">
        <main className="layout__content">
            <Outlet />
        </main>
        <MenuSidebar />
    </div>
  );
}
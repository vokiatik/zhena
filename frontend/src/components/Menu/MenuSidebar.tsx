import { useState } from "react";
import { Link } from "react-router-dom";
import "./MenuSidebar.css";
import { useUser } from "../../contexts";

export default function MenuSidebar() {
  const { user, hasAnyRole } = useUser();
  const [openAccordion, setOpenAccordion] = useState<string | null>(null);

  const toggleAccordion = (key: string) => {
    setOpenAccordion((prev) => (prev === key ? null : key));
  };

  if (!user) {
    return null;
  }
  return (
    <aside className="menusidebar menusidebar--right">
      <nav className="menusidebar__nav">
        {hasAnyRole("admin", "marketing_specialist") && (
          <Link to="/" className="menusidebar__nav-link">Chat</Link>
        )}
        {hasAnyRole("admin", "marketing_specialist", "analyst") && (
          <Link to="/processes" className="menusidebar__nav-link">Processes</Link>
        )}
        {hasAnyRole("admin", "marketing_specialist") && (
          <Link to="/upload" className="menusidebar__nav-link">File Upload</Link>
        )}
        {hasAnyRole("admin", "marketing_specialist") && (
          <Link to="/link-upload" className="menusidebar__nav-link">Link Upload</Link>
        )}
        {hasAnyRole("admin") && (
          <div className="menusidebar__accordion">
            <button
              className={`menusidebar__accordion-toggle ${openAccordion === "settings" ? "menusidebar__accordion-toggle--open" : ""}`}
              onClick={() => toggleAccordion("settings")}
            >
              <span>Settings</span>
              <span className="menusidebar__accordion-arrow" />
            </button>
            <div className={`menusidebar__accordion-body ${openAccordion === "settings" ? "menusidebar__accordion-body--open" : ""}`}>
              <Link to="/settings/process" className="menusidebar__nav-link">Process Settings</Link>
              <Link to="/settings/reference" className="menusidebar__nav-link">Reference Settings</Link>
            </div>
          </div>
        )}
      </nav>

      {user && (
        <div className="menusidebar__user-info">
          <span className="menusidebar__user-email">{user.email}</span>
          <Link to="/logout" className="menusidebar__logout-link">Log out</Link>
        </div>
      )}
    </aside>
  );
}
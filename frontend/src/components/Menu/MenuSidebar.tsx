import { Link } from "react-router-dom";
import "./MenuSidebar.css";
import { useUser } from "../../contexts";

export default function MenuSidebar() {
  const { user, isLoading, hasAnyRole } = useUser();

  if (!user && !isLoading) {
    return null;
  }
  return (
    <aside className="menusidebar menusidebar--right">
      <nav className="menusidebar__nav">
        {hasAnyRole("admin", "marketing_specialist") && (
          <Link to="/" className="menusidebar__nav-link">Chat</Link>
        )}
        {hasAnyRole("admin", "marketing_specialist", "analyst") && (
          <Link to="/screening/table1" className="menusidebar__nav-link">Picture Screening</Link>
        )}
        {hasAnyRole("admin", "marketing_specialist") && (
          <Link to="/upload" className="menusidebar__nav-link">File Upload</Link>
        )}
        {hasAnyRole("admin") && (
          <Link to="/process" className="menusidebar__nav-link">Process Settings</Link>
        )}
      </nav>
    </aside>
  );
}
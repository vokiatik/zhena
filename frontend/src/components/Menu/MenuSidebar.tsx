import { Link } from "react-router-dom";
import "./MenuSidebar.css";
import { useUser } from "../../contexts";

export default function MenuSidebar() {
  const { user, isLoading } = useUser();

  if (!user && !isLoading) {
    return null; // Don't show the sidebar if the user is not logged in
  }
  return (
    <aside className="menusidebar menusidebar--right">
      <nav className="menusidebar__nav">
        <Link to="/" className="menusidebar__nav-link">Chat</Link>
        <Link to="/screening/table1" className="menusidebar__nav-link">Picture Screening</Link>
        <Link to="/upload" className="menusidebar__nav-link">File Upload</Link>
        <Link to="/process" className="menusidebar__nav-link">Process Settings</Link>
      </nav>
      {/* Add your user/logout section here */}
    </aside>
  );
}
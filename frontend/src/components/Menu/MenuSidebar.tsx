import { Link } from "react-router-dom";
import "./MenuSidebar.css";

export default function MenuSidebar() {
  return (
    <aside className="menusidebar menusidebar--right">
      <nav className="menusidebar__nav">
        <Link to="/" className="menusidebar__nav-link">Chat</Link>
        <Link to="/screening/table1" className="menusidebar__nav-link">Picture Screening</Link>
        <Link to="/settings" className="menusidebar__nav-link">Settings</Link>
      </nav>
      {/* Add your user/logout section here */}
    </aside>
  );
}
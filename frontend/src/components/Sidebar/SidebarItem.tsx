interface SidebarItemProps {
  title: string;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

export default function SidebarItem({ title, isActive, onSelect, onDelete }: SidebarItemProps) {
  return (
    <div
      className={`sidebar__item ${isActive ? "sidebar__item--active" : ""}`}
      onClick={onSelect}
    >
      <span className="sidebar__item-title">{title}</span>
      <button
        className="sidebar__item-delete"
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
        aria-label="Delete chat"
      >
        ✕
      </button>
    </div>
  );
}

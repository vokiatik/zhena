import { useState } from "react";
import type { DiskFolder } from "../../types/yandex_disk";
import "./YandexDiskFolderTree.css";

interface Props {
    tree: DiskFolder;
    selected: Set<string>;
    onChange: (next: Set<string>) => void;
}

// Collect all descendant folder paths (including self).
export function collectAllPaths(node: DiskFolder): string[] {
    const paths: string[] = [node.path];
    for (const child of node.folders) {
        paths.push(...collectAllPaths(child));
    }
    return paths;
}

// A leaf folder is one that has files directly inside it.
function isLeaf(node: DiskFolder): boolean {
    return node.files.length > 0;
}

// Total selectable items under a node (files at leaf, or all nested leaf files).
function countItems(node: DiskFolder): number {
    if (isLeaf(node)) return node.files.length;
    return node.folders.reduce((sum, c) => sum + countItems(c), 0);
}

// Returns true when any path in the subtree is selected.
function anySelected(node: DiskFolder, selected: Set<string>): boolean {
    if (selected.has(node.path)) return true;
    return node.folders.some((c) => anySelected(c, selected));
}

function FolderNode({
    node,
    selected,
    onChange,
    depth,
}: {
    node: DiskFolder;
    selected: Set<string>;
    onChange: (next: Set<string>) => void;
    depth: number;
}) {
    const allChildren = collectAllPaths(node);
    const isChecked = selected.has(node.path);
    const someChildChecked = allChildren.some((p) => p !== node.path && selected.has(p));
    const indeterminate = !isChecked && someChildChecked;

    // Open by default only when something inside is selected.
    const [open, setOpen] = useState(() => anySelected(node, selected));

    // Leaf nodes: sibling folders were already filtered out by the backend
    // (or are hidden because they sit next to images). Don't render sub-folders
    // for leaf nodes at all.
    const visibleChildren = isLeaf(node) ? [] : node.folders;
    const hasChildren = visibleChildren.length > 0;
    const total = countItems(node);

    const handleCheck = () => {
        const next = new Set(selected);
        if (isChecked) {
            for (const p of allChildren) next.delete(p);
        } else {
            for (const p of allChildren) next.add(p);
        }
        onChange(next);
    };

    const handleToggleOpen = (e: React.MouseEvent) => {
        e.preventDefault();
        setOpen((v) => !v);
    };

    return (
        <li className="ydisk-node" style={{ paddingLeft: depth === 0 ? 0 : "1.25rem" }}>
            <div className="ydisk-row">
                {/* Expand/collapse arrow – only for non-leaf nodes with children */}
                {hasChildren ? (
                    <button
                        type="button"
                        className={`ydisk-arrow ${open ? "ydisk-arrow--open" : ""}`}
                        onClick={handleToggleOpen}
                        aria-label={open ? "Collapse" : "Expand"}
                    >
                        ▶
                    </button>
                ) : (
                    <span className="ydisk-arrow ydisk-arrow--spacer" />
                )}

                <label className="ydisk-label">
                    <input
                        type="checkbox"
                        className="ydisk-checkbox"
                        checked={isChecked}
                        ref={(el) => { if (el) el.indeterminate = indeterminate; }}
                        onChange={handleCheck}
                    />
                    <span className="ydisk-icon">
                        {isLeaf(node) ? "🖼" : "📁"}
                    </span>
                    <span className="ydisk-name">{node.name}</span>
                    <span className="ydisk-count">
                        {total} {isLeaf(node) ? (total === 1 ? "file" : "files") : (total === 1 ? "item" : "items")}
                    </span>
                </label>
            </div>

            {hasChildren && open && (
                <ul className="ydisk-children">
                    {visibleChildren.map((child) => (
                        <FolderNode
                            key={child.path}
                            node={child}
                            selected={selected}
                            onChange={onChange}
                            depth={depth + 1}
                        />
                    ))}
                </ul>
            )}
        </li>
    );
}

export default function YandexDiskFolderTree({ tree, selected, onChange }: Props) {
    return (
        <ul className="ydisk-tree">
            <FolderNode node={tree} selected={selected} onChange={onChange} depth={0} />
        </ul>
    );
}

import { useState, useRef } from "react";
import { useApi } from "../../api";
import { useProcessInstances } from "../../hooks/useProcessInstances";
import { useToast } from "../../contexts/ToastContext";
import YandexDiskFolderTree, { collectAllPaths } from "../../components/YandexDisk/YandexDiskFolderTree";
import type { DiskFolder } from "../../types/yandex_disk";

// ── Default selection: last month of last year ────────────────────────────

const RUSSIAN_MONTHS: Record<number, string[]> = {
    1: ["январь", "января", "январе"],
    2: ["февраль", "февраля", "феврале"],
    3: ["март", "марта", "марте"],
    4: ["апрель", "апреля", "апреле"],
    5: ["май", "мая"],
    6: ["июнь", "июня", "июне"],
    7: ["июль", "июля", "июле"],
    8: ["август", "августа", "августе"],
    9: ["сентябрь", "сентября", "сентябре"],
    10: ["октябрь", "октября", "октябре"],
    11: ["ноябрь", "ноября", "ноябре"],
    12: ["декабрь", "декабря", "декабре"],
};

function getDefaultSelection(tree: DiskFolder): Set<string> {
    const now = new Date();
    const targetYear = now.getFullYear() - 1;
    const targetMonth = 12; // December — last month of last year
    const monthTokens = RUSSIAN_MONTHS[targetMonth];
    const yearStr = String(targetYear);
    const padded = String(targetMonth).padStart(2, "0");

    function matchesTarget(name: string): boolean {
        const lower = name.toLowerCase();
        const hasYear = lower.includes(yearStr);
        const hasMonth =
            monthTokens.some((m) => lower.includes(m)) ||
            lower.includes(`-${padded}`) ||
            lower.includes(`_${padded}`) ||
            lower.includes(`/${padded}`);
        return hasYear && hasMonth;
    }

    const selected = new Set<string>();

    function walk(node: DiskFolder): void {
        if (matchesTarget(node.name)) {
            collectAllPaths(node).forEach((p) => selected.add(p));
            return; // don't recurse further — whole subtree is selected
        }
        for (const child of node.folders) walk(child);
    }

    walk(tree);
    return selected;
}

interface ProvideLinkStepProps {
    processId: string;
    onDone: () => void;
}

type Phase = "form" | "tree" | "importing";

export default function ProvideLinkStep({ processId, onDone }: ProvideLinkStepProps) {
    const { post } = useApi();
    const { provideLink } = useProcessInstances();
    const { showToast } = useToast();

    // ── Phase 1: user enters link + token ────────────────────────
    const [link, setLink] = useState("");
    const [token, setToken] = useState("");
    const [phase, setPhase] = useState<Phase>("form");
    const [loadingTree, setLoadingTree] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const abortRef = useRef<AbortController | null>(null);

    // ── Phase 2: folder tree + selection ─────────────────────────
    const [tree, setTree] = useState<DiskFolder | null>(null);
    const [selected, setSelected] = useState<Set<string>>(new Set());

    const handleFetchTree = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!link.trim() || !token.trim()) {
            setError("Both link and OAuth token are required.");
            return;
        }
        const controller = new AbortController();
        abortRef.current = controller;
        setLoadingTree(true);
        setError(null);
        try {
            const res = await post<DiskFolder>("/yandex-disk/tree", {
                url: link.trim(),
                token: token.trim(),
            }, { signal: controller.signal });
            setTree(res.data);
            setSelected(getDefaultSelection(res.data));
            setPhase("tree");
        } catch (err: any) {
            if ((err as any)?.code === "ERR_CANCELED" || (err as any)?.name === "CanceledError") {
                // user cancelled — stay on the form, no error message
                return;
            }
            setError(err?.response?.data?.detail || err?.message || "Failed to fetch folder tree.");
        } finally {
            abortRef.current = null;
            setLoadingTree(false);
        }
    };

    const handleImport = async () => {
        if (selected.size === 0) {
            setError("Select at least one folder to import.");
            return;
        }
        setPhase("importing");
        setError(null);
        try {
            const res = await post<{ ok: boolean; inserted: number; skipped: number }>(
                "/yandex-disk/import",
                {
                    process_id: processId,
                    token: token.trim(),
                    selected_paths: Array.from(selected),
                }
            );
            const { inserted, skipped } = res.data;
            showToast(`Imported ${inserted} picture${inserted !== 1 ? "s" : ""}${skipped ? ` (${skipped} folder${skipped !== 1 ? "s" : ""} skipped)` : ""}.`, "success");

            // Store the link in the process comment and advance status
            await provideLink(processId, link.trim());
            onDone();
        } catch (err: any) {
            setError(err?.response?.data?.detail || err?.message || "Import failed.");
            setPhase("tree");
        }
    };

    // ── Render ───────────────────────────────────────────────────

    if (phase === "form" || phase === "tree") {
        return (
            <div className="dp-step-body">
                {phase === "form" && (
                    <>
                        <p className="dp-step-desc">
                            Enter the Yandex Disk folder URL and your personal OAuth token.
                            The token is used only for this request and is never stored.
                        </p>
                        <form onSubmit={handleFetchTree} className="dp-link-form">
                            <label className="dp-link-label">Yandex Disk folder URL</label>
                            <input
                                type="text"
                                value={link}
                                onChange={(e) => setLink(e.target.value)}
                                placeholder="https://disk.yandex.ru/client/disk/…"
                                className="dp-link-input"
                                autoComplete="off"
                                name="ydisk-folder-url"
                                disabled={loadingTree}
                            />
                            <label className="dp-link-label">OAuth token</label>
                            <input
                                type="password"
                                value={token}
                                onChange={(e) => setToken(e.target.value)}
                                placeholder="y0_AgAAAA…"
                                className="dp-link-input"
                                autoComplete="new-password"
                                name="ydisk-oauth-token"
                                disabled={loadingTree}
                            />
                            <p className="dp-link-hint">
                                Don't have a token?{" "}
                                <a
                                    href="https://yandex.ru/dev/disk/poligon/"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="dp-link-hint-link"
                                >
                                    Get one at the Yandex Disk API playground
                                </a>{" "}
                                — click <strong>Получить OAuth-токен</strong> and copy the value.
                            </p>
                            {error && <p className="dp-msg dp-msg--error">{error}</p>}
                            <button
                                type="submit"
                                className="button-primary dp-submit-btn"
                                disabled={loadingTree || !link.trim() || !token.trim()}
                            >
                                {loadingTree ? "Loading…" : "Browse Folders"}
                            </button>
                            {loadingTree && (
                                <button
                                    type="button"
                                    className="button-secondary dp-submit-btn"
                                    onClick={() => abortRef.current?.abort()}
                                >
                                    Cancel
                                </button>
                            )}
                        </form>
                    </>
                )}

                {phase === "tree" && tree && (
                    <>
                        <div className="dp-tree-header">
                            <button
                                className="dp-back-btn"
                                type="button"
                                onClick={() => { setPhase("form"); setTree(null); setSelected(new Set()); setError(null); }}
                            >
                                ← Change link
                            </button>
                            <p className="dp-step-desc dp-step-desc--inline">
                                Select the folders to import for this report.
                                Selecting a parent folder selects all its children.
                            </p>
                        </div>

                        <YandexDiskFolderTree
                            tree={tree}
                            selected={selected}
                            onChange={setSelected}
                        />

                        {error && <p className="dp-msg dp-msg--error">{error}</p>}

                        <div className="dp-tree-footer">
                            <span className="dp-selection-count">
                                {selected.size} folder{selected.size !== 1 ? "s" : ""} selected
                            </span>
                            <button
                                type="button"
                                className="button-primary dp-submit-btn"
                                disabled={selected.size === 0}
                                onClick={handleImport}
                            >
                                Import Selected
                            </button>
                        </div>
                    </>
                )}
            </div>
        );
    }

    return (
        <div className="dp-step-body">
            <p className="dp-step-desc">Importing pictures from Yandex Disk…</p>
        </div>
    );
}

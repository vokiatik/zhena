import { useState, useRef, useCallback, useEffect } from "react";

const SAVE_DELAY = 2000;

export function useSaveTimer(onSave: () => Promise<void>) {
    const [saving, setSaving] = useState(false);
    const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    const cancel = useCallback(() => {
        if (timerRef.current) {
            clearTimeout(timerRef.current);
            timerRef.current = null;
        }
        setSaving(false);
    }, []);

    const start = useCallback(() => {
        if (saving) return;
        setSaving(true);
        timerRef.current = setTimeout(async () => {
            timerRef.current = null;
            setSaving(false);
            await onSave();
        }, SAVE_DELAY);
    }, [saving, onSave]);

    const reset = useCallback(() => {
        cancel();
    }, [cancel]);

    // Cancel on any keypress while saving
    useEffect(() => {
        if (!saving) return;
        const handler = (e: KeyboardEvent) => {
            e.preventDefault();
            cancel();
        };
        window.addEventListener("keydown", handler);
        return () => window.removeEventListener("keydown", handler);
    }, [saving, cancel]);

    return { saving, start, reset };
}

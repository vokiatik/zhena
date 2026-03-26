import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import "./CustomToast.css";

export type ToastType = "success" | "error" | "info" | "warning";

type Props = {
    message: string;
    type?: ToastType;
    duration?: number;
    onDone?: () => void;
};

export default function CustomToast({
    message,
    type = "info",
    duration = 3000,
    onDone,
}: Props) {
    const [leaving, setLeaving] = useState(false);

    useEffect(() => {
        const fadeTimer = window.setTimeout(() => {
            setLeaving(true);
        }, duration - 300);

        const doneTimer = window.setTimeout(() => {
            onDone?.();
        }, duration);

        return () => {
            window.clearTimeout(fadeTimer);
            window.clearTimeout(doneTimer);
        };
    }, [duration, onDone]);

    return createPortal(
        <div className={`custom-toast custom-toast--${type} ${leaving ? "custom-toast--hide" : ""}`}>
            {message}
        </div>,
        document.body
    );
}
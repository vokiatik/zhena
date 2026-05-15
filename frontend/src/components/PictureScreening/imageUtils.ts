const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const DRIVE_FILE_RE = /drive\.google\.com\/file\/d\/([^/?#]+)/;

/**
 * Resolve a Google Drive sharing URL to a direct thumbnail URL (no backend proxy).
 * The browser fetches this directly from Google — faster than routing via the proxy.
 */
export function toPlainImageUrl(url: string): string {
    const m = DRIVE_FILE_RE.exec(url);
    if (m) {
        return `https://drive.google.com/thumbnail?id=${m[1]}&sz=w1000`;
    }
    return url;
}

/** Convert a Google Drive sharing URL to an image URL served via the backend proxy. */
export function toDirectImageUrl(url: string): string {
    if (url.includes("drive.google.com") || url.includes("googleusercontent.com")) {
        return `${API_BASE}/proxy/image?url=${encodeURIComponent(url)}`;
    }
    return url;
}

// ── Per-session image source cache ────────────────────────────────
// Maps original URL → resolved src that loaded successfully.
// Prevents re-fetching images when navigating back to a previously seen slide.
const _imageCache = new Map<string, string>();

export function getCachedSrc(originalUrl: string): string | undefined {
    return _imageCache.get(originalUrl);
}

export function setCachedSrc(originalUrl: string, loadedSrc: string): void {
    _imageCache.set(originalUrl, loadedSrc);
}

export function evictCachedSrc(originalUrl: string): void {
    _imageCache.delete(originalUrl);
}

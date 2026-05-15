import { useState, useEffect } from "react";
import type { AdvertisementLinkItem } from "../../types/advertisement";
import {
    toDirectImageUrl,
    toPlainImageUrl,
    getCachedSrc,
    setCachedSrc,
    evictCachedSrc,
} from "./imageUtils";

interface AdvertisementImageCarouselProps {
    links: AdvertisementLinkItem[];
    incorrectIds: Set<string>;
    onToggleIncorrect: (linkId: string) => void;
}

export default function AdvertisementImageCarousel({
    links,
    incorrectIds,
    onToggleIncorrect,
}: AdvertisementImageCarouselProps) {
    const [carouselIndex, setCarouselIndex] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    // IDs of links for which the user has explicitly requested proxy load
    const [proxyIds, setProxyIds] = useState<Set<string>>(new Set());

    // Reset index and proxy state when the link list changes (new advertisement loaded)
    useEffect(() => {
        setCarouselIndex(0);
        setProxyIds(new Set());
    }, [links]);

    // Update loading state when slide changes — skip spinner if already cached
    useEffect(() => {
        const link = links[Math.min(carouselIndex, links.length - 1)];
        if (!link) return;
        setIsLoading(getCachedSrc(link.url) === undefined);
    }, [carouselIndex, links]);

    // Prefetch the next image using the plain URL so it's ready before the user navigates
    useEffect(() => {
        const nextIndex = carouselIndex + 1;
        if (nextIndex >= links.length) return;
        const next = links[nextIndex];
        if (getCachedSrc(next.url) !== undefined) return; // already cached
        const img = new Image();
        img.src = toPlainImageUrl(next.url);
        img.onload = () => setCachedSrc(next.url, img.src);
    }, [carouselIndex, links]);

    if (links.length === 0) {
        return <div className="pv-no-image">No images</div>;
    }

    const safeIndex = Math.min(carouselIndex, links.length - 1);
    const currentLink = links[safeIndex];

    if (!currentLink) {
        return <div className="pv-no-image">No images</div>;
    }

    const getSrc = (link: AdvertisementLinkItem): string => {
        const cached = getCachedSrc(link.url);
        if (cached !== undefined) return cached;
        return proxyIds.has(link.id)
            ? toDirectImageUrl(link.url)
            : toPlainImageUrl(link.url);
    };

    const currentSrc = getSrc(currentLink);

    const handleLoad = () => {
        setCachedSrc(currentLink.url, currentSrc);
        setIsLoading(false);
    };

    const handleReload = () => {
        evictCachedSrc(currentLink.url);
        setProxyIds((prev) => new Set(prev).add(currentLink.id));
        setIsLoading(true);
    };

    return (
        <>
            <div className={`pv-carousel-frame${incorrectIds.has(currentLink.id) ? " pv-carousel-frame--incorrect" : ""}`}>
                {isLoading && (
                    <div className="pv-image-loader">
                        <span className="pv-image-spinner" />
                    </div>
                )}
                <img
                    src={currentSrc}
                    alt="advertisement"
                    className="pv-image"
                    style={isLoading ? { opacity: 0, position: "absolute" } : undefined}
                    onLoad={handleLoad}
                    onError={() => setIsLoading(false)}
                />
            </div>

            {/* Checkbox + reload button row */}
            <div className="pv-carousel-actions">
                <label className="pv-link-checkbox">
                    <input
                        type="checkbox"
                        checked={!incorrectIds.has(currentLink.id)}
                        onChange={() => onToggleIncorrect(currentLink.id)}
                    />
                    <span>Image fits the criteria</span>
                </label>
                <button type="button" className="pv-reload-btn" onClick={handleReload}>
                    ↺ Reload via proxy
                </button>
            </div>

            {/* Navigation */}
            {links.length > 1 && (
                <div className="pv-carousel-nav">
                    <button
                        type="button"
                        className="pv-carousel-btn"
                        onClick={() => setCarouselIndex((i) => Math.max(0, i - 1))}
                        disabled={safeIndex === 0}
                    >
                        ‹
                    </button>
                    <span className="pv-carousel-counter">
                        {safeIndex + 1} / {links.length}
                        {incorrectIds.has(currentLink.id) && (
                            <span className="pv-carousel-badge--incorrect"> ✗</span>
                        )}
                    </span>
                    <button
                        type="button"
                        className="pv-carousel-btn"
                        onClick={() => setCarouselIndex((i) => Math.min(links.length - 1, i + 1))}
                        disabled={safeIndex === links.length - 1}
                    >
                        ›
                    </button>
                </div>
            )}

            {/* Dot strip */}
            {links.length > 1 && (
                <div className="pv-carousel-dots">
                    {links.map((lnk, idx) => (
                        <button
                            key={lnk.id}
                            type="button"
                            className={[
                                "pv-carousel-dot",
                                idx === safeIndex ? "pv-carousel-dot--active" : "",
                                incorrectIds.has(lnk.id) ? "pv-carousel-dot--incorrect" : "",
                            ].filter(Boolean).join(" ")}
                            onClick={() => setCarouselIndex(idx)}
                            aria-label={`Image ${idx + 1}${incorrectIds.has(lnk.id) ? " (incorrect)" : ""}`}
                        />
                    ))}
                </div>
            )}
        </>
    );
}

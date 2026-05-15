import { useState, useCallback, useEffect, useMemo } from "react";
import type {
    AdvertisementItem,
    AdvertisementLinkItem,
    RangeValueRef,
    SimpleValueRef,
    ScreeningOptions,
} from "../../types/advertisement";
import CustomDropdown from "../shared/dropdown/CustomDropdown";
import RangeField from "./RangeField";
import AdvertisementImageCarousel from "./AdvertisementImageCarousel";

interface AdvertisementViewerProps {
    advertisement: AdvertisementItem;
    options: ScreeningOptions;
    onVerify: (payload: {
        brand_id: string | null;
        brand_range_ids: string[];
        product_category_id: string | null;
        product_category_range_ids: string[];
        brand_category_id: string | null;
        advertising_category_ids: string[];
        incorrect_link_ids: string[];
    }) => Promise<void>;
    onDecline?: () => Promise<void>;
    onReturnToUnverified?: () => Promise<void>;
}

export default function AdvertisementViewer({
    advertisement,
    options,
    onVerify,
    onDecline,
    onReturnToUnverified,
}: AdvertisementViewerProps) {
    console.log("AdvertisementViewer render", { advertisement, options });
    const [brandId, setBrandId] = useState<string | null>(
        advertisement.brand?.id ?? null
    );
    const [brandRange, setBrandRange] = useState<RangeValueRef[]>(
        advertisement.brand_range
    );
    const [productCategoryId, setProductCategoryId] = useState<string | null>(
        advertisement.product_category?.id ?? null
    );
    const [productCategoryRange, setProductCategoryRange] = useState<RangeValueRef[]>(
        advertisement.product_category_range
    );
    const [brandCategoryId, setBrandCategoryId] = useState<string | null>(
        advertisement.brand_category?.id ?? null
    );
    const [advertisingCategory, setAdvertisingCategory] = useState<RangeValueRef[]>(
        advertisement.advertising_category
    );

    const [isSaving, setIsSaving] = useState(false);
    const [isDeclining, setIsDeclining] = useState(false);
    const [isReturning, setIsReturning] = useState(false);

    // ── Carousel state ────────────────────────────────────────────
    // Memoised so the carousel's useEffect([links]) doesn't fire on every parent render
    const links: AdvertisementLinkItem[] = useMemo(() =>
        advertisement.links?.filter((l) => !l.is_incorrect) ??
        (advertisement.url ? [{ id: "legacy", url: advertisement.url, is_incorrect: false }] : []),
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [advertisement.id, advertisement.links, advertisement.url]
    );
    const [incorrectIds, setIncorrectIds] = useState<Set<string>>(
        () => new Set(links.filter((l) => l.is_incorrect).map((l) => l.id))
    );

    // Reset all fields when advertisement changes
    useEffect(() => {
        setBrandId(advertisement.brand?.id ?? null);
        setBrandRange(advertisement.brand_range);
        setProductCategoryId(advertisement.product_category?.id ?? null);
        setProductCategoryRange(advertisement.product_category_range);
        setBrandCategoryId(advertisement.brand_category?.id ?? null);
        setAdvertisingCategory(advertisement.advertising_category);
        setIncorrectIds(new Set(
            (advertisement.links ?? []).filter((l) => l.is_incorrect).map((l) => l.id)
        ));
    }, [advertisement.id]);

    const toggleIncorrect = (linkId: string) => {
        setIncorrectIds((prev) => {
            const next = new Set(prev);
            if (next.has(linkId)) {
                next.delete(linkId);
            } else {
                next.add(linkId);
            }
            return next;
        });
    };

    // ── Range helpers ────────────────────────────────────────────

    const addToRange = useCallback(
        (
            id: string,
            allOptions: SimpleValueRef[],
            setter: React.Dispatch<React.SetStateAction<RangeValueRef[]>>
        ) => {
            const opt = allOptions.find((o) => o.id === id);
            if (!opt) return;
            setter((prev) => {
                if (prev.some((v) => v.id === id)) return prev;
                return [...prev, { row_id: `new-${id}`, id: opt.id, value: opt.value }];
            });
        },
        []
    );

    const removeFromRange = useCallback(
        (rowId: string, setter: React.Dispatch<React.SetStateAction<RangeValueRef[]>>) => {
            setter((prev) => prev.filter((v) => v.row_id !== rowId));
        },
        []
    );

    // ── Change detection ──────────────────────────────────────────
    const isProcessed = advertisement.verified || advertisement.declined;
    const setsEqual = (a: Set<string>, b: Set<string>) =>
        a.size === b.size && [...a].every((v) => b.has(v));
    // For processed ads: only enable Update when something actually changed
    const hasChanged =
        brandId !== (advertisement.brand?.id ?? null) ||
        brandCategoryId !== (advertisement.brand_category?.id ?? null) ||
        productCategoryId !== (advertisement.product_category?.id ?? null) ||
        !setsEqual(new Set(brandRange.map((v) => v.id)), new Set(advertisement.brand_range.map((v) => v.id))) ||
        !setsEqual(new Set(productCategoryRange.map((v) => v.id)), new Set(advertisement.product_category_range.map((v) => v.id))) ||
        !setsEqual(new Set(advertisingCategory.map((v) => v.id)), new Set(advertisement.advertising_category.map((v) => v.id))) ||
        incorrectIds.size > 0;

    // ── Handlers ─────────────────────────────────────────────────

    const handleSave = async () => {
        if (isSaving || isDeclining || isReturning) return;
        setIsSaving(true);
        try {
            await onVerify({
                brand_id: brandId,
                brand_range_ids: brandRange.map((v) => v.id),
                product_category_id: productCategoryId,
                product_category_range_ids: productCategoryRange.map((v) => v.id),
                brand_category_id: brandCategoryId,
                advertising_category_ids: advertisingCategory.map((v) => v.id),
                incorrect_link_ids: Array.from(incorrectIds),
            });
        } finally {
            setIsSaving(false);
        }
    };

    const handleDecline = async () => {
        if (isSaving || isDeclining || isReturning || !onDecline) return;
        setIsDeclining(true);
        try {
            await onDecline();
        } finally {
            setIsDeclining(false);
        }
    };

    const handleReturnToUnverified = async () => {
        if (isSaving || isDeclining || isReturning || !onReturnToUnverified) return;
        setIsReturning(true);
        try {
            await onReturnToUnverified();
        } finally {
            setIsReturning(false);
        }
    };

    // ── Render ───────────────────────────────────────────────────

    return (
        <div className="pv-wrapper">
            <div className="pv-image-fields-container">
                <div className="pv-image-container">
                    <AdvertisementImageCarousel
                        links={links}
                        incorrectIds={incorrectIds}
                        onToggleIncorrect={toggleIncorrect}
                    />
                </div>

                <div className="pv-fields">
                    {/* 1. Brand (single dropdown) */}
                    <label className="pv-field">
                        <span className="pv-field-label">brand</span>
                        <CustomDropdown
                            options={options.brand.map((o) => ({ label: o.value, value: o.id }))}
                            value={brandId}
                            onChange={setBrandId}
                            searchable
                            placeholder="Select brand…"
                        />
                    </label>

                    {/* 2. Brand range (multi-value list) */}
                    <RangeField
                        label="brand_range"
                        values={brandRange}
                        options={options.brand}
                        onAdd={(id) => addToRange(id, options.brand, setBrandRange)}
                        onRemove={(rowId) => removeFromRange(rowId, setBrandRange)}
                    />

                    {/* 3. Product category (single dropdown) */}
                    <label className="pv-field">
                        <span className="pv-field-label">product_category</span>
                        <CustomDropdown
                            options={options.product_category.map((o) => ({ label: o.value, value: o.id }))}
                            value={productCategoryId}
                            onChange={setProductCategoryId}
                            searchable
                            placeholder="Select product category…"
                        />
                    </label>

                    {/* 4. Product category range (multi-value list) */}
                    <RangeField
                        label="product_category_range"
                        values={productCategoryRange}
                        options={options.product_category}
                        onAdd={(id) => addToRange(id, options.product_category, setProductCategoryRange)}
                        onRemove={(rowId) => removeFromRange(rowId, setProductCategoryRange)}
                    />

                    {/* 5. Brand category (single dropdown) */}
                    <label className="pv-field">
                        <span className="pv-field-label">brand_category</span>
                        <CustomDropdown
                            options={options.brand_category.map((o) => ({ label: o.value, value: o.id }))}
                            value={brandCategoryId}
                            onChange={setBrandCategoryId}
                            searchable
                            placeholder="Select brand category…"
                        />
                    </label>

                    {/* 6. Advertising category (multi-value list) */}
                    <RangeField
                        label="advertising_category"
                        values={advertisingCategory}
                        options={options.add_category}
                        onAdd={(id) => addToRange(id, options.add_category, setAdvertisingCategory)}
                        onRemove={(rowId) => removeFromRange(rowId, setAdvertisingCategory)}
                    />
                </div>
            </div>
            <div className="pv-buttons">
                {!isProcessed ? (
                    // ── Unverified: Proceed + Decline ────────────────────
                    <>
                        <button
                            className="button-primary btn-large"
                            onClick={handleSave}
                            disabled={isSaving || isDeclining}
                            type="button"
                        >
                            {isSaving ? "Saving…" : "Proceed"}
                        </button>
                        {onDecline && (
                            <button
                                className="button-danger btn-large"
                                onClick={handleDecline}
                                disabled={isSaving || isDeclining}
                                type="button"
                            >
                                {isDeclining ? "Declining…" : "Decline"}
                            </button>
                        )}
                    </>
                ) : (
                    // ── Processed: Update + Return to Unverified ─────────
                    <>
                        <button
                            className="button-primary btn-large"
                            onClick={handleSave}
                            disabled={isSaving || isReturning || !hasChanged}
                            type="button"
                        >
                            {isSaving ? "Saving…" : "Update"}
                        </button>
                        {onReturnToUnverified && (
                            <button
                                className="button-secondary btn-large"
                                onClick={handleReturnToUnverified}
                                disabled={isSaving || isDeclining || isReturning}
                                type="button"
                            >
                                {isReturning ? "Returning…" : "Return to Unverified"}
                            </button>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}


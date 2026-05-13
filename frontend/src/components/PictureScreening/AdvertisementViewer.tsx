import { useState, useCallback } from "react";
import type {
    AdvertisementItem,
    RangeValueRef,
    SimpleValueRef,
    ScreeningOptions,
} from "../../types/advertisement";
import CustomDropdown from "../shared/dropdown/CustomDropdown";
import RangeField from "./RangeField";

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
    }) => Promise<void>;
    onDecline?: () => Promise<void>;
}

export default function AdvertisementViewer({
    advertisement,
    options,
    onVerify,
    onDecline,
}: AdvertisementViewerProps) {
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

    // ── Save ─────────────────────────────────────────────────────

    const handleSave = async () => {
        if (isSaving || isDeclining) return;
        setIsSaving(true);
        try {
            await onVerify({
                brand_id: brandId,
                brand_range_ids: brandRange.map((v) => v.id),
                product_category_id: productCategoryId,
                product_category_range_ids: productCategoryRange.map((v) => v.id),
                brand_category_id: brandCategoryId,
                advertising_category_ids: advertisingCategory.map((v) => v.id),
            });
        } finally {
            setIsSaving(false);
        }
    };

    const handleDecline = async () => {
        if (isSaving || isDeclining || !onDecline) return;
        setIsDeclining(true);
        try {
            await onDecline();
        } finally {
            setIsDeclining(false);
        }
    };

    // ── Render ───────────────────────────────────────────────────

    return (
        <div className="pv-wrapper">
            <div className="pv-image-container">
                <img src={advertisement.url} alt="advertisement" className="pv-image" />
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

                {/* Read-only date fields */}
                {advertisement.first_appearance_date && (
                    <label className="pv-field">
                        <span className="pv-field-label">first_appearance_date</span>
                        <input
                            type="text"
                            className="pv-field-input"
                            value={advertisement.first_appearance_date}
                            disabled
                        />
                    </label>
                )}
                {advertisement.last_appearance_date && (
                    <label className="pv-field">
                        <span className="pv-field-label">last_appearance_date</span>
                        <input
                            type="text"
                            className="pv-field-input"
                            value={advertisement.last_appearance_date}
                            disabled
                        />
                    </label>
                )}
            </div>

            <div className="pv-buttons">
                <button
                    className="button-primary"
                    onClick={handleSave}
                    disabled={isSaving || isDeclining}
                    type="button"
                >
                    {isSaving ? "Saving…" : "Proceed"}
                </button>
                {onDecline && (
                    <button
                        className="button-danger"
                        onClick={handleDecline}
                        disabled={isSaving || isDeclining}
                        type="button"
                    >
                        {isDeclining ? "Declining…" : "Decline"}
                    </button>
                )}
            </div>
        </div>
    );
}

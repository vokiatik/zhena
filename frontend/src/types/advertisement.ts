export interface SimpleValueRef {
  id: string;
  value: string;
}

/** A range-table row: includes the junction table row id for deletes */
export interface RangeValueRef extends SimpleValueRef {
  row_id: string;
}

export interface AdvertisementItem {
  id: string;
  url: string;
  verified: boolean;
  declined: boolean;
  process_id: string | null;
  first_appearance_date: string | null;
  last_appearance_date: string | null;

  /** Single-value FK fields */
  brand: SimpleValueRef | null;
  product_category: SimpleValueRef | null;
  brand_category: SimpleValueRef | null;

  /** Multi-value range fields */
  brand_range: RangeValueRef[];
  product_category_range: RangeValueRef[];
  advertising_category: RangeValueRef[];
}

export interface ScreeningOptions {
  brand: SimpleValueRef[];
  product_category: SimpleValueRef[];
  brand_category: SimpleValueRef[];
  add_category: SimpleValueRef[];
}

export interface AdvertisementScreeningResponse {
  unverified: AdvertisementItem[];
  verified: AdvertisementItem[];
  declined: AdvertisementItem[];
  options: ScreeningOptions;
}

export interface AdvertisementVerifyPayload {
  id: string;
  process_id: string;
  brand_id: string | null;
  brand_range_ids: string[];
  product_category_id: string | null;
  product_category_range_ids: string[];
  brand_category_id: string | null;
  advertising_category_ids: string[];
}

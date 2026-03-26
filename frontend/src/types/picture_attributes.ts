export interface PictureAttributes {
  id: string;
  title: string;
  is_shown: boolean;
  is_editable: boolean;
  created_at: string;
  process_id: string;
  reference_value_presetting_type?: string; // "fixed" | "random" | null
}

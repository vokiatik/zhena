export interface ReferenceValue {
  id: string;
  value: string;
}

export interface PictureAttribute {
  id: string;
  title: string;
  is_shown: boolean;
  is_editable: boolean;
  created_at: string;
  process_id: string;
  reference_type_id?: string;
  reference_type_name?: string;
  reference_values?: ReferenceValue[];
}

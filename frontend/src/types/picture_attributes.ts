export interface PictureAttributes {
  id: string;
  title: string;
  is_shown: boolean;
  is_editable: boolean;
  created_at: string;
  file_id: string;

  reference_table_name?: string;
  reference_column_name?: string;
}

import type { PictureAttribute } from "./picture_attributes";

export interface ProcessingItem {
  id: string;
  title: string;
  description: string;
  table_name: string;
  created_at: string;
  attributes: PictureAttribute[];
}

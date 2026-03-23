import type { PictureAttributes } from "./picture_attributes";

export interface ProcessingItem {
  id: string;
  title: string;
  description: string;
  created_at: string;
  responsible_user_id: string;
  attributes: PictureAttributes[];
}

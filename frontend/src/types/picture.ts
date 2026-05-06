export interface PictureItem {
  id: string;
  url: string;
  verified: boolean;
  declined: boolean;
  [key: string]: unknown;
}

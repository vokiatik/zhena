export interface ProcessInstance {
  id: string;
  type_name: string;
  type_id: string;
  status_name: string;
  status_id: string | null;
  comment: string | null;
  initiator_id: string | null;
  total_items: number | null;
  parent_process_id: string | null;
  created_at: string;
}

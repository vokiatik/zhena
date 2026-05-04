export interface MissingReferenceValue {
  type_id: string;
  type_name: string;
  column: string;
  value: string;
}

export interface ValidationRequiredResponse {
  status: "needs_validation";
  missing_values: MissingReferenceValue[];
  existing_values_by_type: Record<string, string[]>;
}

export interface ConfirmDecision {
  type_id: string;
  column: string;
  original_value: string;
  save: boolean;
  replace_with: string | null;
}

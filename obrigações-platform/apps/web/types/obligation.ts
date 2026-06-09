export interface Obligation {
  id: number;
  contract_id: number;
  document_name: string | null;
  item_number: string | null;
  recurrence: string | null;
  obligation_text: string;
  observations: string | null;
  status: string;
  responsible: string | null;
  deadline: string | null;
  source_row: number | null;

  email_enabled: boolean;
  email_destino: string | null;
  data_envio_email: string | null;
  status_envio: string | null;
  last_email_sent_at: string | null;

  trigger_family: string | null;
  trigger_type: string | null;
  condition_raw: string | null;
  condition_canonical: string | null;
  condition_status: string | null;

  created_at: string;
  updated_at: string;
}

export interface Contract {
  id: number;
  name: string;
  code: string | null;
}

export interface ObligationStatusHistory {
  id: number;
  obligation_id: number;
  old_status: string | null;
  new_status: string;
  note: string | null;
  changed_at: string;
}

export interface ObligationDetailResponse {
  obligation: Obligation;
  history: ObligationStatusHistory[];
}

export interface ObligationsResponse {
  items: Obligation[];
  total: number;
  skip: number;
  limit: number;
}

export interface UpdateObligationPayload {
  status?: string;
  observations?: string;
  note?: string;

  email_enabled?: boolean;
  email_destino?: string | null;
  data_envio_email?: string | null;

  trigger_family?: string | null;
  trigger_type?: string | null;
  condition_raw?: string | null;
  condition_canonical?: string | null;
  condition_status?: string | null;
}

export interface ObligationCreateRequest {
  contract_id: number;
  document_name?: string | null;
  item_number?: string | null;
  recurrence?: string | null;
  obligation_text: string;
  observations?: string | null;
  responsible?: string | null;
  status?: string;

  email_enabled?: boolean;
  email_destino?: string | null;
  data_envio_email?: string | null;

  trigger_family?: string | null;
  trigger_type?: string | null;
  condition_raw?: string | null;
  condition_canonical?: string | null;
  condition_status?: string | null;
}
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ObligationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: int

    document_name: str | None = None
    item_number: str | None = None
    recurrence: str | None = None

    obligation_text: str
    observations: str | None = None

    status: str
    responsible: str | None = None
    deadline: datetime | None = None
    source_row: int | None = None

    email_enabled: bool
    email_destino: str | None = None

    manual_reminder_at: datetime | None = None
    manual_reminder_sent_at: datetime | None = None

    recurrence_mode: str | None = None
    recurrence_time: str | None = None
    recurrence_interval_days: int | None = None
    recurrence_weekday: int | None = None
    recurrence_day_of_month: int | None = None
    recurrence_month: int | None = None

    next_recurrence_at: datetime | None = None
    next_reminder_at: datetime | None = None
    last_email_sent_at: datetime | None = None

    status_envio: str | None = None

    trigger_family: str | None = None
    trigger_type: str | None = None
    condition_raw: str | None = None
    condition_canonical: str | None = None
    condition_status: str | None = None

    has_dependency: bool = False
    is_condition_for_count: int = 0

    obligation_code: str | None = None
    contract_phase: str | None = None
    trigger_category: str | None = None
    compliance_logic: str | None = None
    trigger_source: str | None = None
    internal_inputs: str | None = None
    external_inputs: str | None = None
    depends_on_clauses: str | None = None
    is_input_for_clauses: str | None = None
    deadline_type: str | None = None
    deadline_value: str | None = None
    deadline_text: str | None = None
    expected_output: str | None = None
    interpretive_notes: str | None = None

    pagina_contrato: int | None = None

    created_at: datetime
    updated_at: datetime


class ObligationCreateRequest(BaseModel):
    contract_id: int

    document_name: str | None = None
    item_number: str | None = None
    recurrence: str | None = None

    obligation_text: str
    observations: str | None = None
    responsible: str | None = None
    status: str = "pending"

    email_enabled: bool = False
    email_destino: str | None = None

    manual_reminder_at: datetime | None = None

    recurrence_mode: str | None = None
    recurrence_time: str | None = None
    recurrence_interval_days: int | None = None
    recurrence_weekday: int | None = None
    recurrence_day_of_month: int | None = None
    recurrence_month: int | None = None

    trigger_family: str | None = None
    trigger_type: str | None = None
    condition_raw: str | None = None
    condition_canonical: str | None = None
    condition_status: str | None = None
    condition_obligation_id: int | None = None
    contract_phase: str | None = None
    pagina_contrato: int | None = None


class ObligationStatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    obligation_id: int
    old_status: str | None = None
    new_status: str
    note: str | None = None
    changed_at: datetime


class ObligationDetailResponse(BaseModel):
    obligation: ObligationRead
    history: list[ObligationStatusHistoryRead]


class ObligationUpdateRequest(BaseModel):
    status: str | None = None
    observations: str | None = None
    note: str | None = None

    email_enabled: bool | None = None
    email_destino: str | None = None

    manual_reminder_at: datetime | None = None

    recurrence_mode: str | None = None
    recurrence_time: str | None = None
    recurrence_interval_days: int | None = None
    recurrence_weekday: int | None = None
    recurrence_day_of_month: int | None = None
    recurrence_month: int | None = None

    trigger_family: str | None = None
    trigger_type: str | None = None
    condition_raw: str | None = None
    condition_canonical: str | None = None
    condition_status: str | None = None
    contract_phase: str | None = None
    deadline: datetime | None = None
    pagina_contrato: int | None = None


class ObligationListResponse(BaseModel):
    items: list[ObligationRead]
    total: int
    skip: int
    limit: int


class ObligationUpdateResponse(BaseModel):
    obligation: ObligationRead
    history: list[ObligationStatusHistoryRead]
    activated_obligations: list[str] = []
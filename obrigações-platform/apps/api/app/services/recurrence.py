from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, time, timedelta

from app.models.obligation import Obligation


WEEKDAY_LABELS = [
    "segunda",
    "terça",
    "quarta",
    "quinta",
    "sexta",
    "sábado",
    "domingo",
]

MONTH_LABELS = [
    "",
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
]


def _clamp_day(year: int, month: int, day: int) -> int:
    return min(max(day, 1), monthrange(year, month)[1])


def _next_month(year: int, month: int) -> tuple[int, int]:
    if month == 12:
        return year + 1, 1
    return year, month + 1


def _parse_time(value: str | None) -> time:
    if not value:
        return time(8, 0)

    try:
        hour, minute = value.split(":")
        return time(int(hour), int(minute))
    except Exception:
        return time(8, 0)


def _combine(d: date, hhmm: str | None) -> datetime:
    return datetime.combine(d, _parse_time(hhmm))


def _base_date(obligation: Obligation, reference_date: date) -> date:
    if obligation.manual_reminder_at is not None:
        return obligation.manual_reminder_at.date()

    if obligation.manual_reminder_sent_at is not None:
        return obligation.manual_reminder_sent_at.date()

    return reference_date


def calculate_next_recurrence_at(
    obligation: Obligation,
    reference_datetime: datetime | None = None,
) -> datetime | None:
    reference_datetime = reference_datetime or datetime.now()

    mode = (obligation.recurrence_mode or "").strip().lower()
    if not mode:
        return None

    base = _base_date(obligation, reference_datetime.date())

    if mode == "manual_days":
        interval = obligation.recurrence_interval_days or 0
        if interval <= 0:
            return None

        candidate_date = base
        candidate = _combine(candidate_date, obligation.recurrence_time)

        while candidate <= reference_datetime:
            candidate_date += timedelta(days=interval)
            candidate = _combine(candidate_date, obligation.recurrence_time)

        return candidate

    if mode == "weekly":
        weekday = obligation.recurrence_weekday
        if weekday is None or weekday < 0 or weekday > 6:
            return None

        candidate_date = reference_datetime.date() + timedelta(
            days=(weekday - reference_datetime.weekday()) % 7
        )
        candidate = _combine(candidate_date, obligation.recurrence_time)

        while candidate <= reference_datetime or candidate.date() < base:
            candidate_date += timedelta(days=7)
            candidate = _combine(candidate_date, obligation.recurrence_time)

        return candidate

    if mode == "monthly":
        day = obligation.recurrence_day_of_month or base.day
        year, month = reference_datetime.year, reference_datetime.month

        while True:
            candidate_date = date(year, month, _clamp_day(year, month, day))
            candidate = _combine(candidate_date, obligation.recurrence_time)

            if candidate > reference_datetime and candidate.date() >= base:
                return candidate

            year, month = _next_month(year, month)

    if mode == "yearly":
        month = obligation.recurrence_month or base.month
        day = obligation.recurrence_day_of_month or base.day
        year = reference_datetime.year

        while True:
            candidate_date = date(year, month, _clamp_day(year, month, day))
            candidate = _combine(candidate_date, obligation.recurrence_time)

            if candidate > reference_datetime and candidate.date() >= base:
                return candidate

            year += 1

    return None


def calculate_next_reminder_at(
    obligation: Obligation,
    reference_datetime: datetime | None = None,
) -> datetime | None:
    reference_datetime = reference_datetime or datetime.now()

    manual = obligation.manual_reminder_at
    recurrence = calculate_next_recurrence_at(
        obligation,
        reference_datetime=reference_datetime,
    )

    valid_candidates: list[datetime] = []

    if manual is not None and manual > reference_datetime:
        valid_candidates.append(manual)

    if recurrence is not None and recurrence > reference_datetime:
        valid_candidates.append(recurrence)

    if not valid_candidates:
        return None

    return min(valid_candidates)


def describe_recurrence(obligation: Obligation) -> str:
    mode = (obligation.recurrence_mode or "").strip().lower()

    if mode == "weekly":
        weekday = obligation.recurrence_weekday
        if weekday is None or weekday < 0 or weekday > 6:
            return "Semanal"
        hora = obligation.recurrence_time or "08:00"
        return f"Semanal — toda {WEEKDAY_LABELS[weekday]} às {hora}"

    if mode == "monthly":
        day = obligation.recurrence_day_of_month or "?"
        hora = obligation.recurrence_time or "08:00"
        return f"Mensal — dia {day} às {hora}"

    if mode == "yearly":
        month = obligation.recurrence_month or 1
        day = obligation.recurrence_day_of_month or "?"
        hora = obligation.recurrence_time or "08:00"
        return f"Anual — {day} de {MONTH_LABELS[month]} às {hora}"

    if mode == "manual_days":
        interval = obligation.recurrence_interval_days or "?"
        hora = obligation.recurrence_time or "08:00"
        return f"Manual — a cada {interval} dias às {hora}"

    return "Sem recorrência"


def should_send_now(obligation: Obligation, now: datetime | None = None) -> bool:
    now = now or datetime.now()

    if not obligation.email_enabled:
        return False

    if not obligation.email_destino:
        return False

    if obligation.status == "completed":
        return False

    if (
        (obligation.trigger_family or "").strip().lower() == "eventual"
        and (obligation.condition_status or "").strip().lower() != "cumprida"
    ):
        return False

    next_reminder = obligation.next_reminder_at
    if next_reminder is None:
        return False

    if (
        obligation.manual_reminder_sent_at
        and obligation.manual_reminder_sent_at.date() == now.date()
    ):
        return False

    return next_reminder <= now
from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.db.session import SessionLocal
from app.services.reminder_runner import (
    resetar_obrigacoes_continuas,
    rodar_lembretes_continuos,
    rodar_lembretes_email,
)

logger = logging.getLogger(__name__)

_scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")


def _run_email_job() -> None:
    db = SessionLocal()
    try:
        enviados = rodar_lembretes_email(db)
        if enviados:
            logger.info("Scheduler de emails: %s lembrete(s) enviado(s).", enviados)
    except Exception:
        logger.exception("Erro ao executar o scheduler de emails.")
    finally:
        db.close()


def _run_monthly_job() -> None:
    db = SessionLocal()
    try:
        resetados = resetar_obrigacoes_continuas(db)
        if resetados:
            logger.info("Job mensal: %s obrigação(ões) reiniciada(s).", resetados)
        enviados = rodar_lembretes_continuos(db)
        if enviados:
            logger.info("Job mensal: lembrete enviado ao escritório.")
    except Exception:
        logger.exception("Erro ao executar o job mensal.")
    finally:
        db.close()


def start_email_scheduler() -> None:
    if _scheduler.running:
        return

    _scheduler.add_job(
        _run_email_job,
        trigger=IntervalTrigger(seconds=30),
        id="email_reminders_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=60,
    )

    _scheduler.add_job(
        _run_monthly_job,
        trigger=CronTrigger(day=1, hour=8, minute=0, timezone="America/Sao_Paulo"),
        id="monthly_reminders_job",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600,
    )

    _scheduler.start()
    logger.info("Scheduler de emails iniciado.")


def stop_email_scheduler() -> None:
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler de emails parado.")
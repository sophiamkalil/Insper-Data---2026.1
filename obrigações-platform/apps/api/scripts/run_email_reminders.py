import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from app.db.session import SessionLocal
from app.services.reminder_runner import rodar_lembretes_email


def main() -> None:
    db = SessionLocal()

    try:
        enviados = rodar_lembretes_email(db)
        print(f"{enviados} lembrete(s) enviado(s).")

    finally:
        db.close()


if __name__ == "__main__":
    main()
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.db.base import Base
from app.db.session import engine
from app.models import contract, obligation, status_history  # noqa: F401
from app.services.scheduler import start_email_scheduler, stop_email_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_email_scheduler()
    yield
    stop_email_scheduler()


app = FastAPI(
    title="Obrigações Platform API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
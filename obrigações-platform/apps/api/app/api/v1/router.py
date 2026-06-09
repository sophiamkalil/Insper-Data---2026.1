from fastapi import APIRouter

from app.api.v1.endpoints.contracts import router as contracts_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.imports import router as imports_router
from app.api.v1.endpoints.obligation_detail import router as obligation_detail_router
from app.api.v1.endpoints.obligations import router as obligations_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(contracts_router, prefix="/contracts", tags=["Contracts"])
api_router.include_router(imports_router, prefix="/imports", tags=["Imports"])
api_router.include_router(obligations_router, prefix="/obligations", tags=["Obligations"])
api_router.include_router(
    obligation_detail_router,
    prefix="/obligations",
    tags=["Obligation Detail"],
)
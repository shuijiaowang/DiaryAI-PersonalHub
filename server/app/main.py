from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import settings
from app.core.errors import DomainError
from app.core.logging import logger, setup_logging
from app.db.session import SessionLocal
from app.modules.registry import load_builtins, sync_to_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info(f"starting {settings.APP_NAME} v{settings.APP_VERSION} env={settings.APP_ENV}")

    # Register all builtin modules into the in-memory registry, then sync to DB.
    load_builtins()
    db = SessionLocal()
    try:
        sync_to_db(db)
    finally:
        db.close()
    yield
    logger.info("shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.APP_DEBUG,
    lifespan=lifespan,
)

if settings.CORS_ALLOW_ALL:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.exception_handler(DomainError)
async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": settings.APP_VERSION}


app.include_router(api_router)

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

import app.models  # noqa: F401  (registers tables)
from app.api.routes import admin_tickets, auth, books, stats, tickets
from app.core.config import settings
from app.core.errors import AppError
from app.db.base import Base
from app.db.session import engine

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)  # creates tables if missing
    yield


app = FastAPI(title="BookLeaf Author Support Portal", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _error(status: int, code: str, message: str, details=None):
    body = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return JSONResponse(status_code=status, content=body)


@app.exception_handler(AppError)
async def app_error_handler(_: Request, exc: AppError):
    return _error(exc.status_code, exc.code, exc.message)


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError):
    details = [{"field": ".".join(str(p) for p in e["loc"][1:]), "message": e["msg"]} for e in exc.errors()]
    return _error(422, "validation_error", "Some fields are invalid.", details)


@app.exception_handler(StarletteHTTPException)
async def http_handler(_: Request, exc: StarletteHTTPException):
    return _error(exc.status_code, "http_error", str(exc.detail))


@app.exception_handler(Exception)
async def unhandled_handler(_: Request, exc: Exception):
    log.exception("Unhandled error", exc_info=exc)
    return _error(500, "server_error", "Something went wrong on our side. Please try again.")


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}

@app.get("/", tags=["System"])
def root():
    return {"service": "BookLeaf API", "docs": "/docs"}


for r in (auth.router, books.router, tickets.router, admin_tickets.router, stats.router):
    app.include_router(r)
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import time
import logging

from app.database.session import init_db
from app.routes import candidates, evaluations

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NexAltis Candidate Evaluation System",
    description=(
        "Internal system for managing candidates, recording interview evaluations, "
        "and ranking candidates by weighted score.\n\n"
        "**Auth:** pass `X-API-Key` header on every request.\n\n"
        "**Scoring:** `Technical×0.30 + Problem Solving×0.25 + Communication×0.20 + Ownership×0.25`"
    ),
    version="1.0.0",
    contact={"name": "NexAltis Technologies LLP", "email": "contact@nexaltistech.com"},
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def timing_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    response.headers["X-Process-Time-Ms"] = f"{(time.time() - start) * 1000:.2f}"
    return response


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": " → ".join(str(loc) for loc in e["loc"]), "message": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        content={"error": "Validation failed", "details": errors})


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                        content={"error": "Database conflict", "detail": str(exc.orig)})


app.include_router(candidates.router)
app.include_router(evaluations.router)


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("Database ready.")


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "docs": "/docs", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "version": "1.0.0"}

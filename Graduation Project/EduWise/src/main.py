"""FastAPI application entry point for the EduWise platform."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.backend.api.v1.automation_endpoints import router as automation_router

app = FastAPI(
    title="EduWise Platform API",
    description="Academic risk and n8n automation integrations.",
    version="1.1.0",
)


@app.exception_handler(RequestValidationError)
async def validation_error(_request: Request, error: RequestValidationError) -> JSONResponse:
    details = [{"loc": item["loc"], "type": item["type"]} for item in error.errors()]
    return JSONResponse(status_code=422, content={"detail": details})


app.include_router(automation_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "EduWise API"}

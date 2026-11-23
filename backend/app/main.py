from typing import Literal, TypedDict

from fastapi import FastAPI

from app.core.config import get_settings


class ApplicationInfo(TypedDict):
    name: str
    description: str
    status: Literal["running"]


class HealthStatus(TypedDict):
    status: Literal["healthy"]


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)


@app.get("/", tags=["application"])
def read_root() -> ApplicationInfo:
    return ApplicationInfo(
        name=settings.app_name,
        description="LaunchShield AI security assessment platform",
        status="running",
    )


@app.get("/health", tags=["application"])
def health_check() -> HealthStatus:
    return HealthStatus(status="healthy")

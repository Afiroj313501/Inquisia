from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.assessments import router as assessments_router
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.interests import router as interests_router
from app.api.v1.papers import router as papers_router
from app.api.v1.profile import router as profile_router
from app.api.v1.recommendations import router as recommendations_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(health_router, prefix=settings.api_v1_prefix)
    application.include_router(auth_router, prefix=settings.api_v1_prefix)
    application.include_router(profile_router, prefix=settings.api_v1_prefix)
    application.include_router(assessments_router, prefix=settings.api_v1_prefix)
    application.include_router(interests_router, prefix=settings.api_v1_prefix)
    application.include_router(recommendations_router, prefix=settings.api_v1_prefix)
    application.include_router(papers_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()

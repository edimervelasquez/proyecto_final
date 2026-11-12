import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from backend.bootstrap import initialize_database
from backend.database import engine, get_db
from backend.middlewares.request_middleware import RequestMiddleware
from backend.routes.auth_routes import router as auth_router
from backend.routes.insumos_routes import router as insumos_router
from backend.routes.calidad_routes import router as calidad_router
from backend.routes.dashboard_routes import router as dashboard_router
from backend.routes.produccion_routes import router as produccion_router
from backend.routes.comercial_routes import router as comercial_router
from backend.routes.merma_routes import router as merma_router
from backend.security import get_secret_key


def create_app(database_engine: Engine = engine) -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        get_secret_key()
        initialize_database(database_engine)
        yield

    application = FastAPI(
        title="API de Gestión",
        description="Migración del sistema a FastAPI",
        version="1.0.0",
        lifespan=lifespan,
    )
    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=database_engine,
    )
    application.state.session_factory = session_factory

    def get_application_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    application.dependency_overrides[get_db] = get_application_db
    application.add_middleware(RequestMiddleware)
    allowed_origins = [
        origin.strip()
        for origin in os.environ.get(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    ]
    if not allowed_origins or "*" in allowed_origins:
        raise ValueError(
            "CORS_ALLOWED_ORIGINS debe contener orígenes explícitos, no '*'."
        )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(auth_router, prefix="/api/auth", tags=["Autenticación"])
    application.include_router(
        insumos_router,
        prefix="/api",
        tags=["Insumos y Fichas Técnicas"],
    )
    application.include_router(calidad_router, prefix="/api")
    application.include_router(dashboard_router, prefix="/api")
    application.include_router(produccion_router, prefix="/api")
    application.include_router(merma_router, prefix="/api")
    application.include_router(comercial_router, prefix="/api")

    @application.get("/")
    def ruta_raiz():
        return {"mensaje": "El servidor FastAPI está funcionando correctamente"}

    return application


app = create_app()
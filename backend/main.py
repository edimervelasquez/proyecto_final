from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.middlewares.request_middleware import RequestMiddleware
from backend.routes.auth_routes import router as auth_router
from backend.routes.insumos_routes import router as insumos_router  # <-- 1. Importas el router de insumos
from backend.routes.calidad_routes import router as calidad_router
from backend.routes.dashboard_routes import router as dashboard_router
from backend.routes.produccion_routes import router as produccion_router

# --- 1. Importamos la base de datos y los modelos ---
from backend.database import engine, Base
from backend.models import models  # Esto hace que SQLAlchemy lea todas tus tablas

# --- 2. Creamos las tablas en MySQL automáticamente si no existen ---
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Gestión",
    description="Migración del sistema a FastAPI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestMiddleware)

app.include_router(auth_router, prefix="/api/auth", tags=["Autenticación"])
app.include_router(insumos_router, prefix="/api", tags=["Insumos y Fichas Técnicas"])  # <-- 2. Incluyes el router en la app
app.include_router(calidad_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(produccion_router, prefix="/api")

@app.get("/")
def ruta_raiz():
    return {"mensaje": "El servidor FastAPI está funcionando correctamente"}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.auth import router as auth_router  # <-- Ruta absoluta agregada

app = FastAPI(
    title="API de Gestión",
    description="Migración del sistema a FastAPI",
    version="1.0.0"
)

# Configuración de CORS para permitir que el frontend haga peticiones
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Autenticación"])

@app.get("/")
def ruta_raiz():
    return {"mensaje": "El servidor FastAPI está funcionando correctamente"}
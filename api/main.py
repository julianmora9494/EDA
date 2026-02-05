"""
FastAPI main application: EDA Dashboard API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging

from .routes import upload, profile, columns, export, data

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Crear directorios necesarios
Path("data").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)

logger.info("EDA Dashboard API starting...")

# Crear app
app = FastAPI(
    title="EDA Dashboard API",
    description="API para análisis exploratorio automatizado de datos Excel",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS (para permitir requests desde Streamlit en localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(upload.router)
app.include_router(profile.router)
app.include_router(columns.router)
app.include_router(export.router)
app.include_router(data.router)


@app.get("/")
def root():
    """
    Root endpoint: información de la API.
    """
    return {
        "name": "EDA Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "upload": "POST /datasets/upload",
            "profile": "GET /datasets/{id}/profile",
            "columns": "GET /datasets/{id}/columns",
            "column_summary": "GET /datasets/{id}/columns/{name}/summary",
            "export_profile": "GET /datasets/{id}/export/profile",
            "export_data": "GET /datasets/{id}/export/data",
            "list": "GET /datasets/list",
            "delete": "DELETE /datasets/{id}",
        }
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

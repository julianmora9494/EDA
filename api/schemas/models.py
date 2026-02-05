"""
Pydantic models para request/response de la API.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UploadResponse(BaseModel):
    """Respuesta al subir un archivo."""
    dataset_id: str
    filename: str
    file_size_mb: float
    sheet_names: List[str]
    selected_sheet: Optional[str] = None
    message: str


class ProfileResponse(BaseModel):
    """Respuesta con el perfil completo."""
    dataset_id: str
    sheet_name: str
    profiled_at: str
    profile_duration_seconds: float
    overview: Dict[str, Any]
    columns: List[Dict[str, Any]]
    column_roles: Dict[str, str]
    quality: Dict[str, Any]
    associations: Dict[str, Any]
    insights: List[Dict[str, Any]]
    preview: Dict[str, List[Dict[str, Any]]]
    sampled: bool


class ColumnListResponse(BaseModel):
    """Respuesta con lista de columnas."""
    dataset_id: str
    n_columns: int
    columns: List[Dict[str, Any]]


class ColumnSummaryResponse(BaseModel):
    """Respuesta con resumen de una columna."""
    column_name: str
    role: str
    metadata: Dict[str, Any]


class ErrorResponse(BaseModel):
    """Respuesta de error."""
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

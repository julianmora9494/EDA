"""
Columns route: endpoints para análisis de columnas individuales.
"""
from fastapi import APIRouter, HTTPException

from ..services.profiler import ProfilerService
from ..schemas.models import ColumnListResponse, ColumnSummaryResponse, ErrorResponse


router = APIRouter(prefix="/datasets", tags=["columns"])

profiler = ProfilerService(data_dir="data")


@router.get("/{dataset_id}/columns", response_model=ColumnListResponse)
def get_columns(dataset_id: str):
    """
    Obtiene lista de columnas con metadata básica.
    
    - **dataset_id**: ID del dataset
    
    Returns:
        Lista de columnas del dataset
    """
    try:
        # Obtener perfil del cache
        profile = profiler.cache_manager.load_profile(dataset_id)
        
        if profile is None:
            raise HTTPException(
                status_code=404,
                detail=f"Perfil no encontrado para dataset {dataset_id}. Use /profile primero."
            )
        
        columns = profile.get("columns", [])
        
        return ColumnListResponse(
            dataset_id=dataset_id,
            n_columns=len(columns),
            columns=columns
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener columnas: {str(e)}")


@router.get("/{dataset_id}/columns/{column_name:path}/summary", response_model=ColumnSummaryResponse)
def get_column_summary(dataset_id: str, column_name: str):
    """
    Obtiene resumen detallado de una columna específica.
    
    - **dataset_id**: ID del dataset
    - **column_name**: Nombre de la columna (puede contener espacios y caracteres especiales)
    
    Returns:
        Resumen detallado de la columna
    """
    try:
        from urllib.parse import unquote
        # Decodificar el nombre de columna
        column_name = unquote(column_name)
        
        metadata = profiler.get_column_detail(dataset_id, column_name)
        
        return ColumnSummaryResponse(
            column_name=column_name,
            role=metadata.get("role", "unknown"),
            metadata=metadata
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener resumen de columna: {str(e)}")

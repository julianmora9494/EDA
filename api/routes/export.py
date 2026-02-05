"""
Export route: endpoints para exportar perfiles y datos.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import json

from ..services.profiler import ProfilerService


router = APIRouter(prefix="/datasets", tags=["export"])

profiler = ProfilerService(data_dir="data")


@router.get("/{dataset_id}/export/profile")
def export_profile_json(dataset_id: str):
    """
    Exporta el perfil EDA completo en formato JSON.
    
    - **dataset_id**: ID del dataset
    
    Returns:
        Archivo JSON con el perfil
    """
    try:
        profile = profiler.cache_manager.load_profile(dataset_id)
        
        if profile is None:
            raise HTTPException(
                status_code=404,
                detail=f"Perfil no encontrado para dataset {dataset_id}"
            )
        
        # Retornar como descarga
        filename = f"profile_{dataset_id}.json"
        
        return JSONResponse(
            content=profile,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar perfil: {str(e)}")


@router.get("/{dataset_id}/export/data")
def export_data(dataset_id: str, format: str = "csv"):
    """
    Exporta los datos del dataset.
    
    - **dataset_id**: ID del dataset
    - **format**: Formato de exportación ('csv' o 'parquet')
    
    Returns:
        Archivo con los datos
    """
    try:
        df = profiler.file_handler.load_dataframe(dataset_id)
        
        if df is None:
            raise HTTPException(
                status_code=404,
                detail=f"Datos no encontrados para dataset {dataset_id}"
            )
        
        # Guardar temporalmente
        if format == "csv":
            file_path = Path("data") / f"export_{dataset_id}.csv"
            df.to_csv(file_path, index=False)
            media_type = "text/csv"
        elif format == "parquet":
            file_path = Path("data") / f"export_{dataset_id}.parquet"
            df.to_parquet(file_path, index=False)
            media_type = "application/octet-stream"
        else:
            raise HTTPException(status_code=400, detail=f"Formato no soportado: {format}")
        
        return FileResponse(
            path=file_path,
            media_type=media_type,
            filename=file_path.name
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar datos: {str(e)}")

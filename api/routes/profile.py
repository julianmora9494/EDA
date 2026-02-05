"""
Profile route: endpoints relacionados con perfiles EDA.
"""
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path

from ..services.profiler import ProfilerService
from ..schemas.models import ProfileResponse, ErrorResponse


router = APIRouter(prefix="/datasets", tags=["profile"])

profiler = ProfilerService(data_dir="data")


@router.get("/{dataset_id}/profile", response_model=ProfileResponse)
def get_profile(
    dataset_id: str,
    sheet_name: str = Query(default=None, description="Nombre de hoja (opcional)"),
    force_refresh: bool = Query(default=False, description="Forzar regeneración")
):
    """
    Obtiene o genera el perfil EDA completo de un dataset.
    
    - **dataset_id**: ID del dataset
    - **sheet_name**: Hoja específica (None = primera hoja)
    - **force_refresh**: Regenerar perfil aunque exista en cache
    
    Returns:
        Perfil EDA completo
    """
    try:
        # Buscar archivo (Excel o CSV)
        data_dir = Path("data")
        files = (
            list(data_dir.glob(f"{dataset_id}_*.xlsx")) + 
            list(data_dir.glob(f"{dataset_id}_*.xls")) +
            list(data_dir.glob(f"{dataset_id}_*.csv"))
        )
        
        if not files:
            raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} no encontrado")
        
        file_path = files[0]
        
        profile = profiler.get_or_create_profile(
            dataset_id=dataset_id,
            file_path=file_path,
            sheet_name=sheet_name,
            force_refresh=force_refresh
        )
        
        return ProfileResponse(**profile)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar perfil: {str(e)}")


@router.get("/list")
def list_datasets():
    """
    Lista todos los datasets disponibles.
    
    Returns:
        Lista de datasets con metadata
    """
    try:
        return {"datasets": profiler.list_datasets()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al listar datasets: {str(e)}")


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: str):
    """
    Elimina un dataset y su perfil.
    
    - **dataset_id**: ID del dataset a eliminar
    
    Returns:
        Mensaje de confirmación
    """
    try:
        profiler.delete_dataset(dataset_id)
        return {"message": f"Dataset {dataset_id} eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar dataset: {str(e)}")

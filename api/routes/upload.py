"""
Upload route: maneja la subida de archivos Excel.
"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from pathlib import Path

from ..services.file_handler import FileHandler
from ..services.profiler import ProfilerService
from ..schemas.models import UploadResponse, ErrorResponse


router = APIRouter(prefix="/datasets", tags=["upload"])

file_handler = FileHandler(data_dir="data")
profiler = ProfilerService(data_dir="data")


@router.post("/upload", response_model=UploadResponse)
async def upload_excel(
    file: UploadFile = File(...),
    auto_profile: bool = Query(default=True, description="Generar perfil automáticamente")
):
    """
    Sube un archivo Excel o CSV y opcionalmente genera el perfil EDA.
    
    - **file**: Archivo Excel (.xlsx, .xls) o CSV (.csv)
    - **auto_profile**: Si True, genera perfil automáticamente
    
    Returns:
        Información del archivo subido + hojas disponibles (solo para Excel)
    """
    # Validar extensión
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=400,
            detail="Formato no soportado. Use .xlsx, .xls o .csv"
        )
    
    try:
        # Leer archivo
        file_bytes = await file.read()
        
        # Guardar
        dataset_id, file_path = file_handler.save_uploaded_file(file_bytes, file.filename)
        
        # Obtener hojas (solo para Excel)
        if file.filename.endswith(('.xlsx', '.xls')):
            sheet_names = file_handler.get_sheet_names(file_path)
            selected_sheet = sheet_names[0] if sheet_names else None
        else:  # CSV
            sheet_names = None
            selected_sheet = None
        
        # Info del archivo
        file_info = file_handler.get_file_info(file_path)
        
        # Si auto_profile, generar perfil con primera hoja (o el CSV completo)
        if auto_profile:
            if sheet_names:
                # Excel: usar primera hoja
                profiler.get_or_create_profile(
                    dataset_id=dataset_id,
                    file_path=file_path,
                    sheet_name=sheet_names[0]
                )
            else:
                # CSV: sin nombre de hoja
                profiler.get_or_create_profile(
                    dataset_id=dataset_id,
                    file_path=file_path,
                    sheet_name=None
                )
        
        return UploadResponse(
            dataset_id=dataset_id,
            filename=file.filename,
            file_size_mb=file_info["size_mb"],
            sheet_names=sheet_names if sheet_names else ["CSV"],
            selected_sheet=selected_sheet if selected_sheet else "CSV",
            message=f"Archivo subido exitosamente. {'Perfil generado.' if auto_profile else 'Use /profile para generar perfil.'}"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar archivo: {str(e)}")

"""
Data route: endpoints para obtener datos del dataset (para visualizaciones)
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import pandas as pd
import numpy as np

from ..services.profiler import ProfilerService


router = APIRouter(prefix="/datasets", tags=["data"])

profiler = ProfilerService(data_dir="data")


@router.get("/{dataset_id}/data/column")
def get_column_data(
    dataset_id: str,
    column_name: str = Query(..., description="Nombre de la columna"),
    limit: Optional[int] = Query(None, description="Límite de registros")
):
    """
    Obtiene los datos de una columna específica.
    
    - **dataset_id**: ID del dataset
    - **column_name**: Nombre de la columna
    - **limit**: Límite de registros (None = todos)
    
    Returns:
        Array con los valores de la columna
    """
    try:
        df = profiler.file_handler.load_dataframe(dataset_id)
        
        if df is None:
            raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} no encontrado")
        
        if column_name not in df.columns:
            raise HTTPException(status_code=404, detail=f"Columna '{column_name}' no encontrada")
        
        # Obtener datos
        data = df[column_name]
        
        if limit:
            data = data.head(limit)
        
        # Convertir a lista (manejar NaN y tipos numpy)
        values = []
        for val in data:
            if pd.isna(val):
                values.append(None)
            elif isinstance(val, (np.integer, np.floating)):
                values.append(float(val))
            else:
                values.append(val)
        
        return {
            "column_name": column_name,
            "n_values": len(values),
            "values": values
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")


@router.get("/{dataset_id}/data/columns")
def get_multiple_columns_data(
    dataset_id: str,
    columns: str = Query(..., description="Nombres de columnas separados por coma"),
    limit: Optional[int] = Query(None, description="Límite de registros")
):
    """
    Obtiene datos de múltiples columnas.
    
    - **dataset_id**: ID del dataset
    - **columns**: Nombres de columnas separados por coma
    - **limit**: Límite de registros
    
    Returns:
        Dict con arrays por columna
    """
    try:
        import pandas as pd
        import numpy as np
        
        df = profiler.file_handler.load_dataframe(dataset_id)
        
        if df is None:
            raise HTTPException(status_code=404, detail=f"Dataset {dataset_id} no encontrado")
        
        column_list = [c.strip() for c in columns.split(',')]
        
        # Validar que existan
        missing_cols = [c for c in column_list if c not in df.columns]
        if missing_cols:
            raise HTTPException(status_code=404, detail=f"Columnas no encontradas: {', '.join(missing_cols)}")
        
        # Obtener datos
        df_subset = df[column_list]
        
        if limit:
            df_subset = df_subset.head(limit)
        
        # Convertir a dict
        result = {}
        for col in column_list:
            values = []
            for val in df_subset[col]:
                if pd.isna(val):
                    values.append(None)
                elif isinstance(val, (np.integer, np.floating)):
                    values.append(float(val))
                else:
                    values.append(str(val))
            result[col] = values
        
        return {
            "n_rows": len(df_subset),
            "columns": column_list,
            "data": result
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener datos: {str(e)}")

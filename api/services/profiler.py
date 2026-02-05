"""
Profiler service: orquesta el perfilamiento EDA usando el motor EDA.
"""
from pathlib import Path
from typing import Dict, Optional
import pandas as pd

from .file_handler import FileHandler
from .cache_manager import CacheManager
from eda.profiling import profile_dataset, get_column_summary


class ProfilerService:
    """Servicio de perfilamiento que coordina file handler, cache y EDA engine."""
    
    def __init__(self, data_dir: str = "data"):
        self.file_handler = FileHandler(data_dir=data_dir)
        self.cache_manager = CacheManager(cache_dir=data_dir)
    
    def get_or_create_profile(
        self,
        dataset_id: str,
        file_path: Path,
        sheet_name: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict:
        """
        Obtiene perfil del cache o lo genera si no existe.
        
        Args:
            dataset_id: ID del dataset
            file_path: Ruta al archivo Excel o CSV
            sheet_name: Nombre de hoja (None = primera para Excel o CSV completo)
            force_refresh: Forzar regeneración
            
        Returns:
            Diccionario con el perfil
        """
        # Verificar cache
        if not force_refresh and self.cache_manager.profile_exists(dataset_id):
            profile = self.cache_manager.load_profile(dataset_id)
            if profile:
                profile["from_cache"] = True
                return profile
        
        # Generar nuevo perfil
        df, used_sheet = self.file_handler.load_excel(file_path, sheet_name)
        
        profile = profile_dataset(
            df=df,
            dataset_id=dataset_id,
            sheet_name=used_sheet,
            sample_threshold=50_000
        )
        
        # Guardar en cache
        self.cache_manager.save_profile(dataset_id, profile)
        
        # Guardar DataFrame procesado
        self.file_handler.save_dataframe(df, dataset_id, format="parquet")
        
        profile["from_cache"] = False
        return profile
    
    def get_column_detail(self, dataset_id: str, column_name: str) -> Dict:
        """
        Obtiene resumen detallado de una columna.
        
        Args:
            dataset_id: ID del dataset
            column_name: Nombre de la columna
            
        Returns:
            Diccionario con resumen de la columna
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # Cargar DataFrame
            logger.info(f"Loading dataframe for dataset_id: {dataset_id}")
            df = self.file_handler.load_dataframe(dataset_id)
            
            if df is None:
                logger.error(f"Dataset {dataset_id} not found")
                raise ValueError(f"Dataset {dataset_id} no encontrado")
            
            logger.info(f"DataFrame loaded. Shape: {df.shape}. Looking for column: '{column_name}'")
            logger.info(f"Available columns: {list(df.columns)}")
            
            if column_name not in df.columns:
                logger.error(f"Column '{column_name}' not found. Available: {list(df.columns)}")
                raise ValueError(f"Columna '{column_name}' no encontrada en dataset")
            
            logger.info(f"Getting summary for column '{column_name}'")
            result = get_column_summary(df, column_name)
            logger.info(f"Summary generated successfully for '{column_name}'")
            return result
            
        except Exception as e:
            logger.exception(f"Error getting column detail for '{column_name}': {str(e)}")
            raise
    
    def list_datasets(self) -> list:
        """
        Lista datasets disponibles en cache.
        
        Returns:
            Lista de datasets cacheados
        """
        return self.cache_manager.list_cached_profiles()
    
    def delete_dataset(self, dataset_id: str):
        """
        Elimina dataset y su perfil.
        
        Args:
            dataset_id: ID del dataset
        """
        self.cache_manager.delete_profile(dataset_id)
        self.file_handler.cleanup(dataset_id)

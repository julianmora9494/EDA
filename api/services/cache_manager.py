"""
Cache manager: persiste y recupera perfiles EDA en JSON.
"""
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime


class CacheManager:
    """Maneja el cache de perfiles EDA."""
    
    def __init__(self, cache_dir: str = "data"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def save_profile(self, dataset_id: str, profile: Dict) -> Path:
        """
        Guarda perfil EDA en JSON.
        
        Args:
            dataset_id: ID del dataset
            profile: Diccionario con el perfil completo
            
        Returns:
            Path al archivo guardado
        """
        # Añadir metadata de cache
        profile["_cache_metadata"] = {
            "dataset_id": dataset_id,
            "cached_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        file_path = self.cache_dir / f"{dataset_id}_profile.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False, default=str)
        
        return file_path
    
    def load_profile(self, dataset_id: str) -> Optional[Dict]:
        """
        Carga perfil EDA desde JSON.
        
        Args:
            dataset_id: ID del dataset
            
        Returns:
            Diccionario con el perfil o None si no existe
        """
        file_path = self.cache_dir / f"{dataset_id}_profile.json"
        
        if not file_path.exists():
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading profile for {dataset_id}: {e}")
            return None
    
    def profile_exists(self, dataset_id: str) -> bool:
        """
        Verifica si existe un perfil cacheado.
        
        Args:
            dataset_id: ID del dataset
            
        Returns:
            True si existe el perfil
        """
        file_path = self.cache_dir / f"{dataset_id}_profile.json"
        return file_path.exists()
    
    def delete_profile(self, dataset_id: str):
        """
        Elimina perfil cacheado.
        
        Args:
            dataset_id: ID del dataset
        """
        file_path = self.cache_dir / f"{dataset_id}_profile.json"
        if file_path.exists():
            file_path.unlink()
    
    def list_cached_profiles(self) -> list:
        """
        Lista todos los perfiles cacheados.
        
        Returns:
            Lista de dataset_ids con perfiles disponibles
        """
        profiles = []
        for file_path in self.cache_dir.glob("*_profile.json"):
            dataset_id = file_path.stem.replace("_profile", "")
            profiles.append({
                "dataset_id": dataset_id,
                "file": file_path.name,
                "size_kb": round(file_path.stat().st_size / 1024, 2),
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
        return profiles

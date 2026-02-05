"""
Sampling strategies: muestreo inteligente para datasets grandes.
"""
import pandas as pd
import numpy as np
from typing import Optional


def get_sample(
    df: pd.DataFrame,
    threshold: int = 50_000,
    sample_size: Optional[int] = None,
    random_state: int = 42
) -> pd.DataFrame:
    """
    Retorna muestra estratégica si el dataset es grande.
    
    Args:
        df: DataFrame original
        threshold: Si filas > threshold, muestrear
        sample_size: Tamaño objetivo de muestra (None = automático)
        random_state: Seed para reproducibilidad
        
    Returns:
        DataFrame (muestra o completo)
    """
    n_rows = len(df)
    
    if n_rows <= threshold:
        return df
    
    # Tamaño de muestra automático
    if sample_size is None:
        sample_size = min(threshold, n_rows)
    
    # Sampling estratificado si hay columnas categóricas obvias
    # (simple random sample por ahora)
    return df.sample(n=sample_size, random_state=random_state)


def should_sample(n_rows: int, threshold: int = 50_000) -> bool:
    """
    Determina si se debe muestrear.
    
    Args:
        n_rows: Número de filas
        threshold: Umbral de muestreo
        
    Returns:
        True si se debe muestrear
    """
    return n_rows > threshold

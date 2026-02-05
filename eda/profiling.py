"""
Profiling engine: orquesta el análisis EDA completo.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

from .typing import infer_variable_role, get_column_metadata
from .quality import check_data_quality, generate_insights
from .associations import compute_all_associations
from .sampling import get_sample, should_sample


def profile_dataset(
    df: pd.DataFrame,
    dataset_id: str,
    sheet_name: str,
    sample_threshold: int = 50_000
) -> Dict:
    """
    Genera perfil EDA completo del dataset.
    
    Args:
        df: DataFrame a perfilar
        dataset_id: ID único del dataset
        sheet_name: Nombre de la hoja
        sample_threshold: Umbral para muestreo
        
    Returns:
        Diccionario con el perfil completo
    """
    profile_start = datetime.now()
    
    # 1. Overview global
    overview = _compute_overview(df)
    
    # 2. Inferir tipos y obtener metadata por columna
    column_profiles = []
    column_roles = {}
    
    for col in df.columns:
        role = infer_variable_role(df[col], len(df))
        metadata = get_column_metadata(df[col], role)
        
        # Scoring de relevancia
        metadata["relevance_score"] = _compute_relevance_score(df[col], role, metadata)
        
        column_profiles.append(metadata)
        column_roles[col] = role
    
    # Ordenar por relevancia
    column_profiles_sorted = sorted(column_profiles, key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    # 3. Calidad de datos
    quality_report = check_data_quality(df)
    
    # 4. Asociaciones (usar muestra si es necesario)
    df_sample = get_sample(df, threshold=sample_threshold)
    associations = compute_all_associations(df_sample, column_roles)
    
    # 5. Generar insights
    insights = generate_insights(df, quality_report, column_profiles)
    
    # 6. Preview de datos
    preview = {
        "head": df.head(5).to_dict(orient="records"),
        "tail": df.tail(5).to_dict(orient="records"),
    }
    
    # Construir perfil completo
    profile = {
        "dataset_id": dataset_id,
        "sheet_name": sheet_name,
        "profiled_at": datetime.now().isoformat(),
        "profile_duration_seconds": (datetime.now() - profile_start).total_seconds(),
        "overview": overview,
        "columns": column_profiles_sorted,
        "column_roles": column_roles,
        "quality": quality_report,
        "associations": associations,
        "insights": insights,
        "preview": preview,
        "sampled": should_sample(len(df), sample_threshold),
    }
    
    return profile


def _compute_overview(df: pd.DataFrame) -> Dict:
    """
    Calcula métricas globales del dataset.
    
    Args:
        df: DataFrame
        
    Returns:
        Diccionario con overview
    """
    n_rows, n_cols = df.shape
    memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    
    # Conteo por tipos
    types_count = {}
    for col in df.columns:
        dtype_str = str(df[col].dtype)
        types_count[dtype_str] = types_count.get(dtype_str, 0) + 1
    
    # Duplicados
    n_duplicates = df.duplicated().sum()
    
    return {
        "n_rows": n_rows,
        "n_columns": n_cols,
        "n_cells": n_rows * n_cols,
        "memory_mb": round(memory_mb, 2),
        "n_duplicate_rows": int(n_duplicates),
        "pct_duplicate_rows": round((n_duplicates / n_rows) * 100, 2) if n_rows > 0 else 0,
        "dtypes_count": types_count,
    }


def _compute_relevance_score(series: pd.Series, role: str, metadata: Dict) -> float:
    """
    Calcula score de relevancia para priorizar variables en visualizaciones.
    
    Args:
        series: Serie de pandas
        role: Rol de la variable
        metadata: Metadata ya calculada
        
    Returns:
        Score de relevancia (0-100)
    """
    score = 50.0  # Base
    
    # Penalizar missing
    pct_missing = metadata.get("pct_missing", 0)
    score -= pct_missing * 0.3  # Hasta -30 si 100% missing
    
    if role == "numeric":
        # Premiar variabilidad
        try:
            std = metadata.get("std", 0)
            mean = metadata.get("mean", 0)
            if mean != 0:
                cv = abs(std / mean)  # Coeficiente de variación
                score += min(cv * 10, 20)  # Hasta +20
        except:
            pass
        
        # Premiar rango
        try:
            q25 = metadata.get("q25", 0)
            q75 = metadata.get("q75", 0)
            iqr = q75 - q25
            if iqr > 0:
                score += min(np.log1p(iqr) * 2, 15)  # Hasta +15
        except:
            pass
    
    elif role in ["categorical_low_card", "categorical_high_card"]:
        # Premiar entropía (diversidad)
        n_unique = metadata.get("n_unique", 1)
        n_total = metadata.get("n_valid", 1)
        if n_total > 0:
            cardinality = n_unique / n_total
            # Óptimo alrededor de 0.1-0.3 (ni muy pocas ni muchas categorías)
            if 0.01 < cardinality < 0.5:
                score += 20
            elif cardinality < 0.01 or cardinality > 0.9:
                score -= 10
        
        # Penalizar concentración extrema
        top_pct = metadata.get("top_pct", 0)
        if top_pct > 90:
            score -= 15
    
    elif role == "datetime":
        # Premiar rango temporal amplio
        range_days = metadata.get("date_range_days", 0)
        if range_days > 365:
            score += 15
        elif range_days > 30:
            score += 10
    
    elif role in ["id_like", "constant", "all_missing"]:
        # Penalizar fuertemente (no son útiles para EDA)
        score = max(score - 40, 5)
    
    # Limitar score entre 0-100
    return max(0, min(100, score))


def get_column_summary(df: pd.DataFrame, column_name: str, role: Optional[str] = None) -> Dict:
    """
    Genera resumen detallado de una columna específica.
    
    Args:
        df: DataFrame
        column_name: Nombre de la columna
        role: Rol (opcional, se infiere si no se provee)
        
    Returns:
        Diccionario con resumen detallado
    """
    if column_name not in df.columns:
        raise ValueError(f"Columna '{column_name}' no encontrada")
    
    series = df[column_name]
    
    if role is None:
        role = infer_variable_role(series, len(df))
    
    # Metadata básica
    metadata = get_column_metadata(series, role)
    
    # Stats específicas por tipo
    if role == "numeric":
        metadata["percentiles"] = _compute_percentiles(series)
        metadata["outliers"] = _detect_outliers(series)
    elif role in ["categorical_low_card", "categorical_high_card"]:
        metadata["value_counts"] = _compute_value_counts(series, top_n=20)
    elif role == "text":
        metadata["sample_values"] = series.dropna().head(10).tolist()
    
    return metadata


def _compute_percentiles(series: pd.Series) -> Dict:
    """Calcula percentiles para numéricas."""
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    result = {}
    for p in percentiles:
        try:
            result[f"p{p}"] = round(float(series.quantile(p / 100)), 4)
        except:
            result[f"p{p}"] = None
    return result


def _detect_outliers(series: pd.Series, method: str = "iqr") -> Dict:
    """Detecta outliers en variable numérica."""
    try:
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = series[(series < lower_bound) | (series > upper_bound)]
        
        return {
            "method": method,
            "lower_bound": round(float(lower_bound), 4),
            "upper_bound": round(float(upper_bound), 4),
            "n_outliers": len(outliers),
            "pct_outliers": round((len(outliers) / len(series)) * 100, 2),
        }
    except:
        return {"n_outliers": 0, "pct_outliers": 0}


def _compute_value_counts(series: pd.Series, top_n: int = 20) -> List[Dict]:
    """Calcula value counts para categóricas."""
    value_counts = series.value_counts().head(top_n)
    total = len(series)
    
    result = []
    for value, count in value_counts.items():
        result.append({
            "value": str(value),
            "count": int(count),
            "percentage": round((count / total) * 100, 2) if total > 0 else 0,
        })
    
    return result
